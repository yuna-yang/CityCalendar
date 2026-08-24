from icalendar import Calendar as ICalCalendar

from citycalendar.models import Category, City
from citycalendar.sources.oplevelser_kbh import OplevelserKbhFleaMarketSource

SAMPLE_ICS = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:test-1@oplevelser-i-koebenhavn.dk
SUMMARY:Loppemarked Toftegaards Plads
DTSTART:20260829T100000
DTEND:20260829T150000
LOCATION:Toftegaards Plads\\, Valby
DESCRIPTION:Stort loppemarked med mange boder.
URL:https://oplevelser-i-koebenhavn.dk/begivenhed/loppemarked-toftegaards-plads/
END:VEVENT
END:VCALENDAR
"""


def test_to_event_extracts_fields_from_ical_vevent():
    calendar = ICalCalendar.from_ical(SAMPLE_ICS)
    vevent = calendar.walk("VEVENT")[0]

    source = OplevelserKbhFleaMarketSource(source_id="test")
    event = source._to_event(vevent)

    assert event is not None
    assert event.title == "Loppemarked Toftegaards Plads"
    assert event.city == City.COPENHAGEN
    assert event.category == Category.FLEA_MARKET
    assert event.start.year == 2026
    assert event.start.month == 8
    assert event.start.day == 29
    assert event.end is not None
    assert event.end.hour == 15
    assert event.location == "Toftegaards Plads, Valby"
    assert event.url == "https://oplevelser-i-koebenhavn.dk/begivenhed/loppemarked-toftegaards-plads/"
