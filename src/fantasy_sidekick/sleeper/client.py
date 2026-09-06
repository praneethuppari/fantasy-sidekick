"""HTTP client for the read-only Sleeper API."""

from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.sleeper.app/v1"


class SleeperClient:
    """Thin wrapper around Sleeper GET endpoints."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        client: httpx.Client | None = None,
        timeout: float = 60.0,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(base_url=base_url, timeout=timeout)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> SleeperClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _get_json(self, path: str) -> Any:
        response = self._client.get(path)
        response.raise_for_status()
        return response.json()

    def get_user(self, id_or_username: str) -> dict[str, Any]:
        return self._get_json(f"/user/{id_or_username}")

    def get_user_leagues(
        self, user_id: str, sport: str, season: str
    ) -> list[dict[str, Any]]:
        return self._get_json(f"/user/{user_id}/leagues/{sport}/{season}")

    def get_league(self, league_id: str) -> dict[str, Any]:
        return self._get_json(f"/league/{league_id}")

    def get_rosters(self, league_id: str) -> list[dict[str, Any]]:
        return self._get_json(f"/league/{league_id}/rosters")

    def get_users(self, league_id: str) -> list[dict[str, Any]]:
        return self._get_json(f"/league/{league_id}/users")

    def get_players(self, sport: str = "nfl") -> dict[str, Any]:
        return self._get_json(f"/players/{sport}")
