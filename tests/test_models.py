from datetime import datetime

from citycalendar.models import Category, City, Event


def test_uid_is_stable_for_same_event():
    kwargs = {
        "title": "Flea market",
        "start": datetime(2026, 9, 1, 9, 0),
        "city": City.LEUVEN,
        "category": Category.FLEA_MARKET,
        "source": "test",
    }
    assert Event(**kwargs).uid == Event(**kwargs).uid


def test_uid_differs_for_different_titles():
    base = {"start": datetime(2026, 9, 1, 9, 0), "city": City.LEUVEN, "category": Category.EVENT, "source": "test"}
    assert Event(title="A", **base).uid != Event(title="B", **base).uid
