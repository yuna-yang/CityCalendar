"""Scrapes the City of Leuven's own municipal agenda - no registration or API key needed.

Source: https://www.leuven.be/agenda
Distinct from visitleuven.be (tourism): this is the city government's own listing,
covering municipal/community events (info sessions, workshops, sports, book sales, etc.).
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

BASE_URL = "https://www.leuven.be/agenda"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CityCalendarBot/1.0)"}

_NL_MONTHS = {
    "januari": 1, "februari": 2, "maart": 3, "april": 4, "mei": 5, "juni": 6,
    "juli": 7, "augustus": 8, "september": 9, "oktober": 10, "november": 11, "december": 12,
}
_DATE_RE = re.compile(r"(\d{1,2})\s+([a-zé]+)\s+(\d{4})", re.IGNORECASE)
_CATEGORY_KEYWORDS = {
    Category.FLEA_MARKET: ("markt", "rommelmarkt", "brocante", "kermis"),
    Category.EXHIBITION: ("tentoonstelling", "expo"),
    Category.MUSEUM_FREE_DAY: ("museum",),
}


class LeuvenBeAgendaSource(BaseSource):
    def __init__(self, source_id: str, max_pages: int = 3) -> None:
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
            cards = soup.select("a.node--type-ct-activity")
            if not cards:
                break
            for card in cards:
                event = self._parse_card(card)
                if event is not None:
                    events.append(event)
        return events

    def _parse_card(self, card) -> Event | None:
        title_el = card.select_one("h3")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)

        date_el = card.select_one(".field--name-field-ct-intertitle")
        start = self._parse_start(date_el.get_text(" ", strip=True)) if date_el else None
        if start is None:
            logger.warning("%s: could not parse a date for %r, skipping", self.source_id, title)
            return None

        description_el = card.select_one(".field--name-field-ct-description p")
        description = description_el.get_text(strip=True) if description_el else ""

        url = card.get("href", "")
        if url.startswith("/"):
            url = f"https://www.leuven.be{url}"
        description = "\n\n".join(part for part in (description, f"More info: {url}" if url else "") if part)

        return Event(
            title=title,
            start=start,
            city=City.LEUVEN,
            category=self._guess_category(title, description),
            description=description,
            url=url,
            source=self.source_id,
        )

    def _parse_start(self, text: str) -> datetime | None:
        match = _DATE_RE.search(text)
        if not match:
            return None
        day, month_name, year = match.groups()
        month = _NL_MONTHS.get(month_name.lower())
        if not month:
            return None
        try:
            return datetime(int(year), month, int(day))
        except ValueError:
            return None

    def _guess_category(self, title: str, description: str) -> Category:
        haystack = f"{title} {description}".lower()
        for category, keywords in _CATEGORY_KEYWORDS.items():
            if any(keyword in haystack for keyword in keywords):
                return category
        return Category.EVENT
