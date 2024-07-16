
# standard
import time
import calendar
import concurrent.futures
from datetime import datetime

# third-party
import urllib3

# local
from .util import MetalArchives, get_json, normalize_keyword_casing, perform_request, MetalArchivesError
from ..interface import AlbumProfile, AlbumTrackLyrics, ReleasePage, ReleasePages


class AlbumError(MetalArchivesError):
    ...


class AlbumLyricsError(MetalArchivesError):
    ...


class Album:

    @staticmethod
    def get_profile(profile_url: str, user_agent: str | None = None) -> AlbumProfile:
        response = perform_request(MetalArchives.get_page, AlbumError, profile_url, user_agent=user_agent)
        return AlbumProfile(profile_url, response.data)
    
    @classmethod
    def get_track_lyrics(cls, metallum_id: str) -> AlbumTrackLyrics:
        track_lyrics_url = MetalArchives.track_lyrics_query(metallum_id)
        response = perform_request(MetalArchives.get_page, AlbumLyricsError, track_lyrics_url)
        return AlbumTrackLyrics(metallum_id, response.data)

    @classmethod
    def get_profiles(cls, profile_urls: list[str], segment_size=16, wait=3.) -> list[AlbumProfile]:
        profiles = list()
        profile_urls_len = len(profile_urls)

        with concurrent.futures.ThreadPoolExecutor() as executor:

            # don't throw them all in at once
            for segment_start in range(0, profile_urls_len + segment_size, segment_size):
                segment_end = min(segment_start + segment_size, profile_urls_len)

                # feed the beast
                album_futures = (executor.submit(cls.get_profile, url) 
                                 for url in profile_urls[segment_start:segment_end] 
                                 if not time.sleep(wait))

                # examine the remains
                for future in concurrent.futures.as_completed(album_futures):
                    profile = future.result()
                    profiles.append(profile)
        
        return profiles

    @staticmethod
    def get_upcoming(echo=0, page_size=100, wait=3., retries=3, timeout_cxn=3., timeout_read=9.) -> ReleasePage:
        data = ReleasePages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=timeout_cxn, read=timeout_read)

        while True:
            endpoint = MetalArchives.upcoming_releases(echo, record_cursor, page_size)

            response = get_json(endpoint, timeout, retries)
            releases = ReleasePage(**normalize_keyword_casing(response))

            data.append(releases)

            record_cursor += page_size
            echo += 1

            if releases.total_records - 1 > record_cursor:
                time.sleep(wait)
                continue
            break

        return data.combine()

    @staticmethod
    def get_range(range_start: datetime, range_stop: datetime | None = None,
                  echo=0, page_size=100, wait=3., retries=3,
                  timeout_cxn=3., timeout_read=9.) -> ReleasePage:

        data = ReleasePages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=timeout_cxn, read=timeout_read)

        range_stop_str = range_stop.strftime('%Y-%m-%d') if range_stop is not None else '0000-00-00'

        while True:
            endpoint = MetalArchives.upcoming_releases(echo, record_cursor, page_size,
                                                       range_start.strftime('%Y-%m-%d'),
                                                       range_stop_str)
            
            response = get_json(endpoint, timeout, retries)
            releases = ReleasePage(**normalize_keyword_casing(response))

            data.append(releases)

            record_cursor += page_size
            echo += 1

            if releases.total_records - 1 > record_cursor:
                time.sleep(wait)
                continue
            break

        return data.combine()
    
    @classmethod
    def get_month(cls, year, month) -> ReleasePage:
        first_day, last_day = calendar.monthrange(year, month)
        month_albums = cls.get_range(datetime(year, month, first_day), 
                                     datetime(year, month, last_day))
        
        return month_albums

    @classmethod
    def get_all(cls):
        year_range = range(1970, datetime.now().year + 2)
        months = [(year, month) 
                  for month in range(1, 13) 
                  for year in year_range]
        
        release_pages = ReleasePages(cls.get_month(*n) for n in months)

        return release_pages.combine()

