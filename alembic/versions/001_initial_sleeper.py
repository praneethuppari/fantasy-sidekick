"""Initial Sleeper sync tables.

Revision ID: 001_initial_sleeper
Revises:
Create Date: 2026-09-05

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_sleeper"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSONB = postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("username", sa.String(length=128), nullable=True),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.Column("avatar", sa.String(length=128), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_table(
        "leagues",
        sa.Column("league_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=True),
        sa.Column("season", sa.String(length=16), nullable=True),
        sa.Column("sport", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=True),
        sa.Column("roster_positions", JSONB, nullable=True),
        sa.Column("settings", JSONB, nullable=True),
        sa.Column("scoring_settings", JSONB, nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("league_id"),
    )
    op.create_table(
        "players",
        sa.Column("player_id", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=256), nullable=True),
        sa.Column("first_name", sa.String(length=128), nullable=True),
        sa.Column("last_name", sa.String(length=128), nullable=True),
        sa.Column("position", sa.String(length=16), nullable=True),
        sa.Column("team", sa.String(length=16), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=True),
        sa.Column("raw", JSONB, nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("player_id"),
    )
    op.create_table(
        "league_users",
        sa.Column("league_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.Column("avatar", sa.String(length=128), nullable=True),
        sa.Column("team_name", sa.String(length=256), nullable=True),
        sa.Column("is_bot", sa.Boolean(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["league_id"], ["leagues.league_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("league_id", "user_id"),
    )
    op.create_table(
        "rosters",
        sa.Column("league_id", sa.String(length=64), nullable=False),
        sa.Column("roster_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.String(length=64), nullable=True),
        sa.Column("players", JSONB, nullable=True),
        sa.Column("starters", JSONB, nullable=True),
        sa.Column("reserve", JSONB, nullable=True),
        sa.Column("settings", JSONB, nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["league_id"], ["leagues.league_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("league_id", "roster_id"),
    )
    op.create_index(
        "ix_rosters_league_owner",
        "rosters",
        ["league_id", "owner_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_rosters_league_owner", table_name="rosters")
    op.drop_table("rosters")
    op.drop_table("league_users")
    op.drop_table("players")
    op.drop_table("leagues")
    op.drop_table("users")
