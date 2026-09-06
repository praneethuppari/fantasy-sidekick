"""Smoke tests for package import and settings."""

from fantasy_sidekick import __version__
from fantasy_sidekick.config import Settings


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_settings_defaults(monkeypatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWILIO_FROM_NUMBER", raising=False)
    settings = Settings.from_env()
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
    assert "fantasy_sidekick" in settings.database_url
    assert settings.twilio_account_sid is None
    assert settings.twilio_auth_token is None
    assert settings.twilio_from_number is None
