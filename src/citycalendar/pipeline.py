"""Orchestrates: run every enabled source, dedupe, cache, and build ICS feeds."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import yaml

from citycalendar.ics_builder import build_feeds
from citycalendar.models import Event
from citycalendar.registry import load_source

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = ROOT / "config" / "sources.yaml"
EVENTS_CACHE = ROOT / "data" / "events.json"
DOCS_DIR = ROOT / "docs"


def run() -> None:
    config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))

    all_events: list[Event] = []
    for entry in config["sources"]:
        if not entry.get("enabled", True):
            continue
        source = load_source(entry["module"], entry["class"], entry["id"], entry.get("params", {}))
        all_events.extend(source.collect())

    # last write wins per uid, order doesn't matter since duplicates are identical events
    deduped = list({event.uid: event for event in all_events}.values())
    deduped.sort(key=lambda event: event.start.replace(tzinfo=None))

    _write_events_cache(deduped)
    build_feeds(deduped, DOCS_DIR)
    logger.info("Wrote %d events across feeds in %s", len(deduped), DOCS_DIR)


def _write_events_cache(events: list[Event]) -> None:
    EVENTS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "uid": event.uid,
            "title": event.title,
            "start": event.start.isoformat(),
            "end": event.end.isoformat() if event.end else None,
            "city": event.city.value,
            "category": event.category.value,
            "location": event.location,
            "description": event.description,
            "url": event.url,
            "source": event.source,
        }
        for event in events
    ]
    EVENTS_CACHE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run()
