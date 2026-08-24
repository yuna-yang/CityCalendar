"""Shared helpers used by multiple scrapers, to avoid repeating the same
boilerplate (HTTP headers, keyword-based category guessing, description building)
in every source module.
"""
from __future__ import annotations

from citycalendar.models import Category

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CityCalendarBot/1.0)"}


def guess_category(haystack: str, keywords: dict[Category, tuple[str, ...]]) -> Category:
    haystack = haystack.lower()
    for category, terms in keywords.items():
        if any(term in haystack for term in terms):
            return category
    return Category.EVENT


def build_description(*parts: str, url: str = "") -> str:
    all_parts = [*parts, f"More info: {url}" if url else ""]
    return "\n\n".join(part for part in all_parts if part)
