
from dataclasses import dataclass, field, InitVar

# import lxml.html

from .band import BandProfile


@dataclass
class SearchResults:
    url: str
    html: InitVar[bytes]

    bands: list[BandProfile] = field(init=False)

    def __post_init__(self, search_results_html: bytes):
        # search_results_document = lxml.html.document_fromstring(search_results_html)
        ...