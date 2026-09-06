"""Sleeper HTTP client unit tests."""

from __future__ import annotations

import httpx

from fantasy_sidekick.sleeper.client import SleeperClient


def test_get_league_builds_path() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/league/abc")
        return httpx.Response(200, json={"league_id": "abc"})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport, base_url="https://api.sleeper.app/v1") as http:
        client = SleeperClient(client=http)
        assert client.get_league("abc")["league_id"] == "abc"
