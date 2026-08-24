from bs4 import BeautifulSoup

from citycalendar.models import Category, City
from citycalendar.sources.leuven_calendar import VisitLeuvenSource

CARD_HTML = """
<a class="state--published node node--type-ct-activity node--view-mode-vm-overview card"
   href="/en/monday-market">
  <div class="card__content">
    <h3 class="field field--name-extra-field-f-content-navigation-title h-sm">
      <span>Market in Wijgmaal</span>
    </h3>
    <div class="field--name-field-ct-dates multiple-items--extra-space">
      <div class="ds-label multiple-results">When: </div>
      <div>Monday 24 August 2026, 15:00 to 19:00 </div>
      <div>Monday 31 August 2026, 15:00 to 19:00 </div>
      + 15 other moments
    </div>
    <div class="field field--name-field-ct-activity-location field--label-inline">
      <div class="field--label field-label-inline">Where</div>
      <div class="field--items">
        <div class="field--item">Parking Sportcomplex Ymeria, Wijgmaal</div>
      </div>
    </div>
  </div>
</a>
"""


def _card():
    return BeautifulSoup(CARD_HTML, "html.parser").select_one("a")


def test_parse_card_extracts_title_start_location_and_category():
    source = VisitLeuvenSource(source_id="test")
    event = source._parse_card(_card())

    assert event is not None
    assert event.title == "Market in Wijgmaal"
    assert event.city == City.LEUVEN
    assert event.category == Category.FLEA_MARKET
    assert event.start.year == 2026
    assert event.start.month == 8
    assert event.start.day == 24
    assert event.start.hour == 15
    assert event.location == "Parking Sportcomplex Ymeria, Wijgmaal"
    assert event.url == "https://www.visitleuven.be/en/monday-market"
    assert "https://www.visitleuven.be/en/monday-market" in event.description
