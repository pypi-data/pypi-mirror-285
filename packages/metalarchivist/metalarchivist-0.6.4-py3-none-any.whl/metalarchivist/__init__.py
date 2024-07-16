from typing import Callable
from datetime import datetime
from dataclasses import asdict

from .export import Band, Album, Label


def series(from_list: list[dict], column: str):
    return [[v for k, v in d.items() if k == column][0] for d in from_list]


def select(from_list: list[dict], column: str):
    return list(map(lambda n: {column: n[column]}, from_list))


def expand(from_list: list, column: str):
    column_sample = next(filter(lambda n: n[column], from_list))[column]
    null_dict = {str(k): None for k in column_sample.keys()}
    return list(map(lambda n: dict(**n[column]) if n[column] else null_dict, from_list))


def where(from_list: list, column: str, key: Callable[..., bool]):
    return [n for n in from_list if key(n[column])]


def drop(from_list: list[dict], *columns: str):
    return [{k: v for k, v in d.items() if k not in columns} for d in from_list]


def rename(from_list: list, column_map: dict):
    return [{column_map.get(k, k): v for k, v in d.items()} for d in from_list]


def join(first_list, second_list, on_column: str):
    return [dict(**left, **{k: v for k, v in right.items() if k not in left}) 
            for left in first_list for right in second_list 
            if left[on_column] == right[on_column]]


def get_releases(range_start: datetime | None = None, range_stop: datetime | None = None, 
               wait=3., retries=3, timeout=3.):
    if range_start:
        release_page = Album.get_range(range_start, range_stop, wait=wait, retries=retries, 
                                       timeout_cxn=timeout, timeout_read=timeout * 3)
    else:
        release_page = Album.get_upcoming(wait=wait, retries=retries, timeout_cxn=timeout, 
                                          timeout_read=timeout * 3)

    album = list(map(asdict, release_page.data))

    band_key = select(expand(select(album, 'band'), 'band'), 'band_key')
    
    # hoist out the link attributes from each band
    band_url = select(expand(select(album, 'band'), 'band'), 'link')
    band_url = series(band_url, 'link')
    band_url = [str(p) for p in band_url]

    band = Band.get_profiles(band_url, wait=wait)
    band = list(map(lambda n: n.to_dict(), band))

    album = expand(select(album, 'album'), 'album')
    album = rename(album, dict(link='url'))

    album_key = select(album, 'album_key')

    album_url = series(album, 'url')
    album_url = [str(u) for u in album_url]
    album_profile = Album.get_profiles(album_url)
    album_profile = list(map(lambda n: n.to_dict(), album_profile))
    album = join(album, album_profile, 'album_key')

    label_link = select(album, 'label')
    label_link = expand(label_link, 'label')
    label_key = select(label_link, 'label_key')

    label_url = where(label_link, 'link', lambda n: n is not None)
    label_url = series(label_url, 'link')
    label_url = [str(u) for u in label_url]
    
    label = Label.get_full_profiles(label_url)
    label = list(map(lambda n: n.to_dict(), label))
    
    album = [dict(album_key=a['album_key'], album=a) for a in album]
    band = [dict(band_key=b['band_key'], band=b) for b in band]

    def hoist_label_key(lbl: dict) -> str:
        return lbl['profile']['label_key']

    label = [dict(label_key=hoist_label_key(lbl) , label=lbl) for lbl in label]

    release = [dict(**lbl, **b, **a) for lbl, b, a in 
               zip(label_key, band_key, album_key)]
    release = join(list(release), album, 'album_key')
    release = join(release, band, 'band_key')
    release = join(release, label, 'label_key')
    release = drop(release, 'album_key', 'band_key', 'label_key')

    return release
