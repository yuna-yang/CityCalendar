"""Scrapes rommelmarktgids.be's dedicated Leuven flea-market listing - no signup needed.

Source: https://www.rommelmarktgids.be/rommelmarkten/leuven/
Every listing on this site is already a flea market/brocante, so no category
detection is needed here.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from citycalendar.models import Category, City, Event
from citycalendar.sources.base import BaseSource
from citycalendar.sources.common import HEADERS, build_description

logger = logging.getLogger(__name__)

BASE_URL = "https://www.rommelmarktgids.be/rommelmarkten/leuven/"

_NL_MONTHS = {
    "jan": 1, "feb": 2, "mrt": 3, "apr": 4, "mei": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12,
}
_DATE_RE = re.compile(r"(\d{1,2})\s+([a-zA-Z]{3})\.?\s+(\d{4})(?:\D+(\d{1,2}):(\d{2}))?")


class RommelmarktgidsSource(BaseSource):
    def fetch(self) -> list[Event]:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        events: list[Event] = []
        for card in soup.select("li.card"):
            event = self._parse_card(card)
            if event is not None:
                events.append(event)
        return events

    def _parse_card(self, card) -> Event | None:
        title_el = card.select_one("h3 a")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)

        date_el = card.select_one("p.card__date span")
        start = self._parse_start(date_el.get_text(" ", strip=True)) if date_el else None
        if start is None:
            logger.warning("%s: could not parse a date for %r, skipping", self.source_id, title)
            return None

        location = ""
        for meta in card.select("p.card__meta"):
            if "card__date" in (meta.get("class") or []):
                continue
            span = meta.select_one("span")
            if span:
                location = span.get_text(strip=True)
                break

        tag_el = card.select_one(".tag")
        tag = tag_el.get_text(strip=True) if tag_el else ""

        url = title_el.get("href", "")
        if url.startswith("/"):
            url = f"https://www.rommelmarktgids.be{url}"

        return Event(
            title=title,
            start=start,
            city=City.LEUVEN,
            category=Category.FLEA_MARKET,
            location=location,
            description=build_description(tag, url=url),
            url=url,
            source=self.source_id,
        )

    def _parse_start(self, text: str) -> datetime | None:
        match = _DATE_RE.search(text)
        if not match:
            return None
        day, month_abbr, year, hour, minute = match.groups()
        month = _NL_MONTHS.get(month_abbr.lower()[:3])
        if not month:
            return None
        try:
            return datetime(int(year), month, int(day), int(hour or 0), int(minute or 0))
        except ValueError:
            return None
