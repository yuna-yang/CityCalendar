from bs4 import BeautifulSoup

from citycalendar.models import Category, City
from citycalendar.sources.brussels_agenda import BrusselsAgendaSource

ROW_HTML = """
<div class="agenda col-12 views-row">
  <div class="views-field views-field-nothing"><div class="field-content row">
    <div class="col-md-9">
      <div class="title"><a href="https://www.brussels.be/gudula26" hreflang="en">Gudula26</a></div>
      <div class="fa-map-marker-alt agenda-icon">
        <div class="agenda-location-name">Cathedral of St. Michael and St. Gudula</div>
        <div class="agenda-location-address">Parvis Sainte-Gudule - 1000 Brussels</div>
      </div>
      <div class="fa-calendar-day agenda-icon">
        <div class="agenda-period">
          <time datetime="2025-12-11T12:00:00Z" class="datetime">11/12/2025</time>
          - <time datetime="2026-12-31T12:00:00Z" class="datetime">31/12/2026</time>
        </div>
      </div>
      <div class="fa-tag agenda-icon">
        <div class="agenda-cat"> Exhibition<span> // </span>Music<span> // </span>Events </div>
      </div>
    </div>
  </div></div>
</div>
"""


def _row():
    return BeautifulSoup(ROW_HTML, "html.parser").select_one("div.agenda.views-row")


def test_parse_row_extracts_title_start_location_and_category():
    source = BrusselsAgendaSource(source_id="test")
    event = source._parse_row(_row())

    assert event is not None
    assert event.title == "Gudula26"
    assert event.city == City.LEUVEN
    assert event.category == Category.EXHIBITION
    assert event.start.year == 2025
    assert event.start.month == 12
    assert event.start.day == 11
    assert event.location == "Cathedral of St. Michael and St. Gudula, Parvis Sainte-Gudule - 1000 Brussels"
    assert event.url == "https://www.brussels.be/gudula26"
