from bs4 import BeautifulSoup

from citycalendar.models import Category, City
from citycalendar.sources.leuven_be_agenda import LeuvenBeAgendaSource

CARD_HTML = """
<a class="card row row--style-no-gutter with-image with-bg-image" href="/rollerparade">
  <div class="card__content">
    <div class="field field--name-field-ct-intertitle field--type-string h6">
      Wo 26 augustus 2026
    </div>
    <h3 class="field field--name-extra-field-f-content-navigation-title title h-lg">
      Roller- en bikeparade
      <svg><use xlink:href="#arrow-right" /></svg>
    </h3>
    <div class="field field--name-field-ct-description field--type-text-long">
      <div class="field--items">
        <div class="field--item"><p>Rijd mee door de Leuvense straten op rolschaatsen.</p></div>
      </div>
    </div>
  </div>
</a>
"""


def _card():
    return BeautifulSoup(CARD_HTML, "html.parser").select_one("a")


def test_parse_card_extracts_title_start_and_description():
    source = LeuvenBeAgendaSource(source_id="test")
    event = source._parse_card(_card())

    assert event is not None
    assert event.title == "Roller- en bikeparade"
    assert event.city == City.LEUVEN
    assert event.category == Category.EVENT
    assert event.start.year == 2026
    assert event.start.month == 8
    assert event.start.day == 26
    assert event.url == "https://www.leuven.be/rollerparade"
    assert "rolschaatsen" in event.description
