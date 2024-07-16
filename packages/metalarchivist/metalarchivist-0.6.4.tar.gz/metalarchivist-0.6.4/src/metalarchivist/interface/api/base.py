
import struct

from abc import ABC
from dataclasses import dataclass, field, InitVar, asdict
from typing import ClassVar, Any

from Crypto.Hash import BLAKE2s


ERROR_INT = -1
ERROR_STR = '#!ERROR'
ERROR_KEY = '000000000000000000000000'
ERROR_DATE = '1900-01-01'

UNKNOWN = 'Unknown'

def create_key(source_id: int | str, seed: str) -> str:
    """ create a unique identifier using BLAKE2s

        source_id : int | str 
            any unique identifier for the given object
        seed : str
            any value that varies the source_id from duplicates, 
            e.g. name or another key
    """

    if isinstance(source_id, int):
        metallum_id_bytes = struct.pack('>Q', source_id)
    elif isinstance(source_id, str):
        metallum_id_bytes = source_id.encode('utf-8')
    else:
        raise TypeError('metallum_id must be a string or integer')
    
    try:
        name_bytes = seed.encode('utf-8')
    except AttributeError:
        raise ValueError(f'name is not a str, or is null (name: {seed}, metallum_id: {str(source_id)})')

    hash_obj = BLAKE2s.new(data=name_bytes, digest_bytes=12, key=metallum_id_bytes)
    return hash_obj.hexdigest()


@dataclass
class PageDataType(ABC):
    ...


@dataclass
class Page(ABC):
    data_type: ClassVar[type] = PageDataType

    i_total_records: InitVar[int] = field(kw_only=True)
    i_total_display_records: InitVar[int] = field(kw_only=True)
    s_echo: InitVar[int] = field(kw_only=True)
    aa_data: InitVar[list] = field(kw_only=True)
    
    error: str | None = field(kw_only=True, default=None)

    metadata: dict[str, Any] = field(default_factory=dict, kw_only=True)

    total_records: int = field(init=False) 
    total_display_records: int = field(init=False)
    echo: int = field(init=False)
    count: int = field(init=False)
    _data: list[PageDataType] = field(init=False)
    _error: str = field(init=False)

    def __post_init__(self, i_total_records: int, i_total_display_records: int,
                      s_echo: int, aa_data: list):
        
        self.total_records = i_total_records
        self.total_display_records = i_total_display_records
        self.echo = s_echo
        self._data = sum(list(map(self._process, aa_data)), [])
        self.count = len(self._data)

        for key, value in self.metadata.items():
            setattr(self, key, value)

    def __init_subclass__(cls, /, data_type=PageDataType, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.data_type = data_type

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            class_str = str(self.__class__)
            raise TypeError(f'{class_str} objects can only be summed with other {class_str} objects')
        
        self._data += other._data
        return self

    def _process(self, record: list[str]) -> list[PageDataType]:
        return [self.data_type(record, **self.metadata)]
    
    @property
    def data(self):
        unioned_data = list()
        for page_data in self._data:
            if isinstance(page_data, list):
                unioned_data += page_data
            else:
                raise ValueError(f'data type {type(page_data)} cannot be combined with list')

        return unioned_data
    
    def to_json(self):
        return list(map(asdict, self.data))


class PageCollection(ABC, list):
    data_type = Page

    def combine(self):
        data_type = self.data_type

        first_page, *remaining = self
        if isinstance(first_page, data_type):
            for page in remaining:
                first_page += page
            return first_page
        else:
            raise ValueError(f'data type {data_type} does not match {type(first_page)}')
    
    def __init_subclass__(cls, /, data_type, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.data_type = data_type
