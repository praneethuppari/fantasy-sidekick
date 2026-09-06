"""Upsert the NFL players catalog from Sleeper into Postgres."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from fantasy_sidekick.db.models import Player
from fantasy_sidekick.db.upsert import upsert
from fantasy_sidekick.sleeper.client import SleeperClient

_PROMOTED_KEYS = frozenset(
    {
        "player_id",
        "full_name",
        "first_name",
        "last_name",
        "position",
        "team",
        "status",
    }
)


@dataclass(frozen=True)
class PlayersSyncResult:
    sport: str
    players_upserted: int


def _now() -> datetime:
    return datetime.now(timezone.utc)


def upsert_players(session: Session, players: dict[str, Any]) -> int:
    now = _now()
    count = 0
    for player_id, payload in players.items():
        if not isinstance(payload, dict):
            continue
        raw = {k: v for k, v in payload.items() if k not in _PROMOTED_KEYS}
        full_name = payload.get("full_name")
        if not full_name:
            parts = [payload.get("first_name"), payload.get("last_name")]
            full_name = " ".join(p for p in parts if p) or None

        upsert(
            session,
            model=Player,
            conflict_columns=["player_id"],
            values={
                "player_id": str(player_id),
                "full_name": full_name,
                "first_name": payload.get("first_name"),
                "last_name": payload.get("last_name"),
                "position": payload.get("position"),
                "team": payload.get("team"),
                "status": payload.get("status"),
                "raw": raw,
                "updated_at": now,
            },
        )
        count += 1
    return count


def sync_players(
    session: Session,
    sport: str = "nfl",
    client: SleeperClient | None = None,
) -> PlayersSyncResult:
    """Fetch the full players catalog and upsert rows."""
    owns_client = client is None
    client = client or SleeperClient()
    try:
        payload = client.get_players(sport)
        n = upsert_players(session, payload)
        session.flush()
        return PlayersSyncResult(sport=sport, players_upserted=n)
    finally:
        if owns_client:
            client.close()
