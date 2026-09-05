"""Smoke tests for the Fantasy Sidekick scaffold."""

from fantasy_sidekick import __version__
from fantasy_sidekick.config import Settings


def test_version_is_semver_like() -> None:
    assert __version__.count(".") >= 1


def test_settings_defaults() -> None:
    settings = Settings.from_env()
    assert settings.app_env
    assert settings.log_level
