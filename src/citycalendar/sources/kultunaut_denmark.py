"""Scrapes Kultunaut, Denmark's main public cultural events database - no registration needed.

Source: https://www.kultunaut.dk/perl/arrlist/type-nynaut
Region scope: the "Storkøbenhavn" (Greater Copenhagen) area filter, plus optionally a
small, capped number of top-rated highlights from another Danish area (e.g. Odense).
Note: Kultunaut only covers Denmark, so Malmo (Sweden) isn't included here - that would
need a separate Swedish source.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from citycalendar.models import Category, City, Event
from citycalendar.sources.base import BaseSource

logger = logging.getLogger(__name__)

LIST_URL = "https://www.kultunaut.dk/perl/arrlist/type-nynaut"
MORE_URL = "https://www.kultunaut.dk/perl/arrlist2/type-nynaut"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CityCalendarBot/1.0)"}

_DA_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "maj": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12,
}
_DATE_RE = re.compile(
    r"(\d{1,2})\.\s*([a-zæøå]{3})[a-zæøå]*\.?\s*(\d{4})"
    r"(?:.*?kl\.?\s*(\d{1,2})[:.](\d{2}))?",
    re.IGNORECASE,
)
_CATEGORY_KEYWORDS = {
    Category.FLEA_MARKET: ("loppemarked", "marked", "genbrug", "torvedag"),
    Category.EXHIBITION: ("udstilling", "kunst", "galleri", "fernisering", "skulptur"),
    Category.MUSEUM_FREE_DAY: ("museum",),
}


class KultunautSource(BaseSource):
    def __init__(
        self, source_id: str, area: str, max_pages: int = 3, max_events: int | None = None
    ) -> None:
        super().__init__(source_id)
        self.area = area
        self.max_pages = max_pages
        self.max_events = max_events

    def fetch(self) -> list[Event]:
        events: list[Event] = []
        offset = 0
        for page in range(self.max_pages):
            url = LIST_URL if page == 0 else MORE_URL
            params = {"Area": self.area, "Order": "Rating"}
            if page:
                params["startnr"] = offset
            response = requests.get(url, params=params, headers=HEADERS, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            products = soup.select("div.product")
            if not products:
                break
            for product in products:
                event = self._parse_product(product)
                if event is not None:
                    events.append(event)
            offset += len(products)
            if self.max_events and len(events) >= self.max_events:
                break
        return events[: self.max_events] if self.max_events else events

    def _parse_product(self, product) -> Event | None:
        link_el = product.select_one("a.product-content")
        title_el = product.select_one(".arr-genre h3")
        if not link_el or not title_el:
            return None
        title = title_el.get_text(strip=True)

        time_el = product.select_one(".kult-month-day time")
        if not time_el:
            return None
        start = self._parse_start(time_el.get_text(" ", strip=True))
        if start is None:
            logger.warning("%s: could not parse a date for %r, skipping", self.source_id, title)
            return None

        location_el = time_el.select_one("b")
        location = location_el.get_text(strip=True) if location_el else ""

        genre_el = product.select_one(".arr-genre .genre_cat")
        genre = genre_el.get_text(strip=True) if genre_el else ""
        url = link_el.get("href", "")

        return Event(
            title=title,
            start=start,
            city=City.COPENHAGEN,
            category=self._guess_category(genre),
            location=location,
            description="\n\n".join(part for part in (genre, f"More info: {url}" if url else "") if part),
            url=url,
            source=self.source_id,
        )

    def _parse_start(self, text: str) -> datetime | None:
        match = _DATE_RE.search(text.lower())
        if not match:
            return None
        day, month_abbr, year, hour, minute = match.groups()
        month = _DA_MONTHS.get(month_abbr[:3])
        if not month:
            return None
        try:
            return datetime(int(year), month, int(day), int(hour or 0), int(minute or 0))
        except ValueError:
            return None

    def _guess_category(self, genre: str) -> Category:
        haystack = genre.lower()
        for category, keywords in _CATEGORY_KEYWORDS.items():
            if any(keyword in haystack for keyword in keywords):
                return category
        return Category.EVENT
