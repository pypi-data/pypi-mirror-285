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
    
    if spec is None:
        raise ModuleNotFoundError

    module = importlib.util.module_from_spec(spec)
    sys.modules[submodule_name] = module

    if spec.loader is None:
        raise ModuleNotFoundError

    spec.loader.exec_module(module)

    return module


def load_module():
    config = ConfigParser()
    config.read('metallum.cfg')

    metalarchivist = prepare_submodule(Submodule.MODULE)
    interface = prepare_submodule(Submodule.IFACE)
    export = prepare_submodule(Submodule.EXPORT)

    return metalarchivist, interface, export, config


class TestGenres(unittest.TestCase):
    metalarchivist, interface, export, config = load_module()

    def test_genres_pages(self):
        target_genre = self.interface.Genre.POWER

        genre_length = self.export.Genre.get_genre_size(target_genre)

        genre_bands = self.export.Genre.get_genre(target_genre, page_size=1000)
        self.assertIsNotNone(genre_bands)
        self.assertIsInstance(genre_bands, self.interface.GenrePage)
        self.assertIsInstance(genre_bands.data, list)

        self.assertEqual(genre_length, len(genre_bands.data))

        self.assertIsInstance(genre_bands.data[0], self.interface.BandGenre)
        self.assertEqual(genre_bands.data[0].genre, target_genre.value)

        genre_json = genre_bands.to_json()
        self.assertIsInstance(genre_json, list)

        for record in genre_json:
            self.assertIsInstance(record, dict)
            self.assertIn('band_key', record)

    def test_genres(self):

        genres = self.interface.Subgenres('Black Metal/Black \'n\' Roll')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 2)
        self.assertEqual(genres.clean_genre, 'Black, Black\'n\'Roll')

        genres = self.interface.Subgenres('Drone/Doom Metal (early); Psychedelic/Post-Rock (later)')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Doom, Drone, Post-Rock, Psychedelic')

        genres = self.interface.Subgenres('Progressive Doom/Post-Metal')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 3)
        self.assertEqual(genres.clean_genre, 'Doom, Post-Metal, Progressive')

        genres = self.interface.Subgenres('Black Death Metal/Grindcore')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Black, Death, Grind, Hardcore')

        genres = self.interface.Subgenres('Black Metal')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 1)
        self.assertEqual(genres.clean_genre, 'Black')

        genres = self.interface.Subgenres('Progressive Death/Black Metal')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 3)
        self.assertEqual(genres.clean_genre, 'Black, Death, Progressive')

        genres = self.interface.Subgenres('Epic Black Metal')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 2)
        self.assertEqual(genres.clean_genre, 'Black, Epic')

        genres = self.interface.Subgenres('Various (early); Atmospheric Black Metal, Ambient (later)')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Various, Ambient, Atmospheric, Black')

        genres = self.interface.Subgenres('Symphonic Gothic Metal with Folk influences')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 3)
        self.assertEqual(genres.clean_genre, 'Folk, Gothic, Symphonic')

        genres = self.interface.Subgenres('Dungeon Synth')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 1)
        self.assertEqual(genres.clean_genre, 'Dungeon-Synth')

        genres = self.interface.Subgenres('Symphoniccore, Melodiccore, Grindcore')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Grind, Hardcore, Melodic, Symphonic')
    
        genres = self.interface.Subgenres('Metalcore')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 1)
        self.assertEqual(genres.clean_genre, 'Hardcore')

        genres = self.interface.Subgenres('Prog Rock, Post-Black')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Black, Post-Metal, Progressive, Rock')

        genres = self.interface.Subgenres('Goregrind/Grindcore (early); Melodic Death Metal/Death \'n\' Roll (later)')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 5)
        self.assertEqual(genres.clean_genre, 'Grind, Hardcore, Death\'n\'Roll, Melodic, Death')

        genres = self.interface.Subgenres('Hardcore')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 1)
        self.assertEqual(genres.clean_genre, 'Hardcore')
    
        genres = self.interface.Subgenres('Hard Rock')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 1)
        self.assertEqual(genres.clean_genre, 'Hard-Rock')
            
        genres = self.interface.Subgenres("Death 'n' Roll")
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 2)
        self.assertEqual(genres.clean_genre, "Death, Death'n'Roll")
    
        genres = self.interface.Subgenres('Goregrind/Death Metal, Noisegrind')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Death, Grind, Hardcore, Noise')

        genres = self.interface.Subgenres('Death/Thrash Metal/Grindcore')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Death, Grind, Hardcore, Thrash')

        genres = self.interface.Subgenres('Crossover/Hardcore/Thrash Metal')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 3)
        self.assertEqual(genres.clean_genre, 'Crossover, Hardcore, Thrash')

        genres = self.interface.Subgenres('Post-Black Metal/Post-Hardcore')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 3)
        self.assertEqual(genres.clean_genre, 'Black, Post-Hardcore, Post-Metal')

        genres = self.interface.Subgenres('AOR/Pop Rock (early); Heavy Metal/Hard Rock (later)')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Arena-Rock, Pop-Rock, Hard-Rock, Heavy')

        genres = self.interface.Subgenres('Powerviolence')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 2)
        self.assertEqual(genres.clean_genre, 'Hardcore, Powerviolence')

        genres = self.interface.Subgenres('Gorenoise')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Death, Grind, Hardcore, Noise')

        genres = self.interface.Subgenres('Black/Death Metal (early); Electronic Rock/Pop (mid); Drum and Bass/Electronic (later)')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 6)
        self.assertEqual(genres.clean_genre, 'Black, Death, Electronic-Rock, Pop, Drum-and-Bass, Electronic')

        genres = self.interface.Subgenres('Black/Death Metal (early); Electronic/Pop (mid); Drum and Bass/Electronic (later)')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 6)
        self.assertEqual(genres.clean_genre, 'Black, Death, Electronic, Pop, Drum-and-Bass')

if __name__ == '__main__':
    run_test_cases()
