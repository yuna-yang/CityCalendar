"""Template for a Copenhagen source - disabled by default until implemented.

Good starting points for real data:
- https://www.opendata.dk/ (Danish municipal open data portal)
- Individual museum / venue websites often publish their own ICS or JSON feeds
"""
from __future__ import annotations

from citycalendar.models import Event
from citycalendar.sources.base import BaseSource


class CopenhagenTemplateSource(BaseSource):
    def __init__(self, source_id: str, city: str = "Copenhagen") -> None:
        super().__init__(source_id)
        self.city = city

    def fetch(self) -> list[Event]:
        raise NotImplementedError(
            "Implement a real Copenhagen source (scrape a site or call an API), "
            "then set enabled: true in config/sources.yaml."
        )
