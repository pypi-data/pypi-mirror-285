
import re

from enum import StrEnum, auto
from dataclasses import dataclass, field, asdict


class ThemePeriod(StrEnum):
    EARLY = auto()
    MID = auto()
    LATER = auto()
    ALL = auto()
    ERROR = auto()

    @classmethod
    def has_value(cls, value) -> bool:
        return value in cls._value2member_map_
    
    @classmethod
    def get(cls, value: str, default):
        try:
            return cls[value]
        except KeyError:
            return default
        

@dataclass(frozen=True)
class Subtheme:
    name: str


ThemePhaseWithoutSubthemesType = tuple[str, ThemePeriod]
ThemePhaseType = tuple[str, list[Subtheme], ThemePeriod]


@dataclass(frozen=True)
class ThemePhase:
    name: str
    subthemes: list[Subtheme] = field(default_factory=list)
    period: ThemePeriod = field(default=ThemePeriod.ALL)


class ThemeRules:
    phase_combos = ['early', 'mid', 'later', 'early/mid', 'early/later', 'mid/later']

    subtheme_pattern = re.compile(r'\(([\w+,\/\. ]+)\)\s?')
    subtheme_delimiter_pattern = re.compile(r'(?:,\s|\s\/\s)')
    phase_pattern = re.compile(fr'^(?P<name>.*?)(\((?P<period>{"(" + "|".join(phase_combos) + ")"})\))?$')

    not_inside_parenthes_str = r'(?!(?:[^(]*\([^)]*\))*[^()]*\))\s*'

    junk = {r'\banti\b(\w)': r'anti-\g<1>',
            r'\)[\/\b\w]': '), ',
            r'\(earlier\)': '(early)',
            r'\(early, later\)': '(early/later)',
            r'\(early\), \b': '(early); ',
            r'\(first album\), \b': '(early); ',
            r'\(later\), \b': '(later); ',
            r'\);$': ')',
            r'\(deb.\)': '',
            r'themes from ': '',
            r' themes': '',
            r'based on ': '',
            r' \(thematic\)': ''}

    substitutions = {r'\bw\.a\.r\.': 'White Aryan Resistance',
                     r'\bnational socialism\b': 'Nazism',
                     r'\bo9a': 'Order of Nine Angles'}
    
    @classmethod
    def not_inside_parenthes_pattern(cls, delimiter: str) -> re.Pattern:
        return re.compile(fr'{delimiter}' + cls.not_inside_parenthes_str)


@dataclass
class Themes:
    full_theme: str
    clean_theme: str = field(init=False)
    phases: list[ThemePhase] = field(init=False)

    def __post_init__(self):
        clean_theme = self.full_theme
        for pattern, substitution in ThemeRules.junk.items():
            clean_theme = re.sub(pattern, substitution, clean_theme, flags=re.IGNORECASE)

        for pattern, substitution in ThemeRules.substitutions.items():
            clean_theme = re.sub(pattern, substitution, clean_theme, flags=re.IGNORECASE)

        del pattern
        del substitution

        phases = clean_theme.split(';')
        phases = self._parse_phases(phases)
        phases = self._explode_phases_on_delimiter(phases, '/')
        phases = self._explode_phases_on_delimiter(phases, ', (?=[A-Z0-9])')
        phases = self._parse_subthemes(phases)
        phases = self._remove_duplicates(phases)
        self.phases = phases = list(map(lambda n: ThemePhase(*n), phases))
        
        sorted_themes = sorted(phases, key=self._phase_sort_key)
        clean_theme_list = list()
        for phase in sorted_themes:
            theme = phase.name
            if len(phase.subthemes) > 0:
                theme = theme + f' ({", ".join(map(lambda n: n.name, phase.subthemes))})'
            try:
                _ = clean_theme_list.index(theme)
            except ValueError:
                clean_theme_list.append(theme)

        self.clean_theme = ', '.join(clean_theme_list)

    @staticmethod
    def _phase_sort_key(phase: ThemePhase):
        return (ThemePeriod._member_names_.index(phase.period.name), phase.name.lower())

    @staticmethod
    def _collapse_recurrent_phases(phases: list[ThemePhase]) -> list[ThemePhase]:
        all_phases = set(map(lambda n: n.period, phases))

        phase_counts: dict[str, set[ThemePeriod]] = dict()
        for phase in phases:
            try:
                phase_counts[phase.name].add(phase.period)
            except KeyError:
                phase_counts[phase.name] = {phase.period}

        consistent_themes = set(theme for theme, phases in phase_counts.items() 
                                if phases == all_phases)
        
        collapsed_phases = list(map(lambda n: ThemePhase(n), consistent_themes))
        collapsed_phases += list(filter(lambda p: p.name not in consistent_themes, phases))

        return collapsed_phases
    
    @staticmethod
    def _remove_duplicates(phases: list[ThemePhaseType]) -> list[ThemePhaseType]:
        unique_phases = list()
        for phase in phases:
            
            phase_exists = False
            for existing_phase in unique_phases:
                theme_match = phase[0] == existing_phase[0]
                subthemes_match = phase[1] == existing_phase[1]
                period_match = phase[2] == existing_phase[2]

                phase_exists = theme_match and subthemes_match and period_match
                if phase_exists:
                    break

            if not phase_exists:
                unique_phases.append(phase)

        return unique_phases

    @staticmethod
    def _explode_phases_on_delimiter(phases: list[tuple[str, ThemePeriod]], delimiter: str) -> list[tuple[str, ThemePeriod]]:
        def explode(phase: tuple[str, ThemePeriod]) -> list[tuple[str, ThemePeriod]]:
            name, period = phase
            not_inside_parenthes = ThemeRules.not_inside_parenthes_pattern(delimiter)
            return [(n.strip(), period) for n in not_inside_parenthes.split(name)]

        return sum(list(map(explode, phases)), [])
    
    @staticmethod
    def _parse_subthemes(phases: list[ThemePhaseWithoutSubthemesType]) -> list[ThemePhaseType]:
        def parse(phase: str, period: ThemePeriod):
            subtheme_pattern = ThemeRules.subtheme_pattern

            subtheme_match = subtheme_pattern.search(phase)
            subthemes = ThemeRules.subtheme_delimiter_pattern.split(subtheme_match.group(1)) if subtheme_match else []

            phase = subtheme_pattern.sub('', phase).rstrip()
            return phase, list(map(Subtheme, subthemes)), period
    
        return list(map(lambda n: parse(*n), phases))
    
    @staticmethod
    def _parse_phases(phases: list[str]) -> list[tuple[str, ThemePeriod]]:
        
        def parse(phase: str):
            phase_match = ThemeRules.phase_pattern.match(phase)
            if phase_match is None:
                raise ValueError

            period_text = phase_match.group('period')
            if period_text is not None:
                period = ThemePeriod.get(period_text.upper(), ThemePeriod.ERROR)
            else:
                period = ThemePeriod.ALL

            phase_name = phase_match.group('name')
            return phase_name, period
        
        return list(map(parse, map(str.lstrip, phases)))

    def to_dict(self) -> dict:
        phases = [dict(name=p.name.lower(), 
                       subthemes=[{k: v.lower() for k, v in asdict(s).items()} for s in p.subthemes], 
                       period=p.period.value) 
                  for p in self.phases]
        
        return dict(theme=self.clean_theme.lower(), theme_phases=phases)
