"""Players catalog sync tests with mocked Sleeper HTTP."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from fantasy_sidekick.db.models import Base, Player
from fantasy_sidekick.sync.players import sync_players


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


def test_sync_players_upserts_without_duplicates(session: Session) -> None:
    client = MagicMock()
    client.get_players.return_value = {
        "101": {
            "player_id": "101",
            "full_name": "Test QB",
            "first_name": "Test",
            "last_name": "QB",
            "position": "QB",
            "team": "SF",
            "status": "Active",
            "injury_status": None,
            "number": 10,
        }
    }

    sync_players(session, sport="nfl", client=client)
    session.commit()
    assert session.scalar(select(func.count()).select_from(Player)) == 1

    client.get_players.return_value["101"]["team"] = "KC"
    sync_players(session, sport="nfl", client=client)
    session.commit()

    assert session.scalar(select(func.count()).select_from(Player)) == 1
    player = session.get(Player, "101")
    assert player is not None
    assert player.team == "KC"
    assert player.raw is not None
    assert "number" in player.raw
