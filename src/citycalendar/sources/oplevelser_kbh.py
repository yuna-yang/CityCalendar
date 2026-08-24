"""Consumes oplevelser-i-koebenhavn.dk's native ICS export, filtered to flea markets.

Source: https://oplevelser-i-koebenhavn.dk/loppemarkeder-koebenhavn/
This site runs the "The Events Calendar" WordPress plugin, which exposes a real .ics
feed - no HTML scraping needed, just re-parsing their already-structured calendar data.
"""
from __future__ import annotations

import logging
from datetime import date, datetime

import requests
from icalendar import Calendar as ICalCalendar

from citycalendar.models import Category, City, Event
from citycalendar.sources.base import BaseSource

logger = logging.getLogger(__name__)

FEED_URL = (
    "https://oplevelser-i-koebenhavn.dk/"
    "?post_type=tribe_events&ical=1&eventDisplay=list&tribe_events_cat=loppemarked"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CityCalendarBot/1.0)"}


class OplevelserKbhFleaMarketSource(BaseSource):
    def fetch(self) -> list[Event]:
        response = requests.get(FEED_URL, headers=HEADERS, timeout=20)
        response.raise_for_status()
        calendar = ICalCalendar.from_ical(response.content)

        events: list[Event] = []
        for vevent in calendar.walk("VEVENT"):
            event = self._to_event(vevent)
            if event is not None:
                events.append(event)
        return events

    def _to_event(self, vevent) -> Event | None:
        title = str(vevent.get("summary", "")).strip()
        start = _as_datetime(vevent.get("dtstart"))
        if not title or start is None:
            logger.warning("%s: could not parse a date for %r, skipping", self.source_id, title)
            return None

        return Event(
            title=title,
            start=start,
            end=_as_datetime(vevent.get("dtend")),
            city=City.COPENHAGEN,
            category=Category.FLEA_MARKET,
            location=str(vevent.get("location", "")),
            description=str(vevent.get("description", "")),
            url=str(vevent.get("url", "")),
            source=self.source_id,
        )


def _as_datetime(field) -> datetime | None:
    if field is None:
        return None
    value = field.dt
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    return None
