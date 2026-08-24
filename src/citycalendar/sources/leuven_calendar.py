"""Scrapes Visit Leuven's public calendar - no registration or API key needed.

Source: https://www.visitleuven.be/en/calendar
"""
from __future__ import annotations

import logging
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateutil_parser

from citycalendar.models import Category, City, Event
from citycalendar.sources.base import BaseSource

logger = logging.getLogger(__name__)

BASE_URL = "https://www.visitleuven.be/en/calendar"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CityCalendarBot/1.0)"}

_WEEKDAY_PREFIX = re.compile(
    r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+", re.IGNORECASE
)
_CATEGORY_KEYWORDS = {
    Category.FLEA_MARKET: ("market",),
    Category.EXHIBITION: ("exhibition",),
    Category.MUSEUM_FREE_DAY: ("museum",),
}


class VisitLeuvenSource(BaseSource):
    def __init__(self, source_id: str, max_pages: int = 5, activity_type: str | None = None) -> None:
        super().__init__(source_id)
        self.max_pages = max_pages
        # e.g. "166" = the site's own "Shopping and markets" facet - use this to
        # guarantee flea-market coverage instead of relying on general pagination
        self.activity_type = activity_type

    def fetch(self) -> list[Event]:
        events: list[Event] = []
        for page in range(self.max_pages):
            params = {"page": page} if page else {}
            if self.activity_type:
                params["f[0]"] = f"activity_types:{self.activity_type}"
            response = requests.get(
                BASE_URL,
                params=params,
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
        title_el = card.select_one("h3 span")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)

        start = self._parse_start(card)
        if start is None:
            logger.warning("%s: could not parse a date for %r, skipping", self.source_id, title)
            return None

        location_el = card.select_one(".field--name-field-ct-activity-location .field--item")
        location = location_el.get_text(strip=True) if location_el else ""

        url = card.get("href", "")
        if url.startswith("/"):
            url = f"https://www.visitleuven.be{url}"

        return Event(
            title=title,
            start=start,
            city=City.LEUVEN,
            category=self._guess_category(title),
            location=location,
            description=f"More info: {url}" if url else "",
            url=url,
            source=self.source_id,
        )

    def _parse_start(self, card) -> datetime | None:
        dates_el = card.select_one(".field--name-field-ct-dates")
        if not dates_el:
            return None
        # the first date div after the "When:" label is the next upcoming occurrence
        candidates = [
            d.get_text(" ", strip=True)
            for d in dates_el.find_all("div")
            if not d.get_text(strip=True).lower().startswith("when")
        ]
        if not candidates:
            return None
        text = _WEEKDAY_PREFIX.sub("", candidates[0])
        text = text.split(" to ")[0]  # drop a range's end time, e.g. "... 15:00 to 19:00"
        try:
            return dateutil_parser.parse(text, dayfirst=True, fuzzy=True)
        except (ValueError, OverflowError):
            return None

    def _guess_category(self, title: str) -> Category:
        haystack = title.lower()
        for category, keywords in _CATEGORY_KEYWORDS.items():
            if any(keyword in haystack for keyword in keywords):
                return category
        return Category.EVENT
