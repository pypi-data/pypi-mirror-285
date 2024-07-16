import time
import string
import concurrent.futures

import urllib3

from .util import MetalArchives, normalize_keyword_casing, perform_request, MetalArchivesError
from ..interface import (LabelProfile, LabelExternalLinks,
                         LabelPage, LabelPages, LabelContainer,
                         LabelRosterPages, LabelRosterPage, 
                         LabelReleasePages, LabelReleasePage)


class LabelError(MetalArchivesError):
    ...


class Label:

    @classmethod
    def get_full_profile(cls, label_url: str, user_agent: str | None = None, wait=3.):
        profile = cls.get_profile(label_url, user_agent=user_agent)
        metallum_id = profile.metallum_id

        time.sleep(wait)
        external_links = cls.get_profile_links(metallum_id, user_agent=user_agent)
        
        time.sleep(wait)
        roster_current = cls.get_label_roster_current(metallum_id, user_agent=user_agent).data
        
        time.sleep(wait)
        roster_past = cls.get_label_roster_past(metallum_id, user_agent=user_agent).data
        
        time.sleep(wait)
        releases = cls.get_label_releases(metallum_id, user_agent=user_agent).data

        return LabelContainer(profile, roster_current, roster_past, releases, external_links)

    @staticmethod
    def get_profile(label_url: str, user_agent: str | None = None) -> LabelProfile:
        response = perform_request(MetalArchives.get_page, LabelError, label_url, user_agent=user_agent)
        return LabelProfile(label_url, response.data)
    
    @staticmethod
    def get_profile_links(metallum_id: int, user_agent: str | None = None) -> LabelExternalLinks:
        links_url = MetalArchives.label_links_query(metallum_id)
        response = perform_request(MetalArchives.get_page, LabelError, links_url, user_agent=user_agent)
        return LabelExternalLinks(metallum_id, response.data)

    @staticmethod
    def get_label_roster_current(metallum_id: int, user_agent: str | None = None,
                                 echo=0, page_size=500, wait=3., timeout_cxn=3., 
                                 timeout_read=9.) -> LabelRosterPage:

        data = LabelRosterPages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=timeout_cxn, read=timeout_read)
    
        while True:
            endpoint = MetalArchives.roster_current_query(metallum_id, echo, record_cursor, page_size)
            response = perform_request(MetalArchives.get_page, LabelError, endpoint,
                                       timeout=timeout, user_agent=user_agent)
            
            kwargs = normalize_keyword_casing(response.json())
            metadata = dict(metallum_id=metallum_id)
            label_roster_page = LabelRosterPage(**kwargs, metadata=metadata)

            data.append(label_roster_page)

            record_cursor += label_roster_page.count
            echo += 1

            if label_roster_page.total_records > record_cursor:
                time.sleep(wait)
                continue

            break

        return data.combine()

    @staticmethod
    def get_label_roster_past(metallum_id: int, user_agent: str | None = None,
                              echo=0, page_size=500, wait=3., timeout_cxn=3., 
                              timeout_read=9.) -> LabelRosterPage:

        data = LabelRosterPages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=timeout_cxn, read=timeout_read)
    
        while True:
            endpoint = MetalArchives.roster_past_query(metallum_id, echo, record_cursor, page_size)
            response = perform_request(MetalArchives.get_page, LabelError, endpoint,
                                       timeout=timeout, user_agent=user_agent)
            
            kwargs = normalize_keyword_casing(response.json())
            metadata = dict(metallum_id=metallum_id)
            label_roster_page = LabelRosterPage(**kwargs, metadata=metadata)

            data.append(label_roster_page)

            record_cursor += label_roster_page.count
            echo += 1

            if label_roster_page.total_records > record_cursor:
                time.sleep(wait)
                continue

            break

        return data.combine()

    @staticmethod
    def get_label_releases(metallum_id: int, user_agent: str | None = None,
                           echo=0, page_size=500, wait=3., timeout_cxn=3., 
                           timeout_read=9.) -> LabelReleasePage:
        data = LabelReleasePages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=timeout_cxn, read=timeout_read)

        while True:
            endpoint = MetalArchives.label_releases_query(metallum_id, echo, record_cursor, page_size)
            response = perform_request(MetalArchives.get_page, LabelError, endpoint,
                                       timeout=timeout, user_agent=user_agent)
            
            kwargs = normalize_keyword_casing(response.json())
            metadata = dict(metallum_id=metallum_id)
            label_release_page = LabelReleasePage(**kwargs, metadata=metadata)

            data.append(label_release_page)

            record_cursor += label_release_page.count
            echo += 1

            if label_release_page.total_records > record_cursor:
                time.sleep(wait)
                continue

            break

        return data.combine()

    @classmethod
    def get_profiles(cls, profile_urls: list[str], segment_size=8, wait=3.) -> list[LabelProfile]:

        profile_urls_len = len(profile_urls)
        profiles = list()
        
        if profile_urls_len == 0:
            return profiles

        with concurrent.futures.ThreadPoolExecutor() as executor:
            
            processed_urls = set()

            # don't throw them all in at once
            for segment_start in range(0, profile_urls_len + segment_size, segment_size):
                segment_end = min(segment_start + segment_size, profile_urls_len)

                label_futures = list()
                for url in profile_urls[segment_start:segment_end]:
                    if url not in processed_urls:
                        future = executor.submit(cls.get_profile, url)
                        label_futures.append(future)
                        processed_urls.add(url)
                        time.sleep(wait)

                # examine the remains
                for future in concurrent.futures.as_completed(label_futures):
                    profile = future.result()
                    profiles.append(profile)

        return profiles
    
    @classmethod
    def get_external_links(cls, metallum_ids: list[int], segment_size=8, wait=3.) -> list[LabelExternalLinks]:

        links = list()
        metallum_ids_count = len(metallum_ids)

        if metallum_ids_count == 0:
            return links

        with concurrent.futures.ThreadPoolExecutor() as executor:
            
            processed_urls = set()

            # don't throw them all in at once
            for segment_start in range(0, metallum_ids_count + segment_size, segment_size):
                segment_end = min(segment_start + segment_size, metallum_ids_count)

                links_futures = list()
                for url in metallum_ids[segment_start:segment_end]:
                    if url not in processed_urls:
                        future = executor.submit(cls.get_profile_links, url)
                        links_futures.append(future)
                        processed_urls.add(url)
                        time.sleep(wait)

                # examine the remains
                for future in concurrent.futures.as_completed(links_futures):
                    profile = future.result()
                    links.append(profile)
        
        return links

    @classmethod
    def get_labels_by_letter(cls, letter: str, echo=0, page_size=500, wait=3.,
                             timeout_cxn=3., timeout_read=9.) -> LabelPage:
        data = LabelPages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=timeout_cxn, read=timeout_read)

        while True:
            endpoint = MetalArchives.label_by_letter(letter, echo, record_cursor, page_size)

            response = perform_request(MetalArchives.get_page, LabelError, endpoint, timeout=timeout)
            kwargs = normalize_keyword_casing(response.json())
            label_page = LabelPage(**kwargs)

            data.append(label_page)

            record_cursor += label_page.count
            echo += 1

            if label_page.total_records > record_cursor:
                time.sleep(wait)
                continue
            
            break

        return data.combine()

    @classmethod
    def get_labels_by_letters(cls, *letters: str, echo=0, page_size=500, wait=3.) -> LabelPage:
        data = LabelPages()

        if len(letters) == 0:
            letters = tuple([n for n in string.ascii_lowercase])

        with concurrent.futures.ThreadPoolExecutor() as executor:
            label_futures = [executor.submit(cls.get_labels_by_letter, letter, echo=echo, page_size=page_size, wait=wait)
                             for letter in letters]
            
            for future in concurrent.futures.as_completed(label_futures):
                data.append(future.result())

        return data.combine()

    @classmethod
    def get_full_profiles(cls, profile_urls: list[str], segment_size=8, wait=3.) -> list[LabelContainer]:

        profile_urls_len = len(profile_urls)
        profiles = list()
        
        if profile_urls_len == 0:
            return profiles

        with concurrent.futures.ThreadPoolExecutor() as executor:
            
            processed_urls = set()

            # don't throw them all in at once
            for segment_start in range(0, profile_urls_len + segment_size, segment_size):
                segment_end = min(segment_start + segment_size, profile_urls_len)

                label_futures = list()
                for url in profile_urls[segment_start:segment_end]:
                    if url not in processed_urls:
                        future = executor.submit(cls.get_full_profile, url)
                        label_futures.append(future)
                        processed_urls.add(url)
                        time.sleep(wait)

                # examine the remains
                for future in concurrent.futures.as_completed(label_futures):
                    profile = future.result()
                    profiles.append(profile)

        return profiles
    