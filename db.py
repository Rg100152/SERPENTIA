"""Tiny SQLite helper shared by the Flask routes."""

from __future__ import annotations

import os
import sqlite3

from flask import current_app

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "snakes.db")


def get_db() -> sqlite3.Connection:
    """Open a connection for the current request with row access by name."""
    path = current_app.config.get("DATABASE", DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: str = DEFAULT_DB_PATH) -> None:
    """Create/seed the database on first run; never wipe user edits."""
    if not os.path.exists(path):
        from seed_snakes import seed

        seed()


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    return dict(row)


def fetch_all(query: str, params: tuple = ()) -> list[dict]:
    conn = get_db()
    try:
        return [dict(r) for r in conn.execute(query, params).fetchall()]
    finally:
        conn.close()


def fetch_one(query: str, params: tuple = ()) -> dict | None:
    conn = get_db()
    try:
        return row_to_dict(conn.execute(query, params).fetchone())
    finally:
        conn.close()
