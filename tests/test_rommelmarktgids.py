from bs4 import BeautifulSoup

from citycalendar.models import Category, City
from citycalendar.sources.rommelmarktgids import RommelmarktgidsSource

CARD_HTML = """
<li class="card">
  <a class="card__media" href="/rommelmarkt/200048/brocanterie-leuven/" tabindex="-1"></a>
  <div class="card__body">
    <div class="card__badges"><span class="tag">Brocante</span></div>
    <h3><a href="/rommelmarkt/200048/brocanterie-leuven/">BROCANTERIE met ARTISANALE MAKERSMARKT</a></h3>
    <p class="card__meta card__date"><span>di 21 jul 2026 · 07:00-16:00</span></p>
    <p class="card__meta"><span>MARTELARENPLEIN 1, 3000 Leuven</span></p>
  </div>
</li>
"""


def _card():
    return BeautifulSoup(CARD_HTML, "html.parser").select_one("li.card")


def test_parse_card_extracts_title_start_location_and_category():
    source = RommelmarktgidsSource(source_id="test")
    event = source._parse_card(_card())

    assert event is not None
    assert event.title == "BROCANTERIE met ARTISANALE MAKERSMARKT"
    assert event.city == City.LEUVEN
    assert event.category == Category.FLEA_MARKET
    assert event.start.year == 2026
    assert event.start.month == 7
    assert event.start.day == 21
    assert event.start.hour == 7
    assert event.location == "MARTELARENPLEIN 1, 3000 Leuven"
    assert event.url == "https://www.rommelmarktgids.be/rommelmarkt/200048/brocanterie-leuven/"
    assert "Brocante" in event.description
