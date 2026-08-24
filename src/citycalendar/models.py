"""Core data model shared by every source and the ICS builder."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Category(str, Enum):
    FLEA_MARKET = "flea_market"
    EXHIBITION = "exhibition"
    MUSEUM_FREE_DAY = "museum_free_day"
    EVENT = "event"


class City(str, Enum):
    # regions, not strict city names: LEUVEN also covers Brussels + nearby Belgium,
    # COPENHAGEN also covers Greater Copenhagen + notable Odense/Malmo events
    COPENHAGEN = "copenhagen"
    LEUVEN = "leuven"


@dataclass
class Event:
    title: str
    start: datetime
    city: City
    category: Category
    end: datetime | None = None
    location: str = ""
    description: str = ""
    url: str = ""
    source: str = ""

    @property
    def uid(self) -> str:
        # stable id so re-scraping the same event never creates a duplicate
        raw = f"{self.source}|{self.title}|{self.start.isoformat()}"
        return f"{hashlib.sha1(raw.encode('utf-8')).hexdigest()}@citycalendar"
