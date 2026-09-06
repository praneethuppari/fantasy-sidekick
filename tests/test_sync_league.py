"""League sync upsert tests with mocked Sleeper HTTP."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from fantasy_sidekick.db.models import Base, League, LeagueUser, Roster, User
from fantasy_sidekick.sync.league import sync_league


LEAGUE_ID = "1392647678189395968"


@pytest.fixture()
def session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    db = factory()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _mock_client() -> MagicMock:
    client = MagicMock()
    client.get_league.return_value = {
        "league_id": LEAGUE_ID,
        "name": "Odysseus’s Crew",
        "season": "2026",
        "sport": "nfl",
        "status": "in_season",
        "roster_positions": ["QB", "RB", "BN"],
        "settings": {"num_teams": 12},
        "scoring_settings": {"rec": 0.5},
    }
    client.get_users.return_value = [
        {
            "user_id": "u1",
            "username": "alice",
            "display_name": "Alice",
            "avatar": "aaa",
            "is_bot": False,
            "metadata": {"team_name": "Argonauts"},
        },
        {
            "user_id": "u2",
            "username": "bob",
            "display_name": "Bob",
            "avatar": None,
            "is_bot": False,
            "metadata": {},
        },
    ]
    client.get_rosters.return_value = [
        {
            "roster_id": 1,
            "owner_id": "u1",
            "players": ["101", "102"],
            "starters": ["101", "0"],
            "reserve": None,
            "settings": {"wins": 1},
        },
        {
            "roster_id": 2,
            "owner_id": "u2",
            "players": ["201"],
            "starters": ["201"],
            "reserve": [],
            "settings": {"wins": 0},
        },
    ]
    return client


def test_sync_league_inserts_rows(session: Session) -> None:
    client = _mock_client()
    result = sync_league(session, LEAGUE_ID, client=client)
    session.commit()

    assert result.users_upserted == 2
    assert result.rosters_upserted == 2
    assert session.scalar(select(func.count()).select_from(League)) == 1
    assert session.scalar(select(func.count()).select_from(User)) == 2
    assert session.scalar(select(func.count()).select_from(LeagueUser)) == 2
    assert session.scalar(select(func.count()).select_from(Roster)) == 2

    league = session.get(League, LEAGUE_ID)
    assert league is not None
    assert league.name == "Odysseus’s Crew"
    assert league.roster_positions == ["QB", "RB", "BN"]

    roster = session.get(Roster, (LEAGUE_ID, 1))
    assert roster is not None
    assert roster.starters == ["101", "0"]
    assert roster.owner_id == "u1"

    lu = session.get(LeagueUser, (LEAGUE_ID, "u1"))
    assert lu is not None
    assert lu.team_name == "Argonauts"


def test_sync_league_second_run_upserts_without_duplicates(session: Session) -> None:
    client = _mock_client()
    sync_league(session, LEAGUE_ID, client=client)
    session.commit()

    first_name = session.get(League, LEAGUE_ID).name
    assert first_name == "Odysseus’s Crew"

    client.get_league.return_value["name"] = "Odysseus’s Crew Updated"
    client.get_rosters.return_value[0]["starters"] = ["101", "102"]

    sync_league(session, LEAGUE_ID, client=client)
    session.commit()

    assert session.scalar(select(func.count()).select_from(League)) == 1
    assert session.scalar(select(func.count()).select_from(User)) == 2
    assert session.scalar(select(func.count()).select_from(LeagueUser)) == 2
    assert session.scalar(select(func.count()).select_from(Roster)) == 2

    league = session.get(League, LEAGUE_ID)
    assert league is not None
    assert league.name == "Odysseus’s Crew Updated"

    roster = session.get(Roster, (LEAGUE_ID, 1))
    assert roster is not None
    assert roster.starters == ["101", "102"]
