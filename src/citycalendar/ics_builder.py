"""Builds the static .ics feed files served from docs/ via GitHub Pages."""
from __future__ import annotations

from pathlib import Path

from icalendar import Calendar
from icalendar import Event as ICalEvent

from citycalendar.models import City, Event


def build_feeds(events: list[Event], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_ics(events, out_dir / "all.ics", "City Calendar - All events")

    by_feed: dict[str, list[Event]] = {}
    for event in events:
        by_feed.setdefault(event.city.value, []).append(event)

    for feed_name, feed_events in by_feed.items():
        _write_ics(feed_events, out_dir / f"{feed_name}.ics", f"City Calendar - {feed_name}")


def _write_ics(events: list[Event], path: Path, calendar_name: str) -> None:
    calendar = Calendar()
    calendar.add("prodid", "-//CityCalendar//citycalendar//EN")
    calendar.add("version", "2.0")
    calendar.add("x-wr-calname", calendar_name)
    calendar.add("x-wr-timezone", "Europe/Brussels")

    for event in events:
        vevent = ICalEvent()
        vevent.add("uid", event.uid)
        vevent.add("summary", event.title)
        vevent.add("dtstart", event.start)
        if event.end:
            vevent.add("dtend", event.end)
        if event.location:
            vevent.add("location", event.location)
        if event.description:
            vevent.add("description", event.description)
        if event.url:
            vevent.add("url", event.url)
        vevent.add("categories", [event.category.value])
        calendar.add_component(vevent)

    # write raw bytes: to_ical() already uses CRLF line endings: text-mode writing
    # on Windows would double them to \r\r\n and corrupt every line for parsers
    path.write_bytes(calendar.to_ical())
