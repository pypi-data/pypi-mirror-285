import re

from dataclasses import field, InitVar, dataclass

import lxml.html

from .base import Page, PageCollection, PageDataType

from ..band import BandLink, BandGenre
from ..album import AlbumLink, AlbumRelease
from ..genre import Subgenres
from ..label import LabelLink, LabelRosterMember, Label, LabelRelease




@dataclass
class Labels(list, PageDataType):
    label_page_record: InitVar[list[str]]

    def __post_init__(self, label_page_record: list[str]):
        (_, label_link_text, specialisation, status_text, 
         country, website_link_text, has_shop_text) = label_page_record
        
        label_link = LabelLink(label_link_text)
        status = lxml.html.fragment_fromstring(status_text).text

        has_shop = len(has_shop_text.replace('&nbsp;', '').strip()) > 0

        specialisation = specialisation.replace('&nbsp;', '').strip()
        if len(specialisation) == 0:
            specialisation = None

        country = country.replace('&nbsp;', '').strip()
        if len(country) == 0:
            country = None

        if len(website_link_text.replace('&nbsp;', '')) > 0:
            website = lxml.html.fragment_fromstring(website_link_text).attrib['href']
        else:
            website = None

        self.append(Label(label_link, status, has_shop, specialisation, country, website))
        


@dataclass
class BandGenres(list, PageDataType):
    genre_page_record: InitVar[list[str]]
    genre: str = field(kw_only=True)

    def __post_init__(self, genre_page_record: list[str]):
        profile_anchor_text, _, subgenre, _ = genre_page_record

        profile_anchor = lxml.html.fragment_fromstring(profile_anchor_text)
        profile_link = profile_anchor.attrib['href']
        band = ''.join(profile_anchor.xpath('./text()'))

        subgenre = Subgenres(subgenre)
        self.append(BandGenre(profile_link, band, subgenre, self.genre))


@dataclass
class LabelReleases(list, PageDataType):
    release_page_record: InitVar[list[str]]
    metallum_id: int = field(kw_only=True)

    def __post_init__(self, release_page_record: list[str]):
        band_link_text, album_link_text, *args = release_page_record
        
        album_link = AlbumLink(album_link_text)

        if re.search(r'>\s?\/\s?<', band_link_text):
            band_links = re.split(r'(?<=>)(\s?\/\s?)(?=<)', band_link_text)

            for link in band_links:
                if link.strip() == '/':
                    continue

                band_link = BandLink(link)
                album_release = LabelRelease(band_link, album_link, *args)
                self.append(album_release)

        else:
            band_link = BandLink(band_link_text)
            album_release = LabelRelease(band_link, album_link, *args)
            self.append(album_release)



@dataclass
class AlbumReleases(list, PageDataType):
    release_page_record: InitVar[list[str]]

    def __post_init__(self, release_page_record: list[str]):
        band_link_text, album_link_text, release_type, genres, *dates = release_page_record
        album_link = AlbumLink(album_link_text)

        if re.search(r'>\s?\/\s?<', band_link_text):
            band_links = band_link_text.split(' / ')
            genre_list = genres.split(' | ')

            for link, genre in zip(band_links, genre_list):
                band_link = BandLink(link)
                subgenres = Subgenres(genre)
                album_release = AlbumRelease(band_link, album_link, release_type, subgenres, *dates)
                self.append(album_release)

        else:
            band_link = BandLink(band_link_text)
            subgenres = Subgenres(genres)
            album_release = AlbumRelease(band_link, album_link, release_type, subgenres, *dates)
            self.append(album_release)


@dataclass
class LabelRosterMembers(list, PageDataType):
    roster_page_record: InitVar[list[str]]
    metallum_id: int = field(kw_only=True)

    def __post_init__(self, roster_page_record: list[str]):
        profile_anchor_text, subgenre_text, country_of_origin, *_ = roster_page_record

        band_link = BandLink(profile_anchor_text)
        subgenres = Subgenres(subgenre_text)
        self.append(LabelRosterMember(self.metallum_id, band_link, subgenres, country_of_origin))


class LabelReleasePage(Page, data_type=LabelReleases):
    ...


class LabelReleasePages(PageCollection, data_type=LabelReleasePage):
    ...


class LabelRosterPage(Page, data_type=LabelRosterMembers):
    ...


class LabelRosterPages(PageCollection, data_type=LabelRosterPage):
    ...


class LabelPage(Page, data_type=Labels):
    ...


class LabelPages(PageCollection, data_type=LabelPage):
    ...


class GenrePage(Page, data_type=BandGenres):
    ...


class GenrePages(PageCollection, data_type=GenrePage):
    ...


class ReleasePage(Page, data_type=AlbumReleases):    
    ...


class ReleasePages(PageCollection, data_type=ReleasePage):
    ...
