"""Entry point: `python -m citycalendar.cli`."""
from __future__ import annotations

from citycalendar.pipeline import run


def main() -> None:
    run()


if __name__ == "__main__":
    main()
