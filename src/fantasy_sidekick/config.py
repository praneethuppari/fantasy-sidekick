"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings for Fantasy Sidekick."""

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = (
        "postgresql+psycopg://fantasy:fantasy@localhost:5433/fantasy_sidekick"
    )
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_from_number: str | None = None

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg://fantasy:fantasy@localhost:5433/fantasy_sidekick",
            ),
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID") or None,
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN") or None,
            twilio_from_number=os.getenv("TWILIO_FROM_NUMBER") or None,
        )

    def require_twilio(self) -> tuple[str, str, str]:
        """Return Twilio credentials or raise if any are missing."""
        missing = [
            name
            for name, value in (
                ("TWILIO_ACCOUNT_SID", self.twilio_account_sid),
                ("TWILIO_AUTH_TOKEN", self.twilio_auth_token),
                ("TWILIO_FROM_NUMBER", self.twilio_from_number),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                "Missing required Twilio settings: " + ", ".join(missing)
            )
        assert self.twilio_account_sid is not None
        assert self.twilio_auth_token is not None
        assert self.twilio_from_number is not None
        return (
            self.twilio_account_sid,
            self.twilio_auth_token,
            self.twilio_from_number,
        )
