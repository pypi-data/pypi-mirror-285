import itertools
import sys
from dataclasses import dataclass, field
from typing import Iterator, Callable


@dataclass
class Watchlist:
    url: str = field(default=None)
    max_items: int = field(default=None)
    page_min: int = field(default=1)
    page_max: int = field(default=1)
    html: str = field(default=None)

    @property
    def is_multipage(self):
        return "${page}" in self.url

    def __post_init__(self):
        assert self.url or self.html
        if self.url and self.is_multipage:
            assert isinstance(self.page_min, int)
            assert isinstance(self.page_max, int)
            assert self.page_min < self.page_max

    def scrape_by_url(self, scraper: Callable[[str], Iterator[dict]]):
        def generate():
            for page in range(self.page_min, self.page_max + 1):
                substituted_url = self.url.replace("${page}", str(page))
                yield from scraper(substituted_url)

        yield from itertools.islice(generate(), self.max_items or sys.maxsize)
