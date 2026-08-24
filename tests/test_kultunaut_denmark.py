from bs4 import BeautifulSoup

from citycalendar.models import Category, City
from citycalendar.sources.kultunaut_denmark import KultunautSource

PRODUCT_HTML = """
<div data-arrnr="19717424" class="product col-lg-6 col-md-6 col-sm-6 col-xs-6">
  <div style="position:relative">
    <a href="https://www.kultunaut.dk/perl/arrmore/type-nynaut?ArrNr=19717424" class="product-content">
      <div class="arr-info">
        <div class="arr-genre">
          <span class="genre_cat notranslate">Loppemarked/Torvedag/Genbrug</span>
          <h3><strong>Loppemarked paa Islands Brygge</strong></h3>
        </div>
        <div class="kult-month-day">
          <time>Ons. 26. aug. 2026 kl. 10:00, <b class="notranslate">Islands Brygge</b></time>
        </div>
      </div>
    </a>
  </div>
</div>
"""


def _product():
    return BeautifulSoup(PRODUCT_HTML, "html.parser").select_one("div.product")


def test_parse_product_extracts_title_start_location_and_category():
    source = KultunautSource(source_id="test", area="Storkøbenhavn")
    event = source._parse_product(_product())

    assert event is not None
    assert event.title == "Loppemarked paa Islands Brygge"
    assert event.city == City.COPENHAGEN
    assert event.category == Category.FLEA_MARKET
    assert event.start.year == 2026
    assert event.start.month == 8
    assert event.start.day == 26
    assert event.start.hour == 10
    assert event.location == "Islands Brygge"
    assert event.url == "https://www.kultunaut.dk/perl/arrmore/type-nynaut?ArrNr=19717424"
    assert "Loppemarked" in event.description
    assert "https://www.kultunaut.dk/perl/arrmore/type-nynaut?ArrNr=19717424" in event.description
