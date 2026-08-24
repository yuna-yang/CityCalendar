# City Calendar

An open, subscribable calendar of flea markets, exhibitions, museum free days
and other events — starting with two regions: Copenhagen (incl. Greater
Copenhagen and notable Odense/Malmo events) and Leuven (incl. Brussels and
nearby areas). Subscribe in Google Calendar once, keep getting updates
forever, no account needed.

## How it works

```mermaid
flowchart LR
    A[Sources: scrapers / APIs] --> B[Pipeline: fetch, dedupe, cache]
    B --> C[ICS feeds in docs/]
    C -->|GitHub Pages, static URL| D[Google Calendar subscription]
```

1. Each **source** (`src/citycalendar/sources/`) fetches events from a site or API.
2. The **pipeline** (`src/citycalendar/pipeline.py`) runs every enabled source,
   falls back to the last good cache if a source breaks, dedupes events, and
   writes `.ics` files to `docs/`.
3. `docs/` is published with **GitHub Pages**, giving each feed a stable URL.
4. A scheduled **GitHub Action** re-runs the pipeline and commits refreshed
   feeds, so anyone who subscribed keeps getting updates automatically.

## Feeds

Just two feeds, one per region. Categories aren't split into separate feeds —
instead every event's title is prefixed with a category emoji, so you can tell
flea markets/exhibitions/museum free days/general events apart at a glance
within a single region feed.

| File | Contents |
| --- | --- |
| `docs/copenhagen.ics` | Copenhagen region (Greater Copenhagen, notable Odense/Malmo events) |
| `docs/leuven.ics` | Leuven region (Leuven, Brussels, nearby areas) |

Subscribe in Google Calendar: **Settings → Add calendar → From URL**, using the
GitHub Pages URL of one of the files above.

## Categories

Flea market (🧺), exhibition (🖼️), museum free day (🏛️), and general event (🎫) —
set per source and tagged on each event's `CATEGORIES` field, and also prefixed
onto the event title as an emoji, since most calendar clients don't expose
per-event coloring or filtering from a subscribed ICS feed.

## Project layout

```
config/sources.yaml              registry of enabled sources
src/citycalendar/models.py       Event, City, Category
src/citycalendar/sources/        one module per data source (extend here)
src/citycalendar/pipeline.py     orchestrates fetch -> dedupe -> build
src/citycalendar/ics_builder.py  builds the .ics files
data/cache/                      last-known-good data per source (robustness)
docs/                            generated feeds, served by GitHub Pages
```

## Adding a new source or city

1. Create `src/citycalendar/sources/<name>.py` with a class extending `BaseSource`
   and implementing `fetch() -> list[Event]`.
2. Register it in `config/sources.yaml` with its module, class, and params.
3. If it needs a city not yet in `models.City`, add it there and map it to a
   feed name in `ics_builder._FEED_BY_CITY`.

A source only needs to raise on failure — `BaseSource.collect()` already
handles logging and falling back to cached data, so one broken scraper never
takes down the whole feed.

## Current sources

- **Visit Leuven calendar** (`sources/leuven_calendar.py`) — real, working. Scrapes the
  public [visitleuven.be/en/calendar](https://www.visitleuven.be/en/calendar) page. No
  registration or API key needed. Also used (via its own "Shopping and markets" facet)
  for a dedicated `leuven_flea_markets` feed.
- **City of Leuven agenda** (`sources/leuven_be_agenda.py`) — real, working. Scrapes
  [leuven.be/agenda](https://www.leuven.be/agenda), the city government's own listing —
  distinct from the tourism site, covering municipal/community events (info sessions,
  workshops, sports, book sales, etc.). No registration needed.
- **Brussels agenda** (`sources/brussels_agenda.py`) — real, working. Scrapes the public
  [brussels.be/agenda](https://www.brussels.be/agenda) page, which conveniently publishes
  category tags per event. No registration or API key needed. Also used (via its own
  "Flea market & rummage sales" category) for a dedicated `brussels_flea_markets` feed.
- **Rommelmarktgids** (`sources/rommelmarktgids.py`) — real, working. Scrapes
  [rommelmarktgids.be](https://www.rommelmarktgids.be/rommelmarkten/leuven/), a site
  entirely dedicated to Leuven-area flea markets/brocante. No registration needed.
- **Oplevelser i København** (`sources/oplevelser_kbh.py`) — real, working. Consumes the
  native ICS export from [oplevelser-i-koebenhavn.dk](https://oplevelser-i-koebenhavn.dk/loppemarkeder-koebenhavn/)'s
  dedicated flea-market listing (it runs "The Events Calendar" WordPress plugin, which
  publishes a real `.ics` feed — no HTML scraping needed, just re-parsing their own
  calendar data). No registration needed.
- **UiTdatabank** (`sources/uitdatabank.py`) — optional, disabled by default. A richer,
  official alternative covering all of Flanders & Brussels via publiq's Search API, but
  requires registering a free integration at [platform.publiq.be](https://platform.publiq.be/)
  (pick "UiTdatabank Search API") and setting the client id as `UITDATABANK_CLIENT_ID`.
  Enable it in `config/sources.yaml` if you want broader coverage later.
- **Kultunaut** (`sources/kultunaut_denmark.py`) — real, working. Scrapes
  [kultunaut.dk](https://www.kultunaut.dk/), Denmark's main public cultural events database.
  One instance covers Greater Copenhagen (`Area=Storkøbenhavn`), another pulls a small,
  capped set of top-rated highlights from Odense, and a third filters to its own
  "Loppemarked/Torvedag/Genbrug" (flea market) genre. No registration or API key needed.
  Note: Kultunaut is Denmark-only, so Malmo (Sweden) isn't covered — that would need a
  separate Swedish source.

## Local development

```bash
pip install -e ".[dev]"
python -m citycalendar.cli   # builds docs/*.ics from config/sources.yaml
pytest
```

## One-time repo setup (once pushed to GitHub)

- Enable GitHub Pages, serving from the `docs/` folder on `main`.
- No secrets are required for the default sources. If you later enable UiTdatabank,
  also add `UITDATABANK_CLIENT_ID` as a repository secret.

## License

MIT — see [LICENSE](LICENSE).
