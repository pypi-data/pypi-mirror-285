import time
import concurrent.futures

import urllib3

from .util import (MetalArchives, MetalArchivesError, MetalArchivesInternalError, 
                   normalize_keyword_casing, perform_request, MAX_ATTEMPTS)
from ..interface import Genre, GenrePage, GenrePages


class GenreError(MetalArchivesError):
    ...


class GenreBands:

    @classmethod
    def get_genre_size(cls, genre: Genre, timeout_cxn=3., timeout_read=9.) -> int:
        timeout = urllib3.Timeout(connect=timeout_cxn, read=timeout_read)
        endpoint = MetalArchives.genre(genre.value, display_length=1)
        response = perform_request(MetalArchives.get_page, GenreError, endpoint, timeout=timeout)
        kwargs = normalize_keyword_casing(response.json())
        genre_page = GenrePage(metadata=dict(genre=genre.value), **kwargs)
        return genre_page.total_records

    @staticmethod
    def get_genre(genre: Genre, echo=0, page_size=500, wait=3., timeout_cxn=3., timeout_read=9.) -> GenrePage:
        attempt = 1
        data = GenrePages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=timeout_cxn, read=timeout_read)

        genre_page_metadata = dict(genre=genre.value)

        while True:
            endpoint = MetalArchives.genre(genre.value, echo, record_cursor, page_size)

            response = perform_request(MetalArchives.get_page, GenreError, endpoint, timeout=timeout)
            kwargs = normalize_keyword_casing(response.json())

            if 'error' in kwargs:
                if attempt == MAX_ATTEMPTS:
                    raise MetalArchivesInternalError(**kwargs)
                else:
                    time.sleep(30)
                    attempt += 1
                    continue

            genre_bands = GenrePage(**kwargs, metadata=genre_page_metadata)
            
            data.append(genre_bands)

            record_cursor += genre_bands.count
            echo += 1
            
            if genre_bands.total_records == record_cursor:
                break
            
            time.sleep(wait)

        return data.combine()
    
    @classmethod
    def get_genres(cls, *genres: Genre, echo=0, page_size=500, wait=3.) -> GenrePage:
        data = GenrePages()

        if len(genres) == 0:
            genres = tuple([g for g in Genre])

        with concurrent.futures.ThreadPoolExecutor() as executor:
            genre_futures = [executor.submit(cls.get_genre, genre, echo=echo, page_size=page_size, wait=wait) 
                             for genre in genres]
        
            for future in concurrent.futures.as_completed(genre_futures):
                data.append(future.result())

        return data.combine()
