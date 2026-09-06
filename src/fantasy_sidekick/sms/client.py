"""Thin Twilio client for plain-text SMS."""

from __future__ import annotations

from typing import Any

from twilio.rest import Client


class TwilioSmsClient:
    """Send a plain-text SMS to one E.164 number via Twilio."""

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_number: str,
        client: Any | None = None,
    ) -> None:
        self._from_number = from_number
        self._owns_client = client is None
        self._client = client or Client(account_sid, auth_token)

    def send(self, to: str, body: str) -> str:
        """Send ``body`` to ``to``; return the Twilio message SID."""
        message = self._client.messages.create(
            to=to,
            from_=self._from_number,
            body=body,
        )
        return str(message.sid)
