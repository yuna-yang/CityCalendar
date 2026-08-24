"""Scrapes the City of Brussels' public events agenda - no registration or API key needed.

Source: https://www.brussels.be/agenda
Events are tagged under the "leuven" region feed (Leuven + Brussels + nearby Belgium).
"""
from __future__ import annotations

import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from citycalendar.models import Category, City, Event
from citycalendar.sources.base import BaseSource

logger = logging.getLogger(__name__)

BASE_URL = "https://www.brussels.be/agenda"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CityCalendarBot/1.0)"}

_CATEGORY_KEYWORDS = {
    Category.FLEA_MARKET: ("market", "brocante", "flea"),
    Category.EXHIBITION: ("exhibition",),
    Category.MUSEUM_FREE_DAY: ("museum",),
}


class BrusselsAgendaSource(BaseSource):
    def __init__(self, source_id: str, max_pages: int = 5) -> None:
        super().__init__(source_id)
        self.max_pages = max_pages

    def fetch(self) -> list[Event]:
        events: list[Event] = []
        for page in range(self.max_pages):
            response = requests.get(
                BASE_URL,
                params={"page": page} if page else {},
                headers=HEADERS,
                timeout=20,
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.select("div.agenda.views-row")
            if not rows:
                break
            for row in rows:
                event = self._parse_row(row)
                if event is not None:
                    events.append(event)
        return events

    def _parse_row(self, row) -> Event | None:
        title_el = row.select_one(".title a")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)

        start, end = self._parse_period(row)
        if start is None:
            logger.warning("%s: could not parse a date for %r, skipping", self.source_id, title)
            return None

        location_name = row.select_one(".agenda-location-name")
        location_address = row.select_one(".agenda-location-address")
        location = ", ".join(
            part.get_text(strip=True)
            for part in (location_name, location_address)
            if part and part.get_text(strip=True)
        )

        genre = self._genre_text(row)
        url = title_el.get("href", "")

        return Event(
            title=title,
            start=start,
            end=end,
            city=City.LEUVEN,
            category=self._guess_category(title, genre),
            location=location,
            description=_build_description(genre, url),
            url=url,
            source=self.source_id,
        )

    def _parse_period(self, row) -> tuple[datetime | None, datetime | None]:
        # multi-day/ongoing entries (e.g. long-running exhibitions) list two <time>
        # tags (start, end); without the end, they'd only ever show on their start
        # day - which is often long past for something still running today.
        time_els = row.select(".agenda-period time[datetime]")
        if not time_els:
            return None, None
        start = self._parse_datetime(time_els[0])
        end = self._parse_datetime(time_els[-1]) if len(time_els) > 1 else None
        return start, end

    def _parse_datetime(self, time_el) -> datetime | None:
        value = time_el.get("datetime")
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _genre_text(self, row) -> str:
        cat_el = row.select_one(".agenda-cat")
        return cat_el.get_text(" ", strip=True) if cat_el else ""

    def _guess_category(self, title: str, genre: str) -> Category:
        haystack = " ".join([title, genre]).lower()
        for category, keywords in _CATEGORY_KEYWORDS.items():
            if any(keyword in haystack for keyword in keywords):
                return category
        return Category.EVENT


def _build_description(genre: str, url: str) -> str:
    parts = [part for part in (genre, f"More info: {url}" if url else "") if part]
    return "\n\n".join(parts)
