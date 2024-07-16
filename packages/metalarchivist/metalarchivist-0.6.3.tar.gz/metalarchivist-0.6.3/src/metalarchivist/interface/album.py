 
import re
import warnings
from datetime import datetime
from dataclasses import dataclass, field, InitVar, asdict

import lxml.html
import lxml.etree
from lxml.etree import ElementBase

from .band import BandLink
from .genre import Subgenres
from .api.base import create_key, ERROR_KEY, ERROR_STR, ERROR_DATE


class ParseError(Exception):
    ...


def _parse_release_date(release_date) -> str:
    """ Normalizes textual release dates to a datetime object """

    def _try_parse_release_date(release_date: str, date_format: str):
        try:
            return datetime.strptime(release_date, date_format) \
                           .date().strftime('%Y-%m-%d')
        except ValueError:
            return None

    release_date = re.sub(r',', '', release_date)
    release_date = re.sub(r'(\d)st', r'\g<1>', release_date)
    release_date = re.sub(r'(\d)nd', r'\g<1>', release_date)
    release_date = re.sub(r'(\d)rd', r'\g<1>', release_date)
    release_date = re.sub(r'(\d)th', r'\g<1>', release_date)
    release_date = re.sub(r'\s(\d)\s', r' 0\g<1> ', release_date)

    release_date_parsed = _try_parse_release_date(release_date, '%B %d %Y')
    if not release_date_parsed:
        release_date_parsed = _try_parse_release_date(release_date, '%B %Y')
    if not release_date_parsed:
        release_date_parsed = _try_parse_release_date(release_date, '%Y-%m-%d %H:%M:%S')

    if release_date_parsed is None:
        release_date_parsed = ERROR_DATE

    return release_date_parsed


class AlbumXPath:
    LABEL_LINK = '//div[@id="album_info"]/dl/dt[text()="Label:"]/following-sibling::dd[1]/a'
    NAME = './/h1[contains(@class, "album_name")]/a/text()'
    BAND_LINK = './/h2[contains(@class, "band_name")]/a'
    DESCRIPTION_TITLES = '//div[@id="album_info"]/dl/dt/text()'
    DESCRIPTION_DETAILS = '//div[@id="album_info"]/dl/dd/text()'
    TRACKLIST = '//div[@id="album_tabs_tracklist"]//tr[@class="even" or @class="odd"]'


@dataclass
class AlbumLink:
    """ The data within an HTML anchor tag pointing to an album page """
    html: InitVar[str]
    
    name: str = field(init=False)
    link: str = field(init=False)
    metallum_id: int = field(init=False)
    album_key: str = field(init=False)
    authenticity: str | None = field(init=False, default=None)

    def __post_init__(self, html: str):
        fragments = lxml.html.fragments_fromstring(html)
        html_anchor, *remaining_tags = fragments
        
        if remaining_tags and remaining_tags[0].tag == 'span':
            self.authenticity = remaining_tags[0].text.strip()

        self.link = link = html_anchor.attrib['href']
        self.name = name = html_anchor.text
        self.metallum_id = metallum_id = int(link.split('/').pop())
        try:
            self.album_key = create_key(metallum_id, name)
        except ValueError:
            warnings.warn(f'invalid album link at {self.link}')
            self.album_key = ERROR_KEY


@dataclass
class ReleaseLink:
    album_key: InitVar[str | None] = field(default=None)
    band_link: InitVar[BandLink | None] = field(default=None)
    release_key: str = field(default=ERROR_KEY)
    band_key: str = field(default=ERROR_KEY)

    def __post_init__(self, album_key: str | None, band_link: BandLink | None):
        if album_key and band_link:
            self.release_key = create_key(album_key, band_link.band_key)
            self.band_key = band_link.band_key


@dataclass
class AlbumRelease:
    band: BandLink
    album: AlbumLink

    release_type: str
    genres: Subgenres
    release_date_display: InitVar[str]
    added_date_display: InitVar[str | None] = field(default=None)

    release_date: str = field(init=False)
    added_date: str | None = field(init=False)

    def __post_init__(self, release_date_display, added_date_display):
        self.release_date = _parse_release_date(release_date_display)

        if added_date_display == 'N/A' or added_date_display is None:
            self.added_date = None
        else:
            added_date = re.sub(r'\/(\d)\/', '/0\1/', added_date_display)
            self.added_date = datetime.strptime(added_date, '%Y-%m-%d %H:%M:%S') \
                                      .strftime('%Y-%m-%dT%H:%M:%SZ')


@dataclass
class AlbumTrackLength:
    """ Numerically defines the length of an album track """
    length_text: InitVar[str]
    hours: int = field(init=False, default=0)
    minutes: int = field(init=False, default=0)
    seconds: int = field(init=False)

    def __post_init__(self, length_text: str):
        split_length_text = length_text.split(':')[::-1]

        self.seconds = int(split_length_text[0])

        try:
            self.minutes = int(split_length_text[1])
            self.hours = int(split_length_text[2])
        except IndexError:
            pass


@dataclass
class AlbumTrack:
    """ A unique track on an album """
    tablerow: InitVar[lxml.etree.ElementBase]

    metallum_id: str = field(init=False)
    number: str = field(init=False)
    title: str = field(init=False)
    length: AlbumTrackLength | None = field(init=False)
    track_key: str = field(init=False)

    def __post_init__(self, tablerow: lxml.etree.ElementBase):
        number, title, length, *_ = tablerow.xpath('./td')

        self.metallum_id = metallum_id = number.xpath('./a').pop().attrib['name']
        self.title = title = title.text.strip()

        self.track_key = create_key(metallum_id, title)

        self.number = re.sub(r'\.$', '', number.xpath('./text()').pop())
        self.length = AlbumTrackLength(length.text) if length.text else None


@dataclass
class AlbumTrackLyrics:
    metallum_id: str
    html: InitVar[bytes]

    text: str = field(init=False)

    def __post_init__(self, lyrics_html: bytes):
        wrapped_html = b'<div>' + lyrics_html + b'</div>'
        lyrics_doc = lxml.html.fragment_fromstring(wrapped_html)
        lyrics_text = lyrics_doc.xpath('./text()')
        lyrics_text = list(map(str.strip, lyrics_text))
        self.text = '\n'.join(lyrics_text)


@dataclass
class AlbumDescription:
    """ Additional information concerning an album """
    release_type: str | None
    release_date: str | None
    catalog_id: str | None
    label: str | None
    media_format: str | None
    version_desc: str | None = field(default=None)
    limitation: str | None = field(default=None)
    reviews: str | None = field(default=None)


@dataclass
class AlbumLabelLink:
    """ Rough copy of .label.LabelLink, defined locally to prevent 
        circular imports between .album and .label 
    """

    html: InitVar[str]

    name: str = field(init=False)
    link: str = field(init=False)
    metallum_id: int = field(init=False)
    label_key: str = field(init=False)

    def __post_init__(self, html: str):
        html_anchor = lxml.html.fragment_fromstring(html)
        self.name = html_anchor.text
        self.link = link = html_anchor.attrib['href'].split('#').pop(0)
        self.metallum_id = int(link.split('/').pop())
        self.label_key = create_key(self.metallum_id, self.name)

    @classmethod
    def from_element(cls, element: ElementBase):
        kwargs = dict(method='html', with_tail=False)
        return cls(lxml.etree.tostring(element, **kwargs))


@dataclass
class AlbumProfile:
    """ An album profile page """
    url: str
    html: InitVar[bytes]

    name: str = field(init=False)
    metallum_id: int = field(init=False)
    album_key: str = field(init=False)
    
    releases: list[ReleaseLink] = field(init=False)
    label: AlbumLabelLink | None = field(init=False)
    tracklist: list[AlbumTrack] = field(init=False)
    description: AlbumDescription = field(init=False)

    def __post_init__(self, profile_html):
        profile_document = lxml.html.document_fromstring(profile_html)
        self.metallum_id = metallum_id = int(self.url.split('/')[-1])
        self.label = self._parse_label(profile_document)
        
        album_tracklist = profile_document.xpath(AlbumXPath.TRACKLIST)
        self.tracklist = list(map(AlbumTrack, album_tracklist))

        try:
            self.name = name = profile_document.xpath(AlbumXPath.NAME).pop()
        except IndexError:
            self.name = name = ERROR_STR
            self.album_key = album_key = ERROR_KEY
            self.description = AlbumDescription(ERROR_STR, ERROR_DATE, ERROR_STR, ERROR_STR, 
                                                ERROR_STR, ERROR_STR, ERROR_STR, ERROR_STR)
            
            self.releases = [ReleaseLink()]
        
        else:
            self.album_key = album_key = create_key(metallum_id, name)

            album_desc_titles = profile_document.xpath(AlbumXPath.DESCRIPTION_TITLES)
            album_desc_detail = profile_document.xpath(AlbumXPath.DESCRIPTION_DETAILS)

            self.description = self._parse_description(album_desc_titles, album_desc_detail)

            band_links = profile_document.xpath(AlbumXPath.BAND_LINK)
            releases: list[ReleaseLink] = list()
            for band_link in band_links:
                band_link_str = lxml.etree.tostring(band_link).decode('utf-8').split('\n')[0]
                band_link_str = band_link_str.split(' / ').pop(0).strip()
                releases.append(ReleaseLink(album_key, BandLink(band_link_str)))

            self.releases = releases

    @classmethod
    def _parse_description(cls, description_titles, description_details) -> AlbumDescription:
        description = {str(dt).lower(): str(dd).strip() 
                       for dt, dd in zip(description_titles, description_details)}
        
        # scrub non alpha and whitespace
        description = {re.sub(r'[^\w\s]+', '', dt): None if dd == 'N/A' else dd 
                       for dt, dd in description.items()}
        
        # underscores
        description = {re.sub(r'\s+', '_', dt): dd
                       for dt, dd in description.items()}
        
        # scrub invalid key names
        description = {cls._scrub_key_names(dt): dd
                       for dt, dd in description.items()}

        return AlbumDescription(**description)
    
    @staticmethod
    def _parse_label(profile_document: lxml.etree.ElementBase) -> AlbumLabelLink | None:
        
        try:
            label_anchor = profile_document.xpath(AlbumXPath.LABEL_LINK).pop()
        except IndexError:
            return None
        else:
            return AlbumLabelLink.from_element(label_anchor)

    @staticmethod
    def _scrub_key_names(key: str) -> str:
        if key == 'type':
            return 'release_type'

        if key == 'format':
            return 'media_format'

        return key
    
    @property
    def release_date(self):
        return _parse_release_date(self.description.release_date)
    
    def to_dict(self):
        return asdict(self)
