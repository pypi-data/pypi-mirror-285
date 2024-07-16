
import os
import sys
import json
import unittest
import importlib.util
from types import ModuleType
from enum import Enum

from configparser import ConfigParser


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


class TestBands(unittest.TestCase):
    metalarchivist, interface, export, config = load_module()

    def test_band_hash(self):
        band_hash = self.interface.create_key(1, 'Amorphis')
        self.assertEqual(band_hash, '6bdefdd6445b150526b32308')

    def test_band_profile(self):
        self.assertIn('Band', dir(self.export))

        band = self.export.Band.get_profile('https://www.metal-archives.com/bands/Furia/23765')
        self.assertEqual(band.name, 'Furia')
        self.assertEqual(band.metallum_id, 23765)

        self.assertIsNotNone(band.themes)
        self.assertIsInstance(band.themes, self.interface.Themes)
        self.assertIsInstance(band.genres, self.interface.Subgenres)

    def test_band_profiles(self):
        self.assertIn('Band', dir(self.export))

        bands = self.export.Band.get_profiles(['https://www.metal-archives.com/bands/Furia/23765',
                                               'https://www.metal-archives.com/bands/Cult_of_Fire/3540334368',
                                               'https://www.metal-archives.com/bands/Urfaust/19596',
                                               'https://www.metal-archives.com/bands/A_Forest_of_Stars/115504',
                                               'https://www.metal-archives.com/bands/Burzum/88',
                                               'https://www.metal-archives.com/bands/Mayhem/67',
                                               'https://www.metal-archives.com/bands/Satanic_Warmaster/989'])

        self.assertEqual(len(bands), 7)

    def test_band_links(self):
        band_links = self.export.Band.get_profile_links(19596)

        link_names = [l.name for l in band_links.links]

        self.assertIn('Bandcamp', link_names)
        self.assertIn('Deezer', link_names)
        self.assertIn('Instagram', link_names)
        self.assertIn('Spotify', link_names)
        self.assertIn('Tidal', link_names)
        self.assertIn('Amazon', link_names)
        self.assertIn('Apple Music', link_names)
        self.assertIn('BigCartel', link_names)
        self.assertIn(b'V\xc3\x83\xc2\xa1n Records'.decode(), link_names)

    def test_band_dates(self):
        
        band = self.export.Band.get_profile('https://www.metal-archives.com/bands/Moonspell/61')
        self.assertIsNotNone(band)
        self.assertEqual(band.description.years_active, '1989-1992 (as Morbid God), 1992-present')

    def test_user_agents(self):
        user_agents = self.export.UserAgent.load()

        for user_agent in user_agents:
            self.assertIsInstance(user_agent, str)
            _ = self.export.Band.get_profile('https://www.metal-archives.com/bands/Moonspell/61', user_agent)


if __name__ == '__main__':
    run_test_cases()
