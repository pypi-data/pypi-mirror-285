
import sys
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


class TestLabel(unittest.TestCase):
    metalarchivist, interface, export, config = load_module()

    def test_label_container(self):
        # label = self.export.Label.get_full_profile('https://www.metal-archives.com/labels/A_Private_Collection/51974')
        # self.assertIsNotNone(label.profile)
        # self.assertIsNotNone(label.roster)
        # self.assertIsNotNone(label.releases)
        # self.assertIsNotNone(label.links)

        # label = self.export.Label.get_full_profile('https://www.metal-archives.com/labels/Primetime_Studios/57738')
        # self.assertIsNotNone(label.profile)
        # self.assertIsNotNone(label.roster)
        # self.assertIsNotNone(label.releases)
        # self.assertIsNotNone(label.links)

        label = self.export.Label.get_full_profile('https://www.metal-archives.com/labels/Season_of_Mist/24')
        self.assertIsNotNone(label.profile)
        self.assertIsNotNone(label.roster)
        self.assertIsNotNone(label.releases)
        self.assertIsNotNone(label.links)

        label = self.export.Label.get_full_profile('https://www.metal-archives.com/labels/Pure_Steel_Records/234')
        self.assertIsNotNone(label.profile)
        self.assertIsNotNone(label.roster)
        self.assertIsNotNone(label.releases)
        self.assertIsNotNone(label.links)

    def test_label(self):
        label_profile = self.export.Label.get_profile('https://www.metal-archives.com/labels/PC_Records/17802')
        self.assertEqual(label_profile.metallum_id, 17802)
        self.assertEqual(label_profile.name, 'PC Records')
        self.assertIsNotNone(label_profile.description)
        
        description = label_profile.description
        self.assertEqual(description.address, 'Steve Geburtig, Markersdorfer Straße 40, 09123 Chemnitz')
        self.assertEqual(description.country, 'Germany')
        self.assertEqual(description.phone_number, '+49 371 26 22 800')
        self.assertEqual(description.status, 'active')
        self.assertEqual(description.styles_and_specialties, 'Music with far-right ideologies, NS metal, RAC')
        self.assertEqual(description.founding_date, 'Unknown')
        self.assertEqual(description.online_shopping, 'Yes')

        label_profile = self.export.Label.get_profile('https://www.metal-archives.com/labels/The_Orchard/24316')
        description = label_profile.description
        self.assertIsNotNone(description.parent_label)
        self.assertEqual(description.parent_label, 'Sony Music')
        self.assertEqual(description.sublabels, 'Infernal Racket, TVT Records')

        self.assertIsNotNone(label_profile.associated)
        self.assertEqual(label_profile.associated.parent.name, 'Sony Music')
        self.assertEqual(label_profile.associated.children[0].name, 'Infernal Racket')
        self.assertEqual(label_profile.associated.children[1].name, 'TVT Records')


    def test_label_roster_current(self):
        label_roster = self.export.Label.get_label_roster_current(17802)
        self.assertIsNotNone(label_roster)
        self.assertGreater(len(label_roster.data), 0)
        
        label_roster_member = label_roster.data[0]
        self.assertIsNotNone(label_roster_member.band.band_key)
        self.assertIsNotNone(label_roster_member.band.name)
        self.assertIsNotNone(label_roster_member.subgenres)
        self.assertIsNotNone(label_roster_member.country_of_origin)

    def test_label_roster_past(self):
        label_roster = self.export.Label.get_label_roster_past(17802)
        self.assertIsNotNone(label_roster)
        self.assertGreater(len(label_roster.data), 0)
        
        label_roster_member = label_roster.data[0]
        self.assertIsNotNone(label_roster_member.band.band_key)
        self.assertIsNotNone(label_roster_member.band.name)
        self.assertIsNotNone(label_roster_member.subgenres)
        self.assertIsNotNone(label_roster_member.country_of_origin)

    def test_label_releases(self):
        label_releases = self.export.Label.get_label_releases(17802)
        self.assertIsNotNone(label_releases)
        self.assertGreater(len(label_releases.data), 0)
        
        label_release = label_releases.data[0]
        self.assertIsNotNone(label_release.band)
        self.assertIsNotNone(label_release.album)
        self.assertIsNotNone(label_release.year)
        self.assertIsNotNone(label_release.catalog)
        self.assertIsNotNone(label_release.media_format)
        self.assertIsNotNone(label_release.description)

    def test_label_links(self):
        label_links = self.export.Label.get_profile_links(17802)
        self.assertIsNotNone(label_links)
        self.assertGreater(len(label_links.links), 0)

    def test_labels(self):
        label_page = self.export.Label.get_labels_by_letter('k')
        self.assertIsNotNone(label_page)
        self.assertGreater(len(label_page.data), 0)
