
import os
import sys
import json
import unittest
import importlib.util
from types import ModuleType
from enum import Enum

from configparser import ConfigParser
from datetime import datetime, date, timedelta


class Submodule(Enum):
    MODULE = 'metalarchivist', './src/metalarchivist/__init__.py'
    EXPORT = 'metalarchivist.export', './src/metalarchivist/export/__init__.py'
    IFACE = 'metalarchivist.interface', './src/metalarchivist/interface/__init__.py'


def run_test_cases():
    unittest.main(argv=[''], verbosity=2)


def prepare_submodule(submodule: Submodule) -> ModuleType:
    submodule_name, submodule_path = submodule.value
    spec = importlib.util.spec_from_file_location(submodule_name, submodule_path)
    if spec is not None and spec.loader is not None:
        module = importlib.util.module_from_spec(spec)
        sys.modules[submodule_name] = module
        spec.loader.exec_module(module)
    else:
        raise ImportError(f'could not load {submodule_name}')

    return module


def load_module():
    config = ConfigParser()
    config.read_dict({'unittests': {'OUTPUTDIR': './'}})
    config.read('metallum.cfg')

    metalarchivist = prepare_submodule(Submodule.MODULE)
    interface = prepare_submodule(Submodule.IFACE)
    export = prepare_submodule(Submodule.EXPORT)

    return metalarchivist, interface, export, config


class TestMetalArchivesDirectory(unittest.TestCase):
    metalarchivist, interface, export, config = load_module()
    
    def test_releases_endpoint(self):        
        self.assertIn('MetalArchives', dir(self.export))

        range_start = datetime(1990, 1, 1).strftime('%Y-%m-%d')
        range_stop = datetime(1990, 12, 31).strftime('%Y-%m-%d')

        self.assertEqual(range_start, '1990-01-01')
        self.assertEqual(range_stop, '1990-12-31')

        expected_endpoint = ('https://www.metal-archives.com/release/ajax-upcoming/json/1'
                             '?sEcho=0&iDisplayStart=0&iDisplayLength=100'
                             '&fromDate=1990-01-01&toDate=1990-12-31')

        endpoint_query = dict(from_date=range_start, to_date=range_stop)
        actual_endpoint = self.export.MetalArchives.upcoming_releases(**endpoint_query)

        self.assertEqual(expected_endpoint, actual_endpoint)


class TestAlbums(unittest.TestCase):
    metalarchivist, interface, export, config = load_module()
    
    def test_date_formatting(self):
        album_profile = self.export.Album.get_profile('https://www.metal-archives.com/albums/Panopticon/The_Rime_of_Memory/1163524')
        self.assertEqual(album_profile.release_date, '2023-11-29')

    def test_release_date_formatting(self):
        release_page = self.export.Album.get_range(datetime(2023, 11, 29), datetime(2023, 11, 29), timeout_read=90.)
        for release in release_page.data:
            self.assertEqual(release.release_date, '2023-11-29')

    def test_releases(self):
        self.assertIn('Album', dir(self.export))

        upcoming_component_attributes = dir(self.export.Album)
        self.assertIn('get_all', upcoming_component_attributes)
        self.assertIn('get_upcoming', upcoming_component_attributes)
        self.assertIn('get_range', upcoming_component_attributes)

    def test_release_fields(self):
        releases = self.export.Album.get_range(date.today(), date.today() + timedelta(days=1))

        releases_attributes = dir(releases)
        self.assertIn('total_records', releases_attributes)
        self.assertIn('total_display_records', releases_attributes)
        self.assertIn('echo', releases_attributes)
        self.assertIn('data', releases_attributes)

        self.assertIsInstance(releases.total_records, int)
        self.assertIsInstance(releases.total_display_records, int)
        self.assertIsInstance(releases.echo, int)
        self.assertIsInstance(releases.data, list)

        self.assertEqual(releases.total_records, releases.total_display_records)
        self.assertGreaterEqual(releases.echo, 0)

    def test_upcoming(self):
        releases = self.export.Album.get_upcoming(timeout_read=90.)
        self.assertIsNotNone(releases)
        self.assertIsInstance(releases, self.interface.ReleasePage)

        data = releases.data
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), releases.total_records)

        album_release = data.pop()
        self.assertIsInstance(album_release, self.interface.AlbumRelease)

    def test_range(self):

        self.assertIn('Album', dir(self.export))

        releases = self.export.Album.get_range(datetime(1990, 1, 1), datetime(1990, 1, 5), timeout_read=90.)
        self.assertIsNotNone(releases)
        self.assertIsInstance(releases, self.interface.ReleasePage)

        total_records = releases.total_records
        total_display_records = releases.total_display_records
        self.assertEqual(total_records, total_display_records)

        self.assertGreaterEqual(releases.echo, 0)

        data = releases.data
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), total_records)

        album_release = data.pop()
        self.assertIsInstance(album_release, self.interface.AlbumRelease)

    # def test_decode_error_handling(self):

    #     self.assertIn('Album', dir(self.export))

    #     releases = self.export.Album.get_range(datetime(2011, 1, 30), datetime(2011, 1, 30))
    #     self.assertIsNotNone(releases)
    #     self.assertIsInstance(releases, self.interface.ReleasePage)
    #     self.assertIsNotNone(releases.error)

    #     total_records = releases.total_records
    #     total_display_records = releases.total_display_records
    #     self.assertEqual(total_records, total_display_records)

    #     self.assertGreaterEqual(releases.echo, 0)

    #     data = releases.data
    #     self.assertIsInstance(data, list)
    #     self.assertGreaterEqual(len(data), total_records)

    #     album_release = data.pop()
    #     self.assertIsInstance(album_release, self.interface.AlbumRelease)

    def test_range_with_null_upper_bound(self):
        interface = prepare_submodule(Submodule.IFACE)
        self.assertIsNotNone(interface)

        export = prepare_submodule(Submodule.EXPORT)
        self.assertIsNotNone(export)

        self.assertIn('Album', dir(export))

        releases = export.Album.get_range(date.today(), timeout_read=90.)
        self.assertIsNotNone(releases)
        self.assertIsInstance(releases, interface.ReleasePage)

        total_records = releases.total_records
        total_display_records = releases.total_display_records
        self.assertEqual(total_records, total_display_records)

        self.assertGreaterEqual(releases.echo, 0)

        data = releases.data
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), total_records)

        album_release = data.pop()
        self.assertIsInstance(album_release, interface.AlbumRelease)

    def test_album_release(self):

        self.assertIn('Album', dir(self.export))

        releases = self.export.Album.get_range(datetime(2023, 8, 11), datetime(2023, 8, 11), timeout_read=90.)

        data = releases.data
        self.assertIsInstance(data, list)

        # can be greater than total records due to split albums
        self.assertGreaterEqual(len(data), releases.total_records)

        album_release = data.pop()
        self.assertIsInstance(album_release, self.interface.AlbumRelease)

        self.assertIn('release_type', dir(album_release))
        self.assertIn('genres', dir(album_release))
        self.assertIn('release_date', dir(album_release))
        self.assertIn('added_date', dir(album_release))
        self.assertIn('band', dir(album_release))
        self.assertIn('album', dir(album_release))

        self.assertIsInstance(album_release.genres, self.interface.Subgenres)
        self.assertIsInstance(album_release.release_date, str)

        if album_release.added_date:
            self.assertIsInstance(album_release.added_date, str)

        self.assertIsInstance(album_release.band, self.interface.BandLink)
        self.assertIsInstance(album_release.album, self.interface.AlbumLink)

    def test_release_report(self):

        releases = self.metalarchivist.get_releases(date.today(), date.today(), wait=.5, timeout=90.)
        self.assertIsInstance(releases, list)

        for release in releases:
            self.assertIn('band', release)
            self.assertIn('album', release)
            self.assertIn('label', release)

            self.assertNotIn('band_key', release)
            self.assertNotIn('album_key', release)
            self.assertNotIn('label_key', release)

            self.assertIn('bands', release['album'])

        output_path = os.path.join(self.config['unittests']['OUTPUTDIR'], 'test-releases-v2.json')
        json.dump(releases, open(output_path, 'w'))


class TestAlbumProfile(unittest.TestCase):
    metalarchivist, interface, export, config = load_module()
    
    def test_album_profile(self):
        self.assertIn('Album', dir(self.export))

        album = self.export.Album.get_profile('https://www.metal-archives.com/albums/Urfaust/Untergang/1161736')
        self.assertIsNotNone(album)

        album_json = album.to_dict()
        album_band_link = album_json['bands']

        self.assertIn('band_key', album_band_link.pop())

    def test_broken_profile(self):
        self.assertIn('Album', dir(self.export))

        album = self.export.Album.get_profile('https://www.metal-archives.com/albums/Saint_Vitus//764118')
        self.assertIsNotNone(album)

        self.assertEqual(album.release_date, '1900-01-01')

        album_json = album.to_dict()
        self.assertEqual(album_json['album_key'], '000000000000000000000000')
        self.assertEqual(album_json['name'], '#!ERROR')

    def test_split_album(self):
        self.assertIn('Album', dir(self.export))

        album = self.export.Album.get_profile('https://www.metal-archives.com/albums/Wastelander_-_Abigail/Nuke_%27n%27_Puke/270220')
        album_json = album.to_dict()

        self.assertEqual(len(album_json['releases']), 2)
        self.assertIn('release_key', album_json['releases'][0])
        self.assertIn('band_key', album_json['releases'][0])

    def test_album_profile_name(self):
        album = self.export.Album.get_profile('https://www.metal-archives.com/albums/Kawir/%CE%9A%CF%85%CE%B4%CE%BF%CE%B9%CE%BC%CE%BF%CF%83/1216552')
        self.assertIsNotNone(album.name)

    def test_album_profile_tracklist(self):
        album = self.export.Album.get_profile('https://www.metal-archives.com/albums/Aamonblut/Black_Candle_Majesty/1239703')
        self.assertIsNotNone(album.tracklist[0].number)
        self.assertEqual(album.tracklist[0].number, '1')

    def test_album_profile_band_link(self):
        album = self.export.Album.get_profile('https://www.metal-archives.com/albums/%CE%A3%CF%84%CE%B1%CE%BC%CE%AC%CF%84%CE%B7%CF%82_%CE%99%CF%89%CE%AC%CE%BD%CE%BD%CE%BF%CF%85/Avalon_%28Hercules_Cover%29/1225997')
        self.assertIsNotNone(album.band.name)
        self.assertIsNotNone(album.band.link)

    def test_track_lyrics(self):
        track_lyrics = self.export.Album.get_track_lyrics('7299894')
        self.assertIsNotNone(track_lyrics.text)


    # def test_album_themes(self):
    #     metalarchivist = prepare_submodule(Submodule.MODULE)
    #     self.assertIsNotNone(metalarchivist)

    #     interface = prepare_submodule(Submodule.IFACE)
    #     self.assertIsNotNone(interface)

    #     export = prepare_submodule(Submodule.EXPORT)
    #     self.assertIsNotNone(export)

    #     albums = metalarchivist.get_albums()


if __name__ == '__main__':
    run_test_cases()
