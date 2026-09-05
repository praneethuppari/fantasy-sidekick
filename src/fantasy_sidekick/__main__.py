"""CLI entry point: ``python -m fantasy_sidekick``."""

from __future__ import annotations

from fantasy_sidekick import __version__
from fantasy_sidekick.config import Settings


def main() -> None:
    settings = Settings.from_env()
    print(f"fantasy-sidekick {__version__} ({settings.app_env})")


if __name__ == "__main__":
    main()
