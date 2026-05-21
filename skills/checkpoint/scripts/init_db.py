"""
init_db.py — Initialize the Sentinel SQLite schema.

Usage:
    python init_db.py [--db PATH]

Creates the `checkpoints` table and associated indexes if they do not exist.
Idempotent: safe to run multiple times.
"""

import argparse
import sqlite3
import sys
from pathlib import Path

# Schema SQL
_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS checkpoints (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at              TEXT    NOT NULL DEFAULT (datetime('now')),
    session_id              TEXT    NOT NULL,
    mode                    TEXT    NOT NULL,
    target                  TEXT    NOT NULL,
    last_tool               TEXT,
    user_level              TEXT    NOT NULL DEFAULT 'operator',
    recon_done              INTEGER NOT NULL DEFAULT 0,
    phase_complete          INTEGER NOT NULL DEFAULT 0,
    active_skill            TEXT,
    pending_actions_json    TEXT    NOT NULL DEFAULT '[]',
    explained_concepts_json TEXT    NOT NULL DEFAULT '[]',
    findings_json           TEXT    NOT NULL DEFAULT '[]',
    findings_count          INTEGER NOT NULL DEFAULT 0,
    nota                    TEXT,
    raw_block               TEXT
)
"""

_CREATE_IDX_SESSION = """
CREATE INDEX IF NOT EXISTS idx_checkpoints_session
    ON checkpoints(session_id, created_at)
"""

_CREATE_IDX_TARGET = """
CREATE INDEX IF NOT EXISTS idx_checkpoints_target
    ON checkpoints(target)
"""


def init_schema(db_path: str) -> bool:
    """
    Create the checkpoints table and indexes if they don't exist.
    Returns True if newly created, False if already present.
    """
    conn = sqlite3.connect(db_path)
    try:
        # Verificar si la tabla ya existe antes de crear
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'"
        )
        already_exists = cur.fetchone() is not None

        conn.execute(_CREATE_TABLE)
        conn.execute(_CREATE_IDX_SESSION)
        conn.execute(_CREATE_IDX_TARGET)
        conn.commit()
    finally:
        conn.close()

    return not already_exists


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize the Sentinel SQLite schema for checkpoint persistence."
    )
    parser.add_argument(
        "--db",
        default="./sentinel.db",
        help="Path to the SQLite database file (default: ./sentinel.db)",
    )
    args = parser.parse_args()

    try:
        created = init_schema(args.db)
    except sqlite3.Error as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if created:
        print("OK: schema initialized")
    else:
        print("OK: schema already up to date")


if __name__ == "__main__":
    main()
