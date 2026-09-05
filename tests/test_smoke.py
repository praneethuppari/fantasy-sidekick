"""Smoke tests for package import and settings."""

from fantasy_sidekick import __version__
from fantasy_sidekick.config import Settings


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_settings_defaults(monkeypatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    settings = Settings.from_env()
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
