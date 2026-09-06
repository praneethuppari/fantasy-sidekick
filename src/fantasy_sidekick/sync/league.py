"""Upsert a Sleeper league (metadata, users, rosters) into Postgres."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from fantasy_sidekick.db.models import League, LeagueUser, Roster, User
from fantasy_sidekick.db.upsert import upsert
from fantasy_sidekick.sleeper.client import SleeperClient


@dataclass(frozen=True)
class LeagueSyncResult:
    league_id: str
    users_upserted: int
    league_users_upserted: int
    rosters_upserted: int


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _team_name(metadata: dict[str, Any] | None) -> str | None:
    if not metadata:
        return None
    return metadata.get("team_name") or metadata.get("team_name_update")


def upsert_league(session: Session, payload: dict[str, Any]) -> None:
    upsert(
        session,
        model=League,
        conflict_columns=["league_id"],
        values={
            "league_id": str(payload["league_id"]),
            "name": payload.get("name"),
            "season": (
                str(payload["season"]) if payload.get("season") is not None else None
            ),
            "sport": payload.get("sport"),
            "status": payload.get("status"),
            "roster_positions": payload.get("roster_positions"),
            "settings": payload.get("settings"),
            "scoring_settings": payload.get("scoring_settings"),
            "updated_at": _now(),
        },
    )


def upsert_users_and_league_users(
    session: Session, league_id: str, users: list[dict[str, Any]]
) -> tuple[int, int]:
    now = _now()
    # Users first so league_users FKs resolve (esp. on SQLite).
    for user in users:
        upsert(
            session,
            model=User,
            conflict_columns=["user_id"],
            values={
                "user_id": str(user["user_id"]),
                "username": user.get("username"),
                "display_name": user.get("display_name"),
                "avatar": user.get("avatar"),
                "updated_at": now,
            },
        )
    session.flush()

    for user in users:
        upsert(
            session,
            model=LeagueUser,
            conflict_columns=["league_id", "user_id"],
            values={
                "league_id": league_id,
                "user_id": str(user["user_id"]),
                "display_name": user.get("display_name"),
                "avatar": user.get("avatar"),
                "team_name": _team_name(user.get("metadata")),
                "is_bot": bool(user.get("is_bot", False)),
                "updated_at": now,
            },
        )
    return len(users), len(users)


def upsert_rosters(
    session: Session, league_id: str, rosters: list[dict[str, Any]]
) -> int:
    now = _now()
    for roster in rosters:
        owner_id = roster.get("owner_id")
        upsert(
            session,
            model=Roster,
            conflict_columns=["league_id", "roster_id"],
            values={
                "league_id": league_id,
                "roster_id": int(roster["roster_id"]),
                "owner_id": str(owner_id) if owner_id is not None else None,
                "players": roster.get("players"),
                "starters": roster.get("starters"),
                "reserve": roster.get("reserve"),
                "settings": roster.get("settings"),
                "updated_at": now,
            },
        )
    return len(rosters)


def sync_league(
    session: Session,
    league_id: str,
    client: SleeperClient | None = None,
) -> LeagueSyncResult:
    """Fetch one league from Sleeper and upsert related rows."""
    owns_client = client is None
    client = client or SleeperClient()
    try:
        league_payload = client.get_league(league_id)
        users_payload = client.get_users(league_id)
        rosters_payload = client.get_rosters(league_id)

        upsert_league(session, league_payload)
        session.flush()
        users_n, league_users_n = upsert_users_and_league_users(
            session, league_id, users_payload
        )
        rosters_n = upsert_rosters(session, league_id, rosters_payload)
        session.flush()

        return LeagueSyncResult(
            league_id=league_id,
            users_upserted=users_n,
            league_users_upserted=league_users_n,
            rosters_upserted=rosters_n,
        )
    finally:
        if owns_client:
            client.close()
