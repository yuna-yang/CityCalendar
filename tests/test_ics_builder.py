from datetime import datetime

from icalendar import Calendar

from citycalendar.ics_builder import build_feeds
from citycalendar.models import Category, City, Event


def test_build_feeds_writes_all_and_per_city_files(tmp_path):
    events = [
        Event(
            title="Leuven flea market",
            start=datetime(2026, 9, 5, 8, 0),
            city=City.LEUVEN,
            category=Category.FLEA_MARKET,
            source="test",
        ),
        Event(
            title="Copenhagen museum free day",
            start=datetime(2026, 9, 6, 10, 0),
            city=City.COPENHAGEN,
            category=Category.MUSEUM_FREE_DAY,
            source="test",
        ),
    ]

    build_feeds(events, tmp_path)

    all_ics = Calendar.from_ical((tmp_path / "all.ics").read_text(encoding="utf-8"))
    assert len(all_ics.walk("VEVENT")) == 2

    leuven_ics = Calendar.from_ical((tmp_path / "leuven-brussels.ics").read_text(encoding="utf-8"))
    assert len(leuven_ics.walk("VEVENT")) == 1

    copenhagen_ics = Calendar.from_ical((tmp_path / "copenhagen.ics").read_text(encoding="utf-8"))
    assert len(copenhagen_ics.walk("VEVENT")) == 1
