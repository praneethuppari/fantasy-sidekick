"""SQLAlchemy ORM models for Sleeper league data."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON


# JSONB on Postgres; JSON elsewhere (e.g. SQLite in unit tests).
JsonbCompat = JSON().with_variant(JSONB(), "postgresql")


class Base(DeclarativeBase):
    """Declarative base for all models."""


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(128), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class League(Base):
    __tablename__ = "leagues"

    league_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    season: Mapped[str | None] = mapped_column(String(16), nullable=True)
    sport: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    roster_positions: Mapped[list | None] = mapped_column(JsonbCompat, nullable=True)
    settings: Mapped[dict | None] = mapped_column(JsonbCompat, nullable=True)
    scoring_settings: Mapped[dict | None] = mapped_column(JsonbCompat, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Roster(Base):
    __tablename__ = "rosters"
    __table_args__ = (Index("ix_rosters_league_owner", "league_id", "owner_id"),)

    league_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("leagues.league_id", ondelete="CASCADE"),
        primary_key=True,
    )
    roster_id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    players: Mapped[list | None] = mapped_column(JsonbCompat, nullable=True)
    starters: Mapped[list | None] = mapped_column(JsonbCompat, nullable=True)
    reserve: Mapped[list | None] = mapped_column(JsonbCompat, nullable=True)
    settings: Mapped[dict | None] = mapped_column(JsonbCompat, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class LeagueUser(Base):
    __tablename__ = "league_users"

    league_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("leagues.league_id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(128), nullable=True)
    team_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Player(Base):
    __tablename__ = "players"

    player_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    position: Mapped[str | None] = mapped_column(String(16), nullable=True)
    team: Mapped[str | None] = mapped_column(String(16), nullable=True)
    status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw: Mapped[dict | None] = mapped_column(JsonbCompat, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
