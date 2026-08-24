from datetime import datetime

from icalendar import Calendar

from citycalendar.ics_builder import build_feeds
from citycalendar.models import Category, City, Event


def test_build_feeds_writes_one_file_per_region_with_emoji_titles(tmp_path):
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

    assert sorted(p.name for p in tmp_path.glob("*.ics")) == ["copenhagen.ics", "leuven.ics"]

    leuven_ics = Calendar.from_ical((tmp_path / "leuven.ics").read_text(encoding="utf-8"))
    leuven_events = leuven_ics.walk("VEVENT")
    assert len(leuven_events) == 1
    assert str(leuven_events[0]["summary"]) == "🧺 Leuven flea market"

    copenhagen_ics = Calendar.from_ical((tmp_path / "copenhagen.ics").read_text(encoding="utf-8"))
    copenhagen_events = copenhagen_ics.walk("VEVENT")
    assert len(copenhagen_events) == 1
    assert str(copenhagen_events[0]["summary"]) == "🏛️ Copenhagen museum free day"
