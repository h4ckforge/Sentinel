"""
checkpoint.py — Parse a CHECKPOINT block and persist it to SQLite.

Usage:
    python checkpoint.py [--db PATH] [--file PATH|-]

Reads a CHECKPOINT/END_CHECKPOINT block from stdin or a file, parses it,
and inserts a row into the checkpoints table.

Exit codes:
    0 — success
    1 — parse error or database error
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

CHECKPOINT_RE = re.compile(
    r"^CHECKPOINT\s*$(.*?)^END_CHECKPOINT\s*$",
    re.DOTALL | re.MULTILINE,
)

ARRAY_FIELDS    = {"pending_actions", "explained_concepts", "findings"}
BOOL_FIELDS     = {"recon_done", "phase_complete"}
REQUIRED_FIELDS = {"session_id", "mode", "target"}

DEFAULTS = {
    "last_tool":          None,
    "user_level":         "operator",
    "recon_done":         False,
    "phase_complete":     False,
    "active_skill":       None,
    "pending_actions":    [],
    "explained_concepts": [],
    "findings":           [],
    "nota":               None,
}


def parse_checkpoint(text: str) -> dict:
    """
    Parse a CHECKPOINT/END_CHECKPOINT block from arbitrary text.

    Returns a dict with fully-typed fields.
    Raises ValueError for missing required fields or invalid JSON arrays.
    """
    m = CHECKPOINT_RE.search(text)
    if not m:
        raise ValueError("No CHECKPOINT/END_CHECKPOINT block found in input")

    raw_block = m.group(0)   # bloque completo incluyendo delimitadores
    body      = m.group(1)

    fields: dict = {}
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            # línea malformada: sin '=' — ignorar silenciosamente
            continue
        key   = key.strip()
        value = value.strip()

        if key in ARRAY_FIELDS:
            try:
                fields[key] = json.loads(value)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Field '{key}' is not valid JSON: {e}\nValue: {value!r}"
                )
        elif key in BOOL_FIELDS:
            fields[key] = value.lower() == "true"
        else:
            # Escalar: None si vacío
            fields[key] = value if value else None

    # Validar campos requeridos — falla ruidoso
    missing = REQUIRED_FIELDS - fields.keys()
    if missing:
        raise ValueError(f"Missing required fields: {sorted(missing)}")

    # Aplicar defaults para opcionales ausentes
    result = {**DEFAULTS, **fields}

    # Calcular findings_count (no confiar en el bloque)
    result["findings_count"] = len(result["findings"])

    # Siempre incluir raw_block completo
    result["raw_block"] = raw_block

    return result


# ---------------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------------

def _table_exists(conn: sqlite3.Connection) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'"
    )
    return cur.fetchone() is not None


def save_checkpoint(parsed: dict, db_path: str) -> int:
    """
    Insert a parsed checkpoint dict into the database.
    Returns the rowid (id) of the inserted row.
    Raises RuntimeError if the DB hasn't been initialized.
    """
    if not Path(db_path).exists():
        raise RuntimeError(
            f"Database not found: {db_path} — run init_db.py first"
        )

    conn = sqlite3.connect(db_path)
    try:
        if not _table_exists(conn):
            raise RuntimeError(
                f"Table 'checkpoints' not found in {db_path} — run init_db.py first"
            )

        cur = conn.execute(
            """
            INSERT INTO checkpoints (
                session_id,
                mode,
                target,
                last_tool,
                user_level,
                recon_done,
                phase_complete,
                active_skill,
                pending_actions_json,
                explained_concepts_json,
                findings_json,
                findings_count,
                nota,
                raw_block
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                parsed["session_id"],
                parsed["mode"],
                parsed["target"],
                parsed["last_tool"],
                parsed["user_level"],
                1 if parsed["recon_done"] else 0,
                1 if parsed["phase_complete"] else 0,
                parsed["active_skill"],
                json.dumps(parsed["pending_actions"]),
                json.dumps(parsed["explained_concepts"]),
                json.dumps(parsed["findings"]),
                parsed["findings_count"],
                parsed["nota"],
                parsed["raw_block"],
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


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
        description="Parse a CHECKPOINT block and persist it to SQLite."
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Path to the SQLite database (default: ./sentinel.db or $SENTINEL_DB)",
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Input file path. Use '-' or omit to read from stdin.",
    )
    args = parser.parse_args()

    db_path = _resolve_db(args.db)

    # Leer input
    try:
        if args.file and args.file != "-":
            text = Path(args.file).read_text(encoding="utf-8")
        else:
            text = sys.stdin.read()
    except OSError as e:
        print(f"ERROR reading input: {e}", file=sys.stderr)
        sys.exit(1)

    # Parsear
    try:
        parsed = parse_checkpoint(text)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Persistir
    try:
        row_id = save_checkpoint(parsed, db_path)
    except (RuntimeError, sqlite3.Error) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: checkpoint saved (id={row_id}, session={parsed['session_id']})")


if __name__ == "__main__":
    main()
