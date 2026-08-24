"""Source backed by publiq's UiTdatabank Search API (Flanders & Brussels).

Docs: https://docs.publiq.be/docs/uitdatabank/search-api/introduction
Auth: "client identification" - just a client id, no secret/token needed.
Register a free integration at https://platform.publiq.be/ to get one, then
set it via the UITDATABANK_CLIENT_ID env var.
"""
from __future__ import annotations

import os
from datetime import datetime

import requests

from citycalendar.models import Category, City, Event
from citycalendar.sources.base import BaseSource

SEARCH_URL = "https://search.uitdatabank.be/events/"

_CATEGORY_KEYWORDS = {
    Category.FLEA_MARKET: ("rommelmarkt", "brocante", "vlooienmarkt"),
    Category.EXHIBITION: ("tentoonstelling", "expo"),
    Category.MUSEUM_FREE_DAY: ("museum", "gratis"),
}


class UitdatabankSource(BaseSource):
    def __init__(self, source_id: str, city: str, categories: list[str] | None = None) -> None:
        super().__init__(source_id)
        self.city = city
        self.categories = categories or [Category.EVENT.value]

    def fetch(self) -> list[Event]:
        client_id = os.environ.get("UITDATABANK_CLIENT_ID")
        if not client_id:
            raise RuntimeError("UITDATABANK_CLIENT_ID environment variable is not set")

        response = requests.get(
            SEARCH_URL,
            headers={"X-Client-Id": client_id},
            params={"q": f"city:{self.city}", "start": 0, "limit": 100},
            timeout=20,
        )
        response.raise_for_status()
        members = response.json().get("member", [])
        return [event for item in members if (event := self._to_event(item)) is not None]

    def _to_event(self, item: dict) -> Event | None:
        start = item.get("startDate")
        if not start:
            return None
        return Event(
            title=_localized(item.get("name"), fallback="Untitled event"),
            start=_parse_datetime(start),
            end=_parse_optional(item.get("endDate")),
            city=self._resolve_city(),
            category=self._guess_category(item),
            location=_localized(item.get("location", {}).get("name"), fallback=""),
            description=_localized(item.get("description"), fallback=""),
            url=item.get("@id", ""),
            source=self.source_id,
        )

    def _resolve_city(self) -> City:
        # both Leuven and Brussels feed into the single "leuven" region
        return City.LEUVEN

    def _guess_category(self, item: dict) -> Category:
        haystack = " ".join(
            [_localized(item.get("name"), ""), _localized(item.get("description"), "")]
        ).lower()
        for category, keywords in _CATEGORY_KEYWORDS.items():
            if any(keyword in haystack for keyword in keywords):
                return category
        return Category.EVENT


def _localized(value, fallback: str) -> str:
    if isinstance(value, dict):
        return value.get("nl") or value.get("en") or next(iter(value.values()), fallback)
    return value or fallback


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _parse_optional(value: str | None) -> datetime | None:
    return _parse_datetime(value) if value else None
