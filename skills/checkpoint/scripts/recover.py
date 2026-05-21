"""
recover.py — Reconstruct a CHECKPOINT block from the Sentinel database.

Usage:
    python recover.py [--session SESSION_ID] [--db PATH]

Without --session: recovers the most recent checkpoint globally.
With --session:    recovers the most recent checkpoint for that session.

Output: a valid CHECKPOINT/END_CHECKPOINT block printed to stdout.
Errors: descriptive message on stderr, exit code 1.
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Consulta
# ---------------------------------------------------------------------------

def _fetch_row(db_path: str, session_id: str | None) -> dict:
    """
    Fetch the relevant checkpoint row from the database.
    Returns a dict keyed by column name.
    Raises RuntimeError on DB/no-results errors.
    """
    if not Path(db_path).exists():
        raise RuntimeError(
            f"Database not found: {db_path} — run init_db.py first"
        )

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        if session_id:
            cur = conn.execute(
                """
                SELECT * FROM checkpoints
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (session_id,),
            )
        else:
            cur = conn.execute(
                """
                SELECT * FROM checkpoints
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
        row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        if session_id:
            raise RuntimeError(f"No checkpoint found for session '{session_id}'")
        raise RuntimeError("No checkpoints found")

    return dict(row)


# ---------------------------------------------------------------------------
# Reconstrucción del bloque
# ---------------------------------------------------------------------------

def _bool_str(value: int) -> str:
    """Convierte 0/1 de SQLite a 'true'/'false'."""
    return "true" if value else "false"


def _compact_json(raw: str | None) -> str:
    """
    Deserializa y re-serializa como JSON compacto (sin espacios).
    Si raw es None o vacío, retorna '[]'.
    """
    if not raw:
        return "[]"
    try:
        return json.dumps(json.loads(raw), separators=(",", ":"))
    except (json.JSONDecodeError, TypeError):
        return "[]"


def reconstruct_block(row: dict) -> str:
    """
    Reconstruct a canonical CHECKPOINT block from a database row.
    Fields with NULL values are omitted (except mandatory ones).
    """
    lines = ["CHECKPOINT"]

    # Campos obligatorios — siempre presentes
    lines.append(f"session_id={row['session_id']}")
    lines.append(f"mode={row['mode']}")
    lines.append(f"target={row['target']}")

    # Campos opcionales escalares — omitir si NULL
    if row.get("last_tool"):
        lines.append(f"last_tool={row['last_tool']}")

    lines.append(f"user_level={row['user_level'] or 'operator'}")
    lines.append(f"recon_done={_bool_str(row['recon_done'])}")
    lines.append(f"phase_complete={_bool_str(row['phase_complete'])}")

    if row.get("active_skill"):
        lines.append(f"active_skill={row['active_skill']}")

    # Arrays — siempre presentes (mínimo '[]')
    lines.append(f"pending_actions={_compact_json(row.get('pending_actions_json'))}")
    lines.append(f"explained_concepts={_compact_json(row.get('explained_concepts_json'))}")
    lines.append(f"findings={_compact_json(row.get('findings_json'))}")

    # Nota — omitir si NULL
    if row.get("nota"):
        lines.append(f"nota={row['nota']}")

    lines.append("END_CHECKPOINT")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _resolve_db(cli_db: str | None) -> str:
    """Resolve DB path: CLI arg > $SENTINEL_DB > default."""
    if cli_db:
        return cli_db
    return os.environ.get("SENTINEL_DB", "./sentinel.db")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reconstruct a CHECKPOINT block from the Sentinel database."
    )
    parser.add_argument(
        "--session",
        default=None,
        help="Session ID to recover. If omitted, recovers the latest global checkpoint.",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Path to the SQLite database (default: ./sentinel.db or $SENTINEL_DB)",
    )
    args = parser.parse_args()

    db_path = _resolve_db(args.db)

    try:
        row = _fetch_row(db_path, args.session)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"ERROR (db): {e}", file=sys.stderr)
        sys.exit(1)

    block = reconstruct_block(row)
    print(block)


if __name__ == "__main__":
    main()
