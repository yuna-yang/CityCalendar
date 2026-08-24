"""Base class every event source must implement."""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from citycalendar.models import Category, City, Event

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "cache"


class BaseSource(ABC):
    def __init__(self, source_id: str) -> None:
        self.source_id = source_id

    @abstractmethod
    def fetch(self) -> list[Event]:
        """Fetch fresh events from the upstream source. Raise on any failure."""

    def collect(self) -> list[Event]:
        """Fetch, falling back to the last good cache so one broken source never empties the feed."""
        cache_file = CACHE_DIR / f"{self.source_id}.json"
        try:
            events = self.fetch()
            self._write_cache(cache_file, events)
            logger.info("%s: fetched %d events", self.source_id, len(events))
            return events
        except Exception:
            logger.exception("%s: fetch failed, falling back to cache", self.source_id)
            return self._read_cache(cache_file)

    @staticmethod
    def _write_cache(cache_file: Path, events: list[Event]) -> None:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                **asdict(event),
                "start": event.start.isoformat(),
                "end": event.end.isoformat() if event.end else None,
            }
            for event in events
        ]
        cache_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def _read_cache(cache_file: Path) -> list[Event]:
        if not cache_file.exists():
            return []
        raw = json.loads(cache_file.read_text(encoding="utf-8"))
        events = []
        for item in raw:
            item["start"] = datetime.fromisoformat(item["start"])
            item["end"] = datetime.fromisoformat(item["end"]) if item.get("end") else None
            item["city"] = City(item["city"])
            item["category"] = Category(item["category"])
            events.append(Event(**item))
        return events
