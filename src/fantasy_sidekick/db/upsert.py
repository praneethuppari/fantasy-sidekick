"""Portable upsert helpers (Postgres ON CONFLICT; SQLite get-or-update)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session


def is_postgres(session: Session) -> bool:
    return session.get_bind().dialect.name == "postgresql"


def upsert(
    session: Session,
    *,
    model: type,
    conflict_columns: list[str],
    values: dict[str, Any],
) -> None:
    """Insert or update a single row keyed by ``conflict_columns``."""
    if is_postgres(session):
        update_cols = {k: values[k] for k in values if k not in conflict_columns}
        stmt = (
            pg_insert(model)
            .values(**values)
            .on_conflict_do_update(
                index_elements=conflict_columns,
                set_=update_cols,
            )
        )
        session.execute(stmt)
        return

    pk = tuple(values[c] for c in conflict_columns)
    if len(conflict_columns) == 1:
        row = session.get(model, pk[0])
    else:
        row = session.get(model, pk)

    if row is None:
        session.add(model(**values))
    else:
        for key, value in values.items():
            if key not in conflict_columns:
                setattr(row, key, value)
