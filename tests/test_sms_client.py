"""Twilio SMS client unit tests (mocked; no live send)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from fantasy_sidekick.config import Settings
from fantasy_sidekick.sms.client import TwilioSmsClient


def test_send_returns_message_sid() -> None:
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(sid="SMtest123")

    sms = TwilioSmsClient(
        account_sid="ACfake",
        auth_token="token",
        from_number="+15550001111",
        client=mock_client,
    )
    sid = sms.send(to="+15551234567", body="Fantasy Sidekick test")

    assert sid == "SMtest123"
    mock_client.messages.create.assert_called_once_with(
        to="+15551234567",
        from_="+15550001111",
        body="Fantasy Sidekick test",
    )


def test_require_twilio_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWILIO_FROM_NUMBER", raising=False)
    settings = Settings.from_env()
    with pytest.raises(ValueError, match="TWILIO_ACCOUNT_SID"):
        settings.require_twilio()


def test_require_twilio_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACabc")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "+15550001111")
    settings = Settings.from_env()
    assert settings.require_twilio() == ("ACabc", "secret", "+15550001111")
