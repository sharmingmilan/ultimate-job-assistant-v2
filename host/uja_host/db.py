"""SQLite persistence for the host.

Per ADR-001 §D7: single SQLite file at <project_root>/.uja/state.db,
schema-versioned, append-only message log.

Tables:
  schema_version    — current schema revision (integer)
  conversations     — one row per chat thread
  messages          — append-only chat history
  tool_invocations  — per-tool-call audit log
  settings          — key-value preferences
  keychain_pointer  — reference to OS keychain entry (key name only)

Design notes:
- All timestamps are UTC ISO-8601 strings (sortable, human-readable).
- messages.content is JSON-serialized list-of-blocks (matches Anthropic
  message content format) so we round-trip text + tool_use + tool_result
  blocks without lossy encoding.
- Migrations are forward-only and idempotent. Each migration takes the
  open connection and bumps schema_version on success.
- Schema version 1 is the v0.2.0 P15 initial schema. Add v2+ migrations
  as the schema evolves.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

CURRENT_SCHEMA_VERSION = 2
DB_RELATIVE_PATH = ".uja/state.db"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _new_id() -> str:
    return uuid.uuid4().hex


def db_path_for_root(project_root: Path) -> Path:
    return project_root / DB_RELATIVE_PATH


@contextmanager
def open_db(project_root: Path) -> Iterator[sqlite3.Connection]:
    """Open (and migrate) the SQLite DB inside <project_root>/.uja/."""
    db_file = db_path_for_root(project_root)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_file, isolation_level=None)  # autocommit
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        _migrate(conn)
        yield conn
    finally:
        conn.close()


def _migrate(conn: sqlite3.Connection) -> None:
    """Forward-only schema migration. Idempotent."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)"
    )
    row = conn.execute("SELECT version FROM schema_version").fetchone()
    current = row["version"] if row else 0

    if current < 1:
        _migrate_to_v1(conn)
    if current < 2:
        _migrate_to_v2(conn)
    # add: if current < 3: _migrate_to_v3(conn) ...

    conn.execute("DELETE FROM schema_version")
    conn.execute("INSERT INTO schema_version (version) VALUES (?)", (CURRENT_SCHEMA_VERSION,))


def _migrate_to_v1(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS conversations (
          id          TEXT PRIMARY KEY,
          title       TEXT NOT NULL DEFAULT '',
          started_at  TEXT NOT NULL,
          updated_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
          id              TEXT PRIMARY KEY,
          conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
          role            TEXT NOT NULL CHECK (role IN ('user','assistant','system','tool')),
          content_json    TEXT NOT NULL,  -- list of content blocks, Anthropic shape
          created_at      TEXT NOT NULL,
          seq             INTEGER NOT NULL  -- per-conversation insert-order tiebreaker
        );
        CREATE INDEX IF NOT EXISTS idx_messages_conv_seq
          ON messages (conversation_id, seq);

        CREATE TABLE IF NOT EXISTS tool_invocations (
          id              TEXT PRIMARY KEY,
          conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
          message_id      TEXT REFERENCES messages(id) ON DELETE SET NULL,
          tool_name       TEXT NOT NULL,
          tool_input_json TEXT NOT NULL,
          tool_output_json TEXT,
          is_error        INTEGER NOT NULL DEFAULT 0,
          created_at      TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS settings (
          key   TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS keychain_pointer (
          id              INTEGER PRIMARY KEY CHECK (id = 1),
          service         TEXT NOT NULL,
          key_name        TEXT NOT NULL,
          last_updated_at TEXT NOT NULL
        );
        """
    )


# ----- Repository functions -----

def create_conversation(conn: sqlite3.Connection, title: str = "") -> str:
    conv_id = _new_id()
    now = _utc_now_iso()
    conn.execute(
        "INSERT INTO conversations (id, title, started_at, updated_at) VALUES (?,?,?,?)",
        (conv_id, title, now, now),
    )
    return conv_id


def list_conversations(conn: sqlite3.Connection, limit: int = 100) -> list[dict]:
    rows = conn.execute(
        "SELECT id, title, started_at, updated_at FROM conversations "
        "ORDER BY updated_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_conversation(conn: sqlite3.Connection, conv_id: str) -> Optional[dict]:
    row = conn.execute(
        "SELECT id, title, started_at, updated_at FROM conversations WHERE id = ?",
        (conv_id,),
    ).fetchone()
    return dict(row) if row else None


def delete_conversation(conn: sqlite3.Connection, conv_id: str) -> bool:
    """Hard-delete a conversation. Cascades to messages, tool_invocations,
    pending_changes, and pending_questions via ON DELETE CASCADE.

    Returns True if a row was deleted, False if conv_id did not exist."""
    cur = conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    return cur.rowcount > 0


def append_message(
    conn: sqlite3.Connection,
    conversation_id: str,
    role: str,
    content_blocks: list[dict] | str,
) -> str:
    """Append a message to a conversation.

    `content_blocks` may be either a list of Anthropic content blocks
    (preferred) or a plain string (will be wrapped in a single text block).
    """
    if isinstance(content_blocks, str):
        content_blocks = [{"type": "text", "text": content_blocks}]

    msg_id = _new_id()
    now = _utc_now_iso()
    next_seq_row = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 AS next_seq FROM messages "
        "WHERE conversation_id = ?",
        (conversation_id,),
    ).fetchone()
    next_seq = next_seq_row["next_seq"]
    conn.execute(
        "INSERT INTO messages (id, conversation_id, role, content_json, created_at, seq) "
        "VALUES (?,?,?,?,?,?)",
        (msg_id, conversation_id, role, json.dumps(content_blocks), now, next_seq),
    )
    conn.execute(
        "UPDATE conversations SET updated_at = ? WHERE id = ?",
        (now, conversation_id),
    )
    return msg_id


def list_messages(conn: sqlite3.Connection, conversation_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT id, role, content_json, created_at FROM messages "
        "WHERE conversation_id = ? ORDER BY seq ASC",
        (conversation_id,),
    ).fetchall()
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "role": r["role"],
            "content": json.loads(r["content_json"]),
            "created_at": r["created_at"],
        })
    return out


def append_tool_invocation(
    conn: sqlite3.Connection,
    conversation_id: str,
    message_id: Optional[str],
    tool_name: str,
    tool_input: Any,
    tool_output: Any = None,
    is_error: bool = False,
) -> str:
    inv_id = _new_id()
    conn.execute(
        "INSERT INTO tool_invocations "
        "(id, conversation_id, message_id, tool_name, tool_input_json, "
        " tool_output_json, is_error, created_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            inv_id,
            conversation_id,
            message_id,
            tool_name,
            json.dumps(tool_input),
            json.dumps(tool_output) if tool_output is not None else None,
            1 if is_error else 0,
            _utc_now_iso(),
        ),
    )
    return inv_id


def get_setting(conn: sqlite3.Connection, key: str) -> Optional[str]:
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def set_keychain_pointer(conn: sqlite3.Connection, service: str, key_name: str) -> None:
    conn.execute(
        "INSERT INTO keychain_pointer (id, service, key_name, last_updated_at) "
        "VALUES (1, ?, ?, ?) "
        "ON CONFLICT(id) DO UPDATE SET service = excluded.service, "
        "  key_name = excluded.key_name, last_updated_at = excluded.last_updated_at",
        (service, key_name, _utc_now_iso()),
    )


def get_keychain_pointer(conn: sqlite3.Connection) -> Optional[dict]:
    row = conn.execute(
        "SELECT service, key_name, last_updated_at FROM keychain_pointer WHERE id = 1"
    ).fetchone()
    return dict(row) if row else None


def _migrate_to_v2(conn: sqlite3.Connection) -> None:
    """Phase 16 schema additions: pending_changes + pending_questions.

    Both tables persist Anthropic tool-use side effects whose resolution
    requires human input (approve/reject a diff; answer a question). The
    chat loop yields a structured payload referencing the row ID; the UI
    reads the row, renders an interaction primitive, posts the user's
    decision back, which updates the row and unblocks the loop.
    """
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS pending_changes (
          id              TEXT PRIMARY KEY,
          conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
          tool_use_id     TEXT,
          changes_json    TEXT NOT NULL,  -- list of {path, before, after}
          summary         TEXT NOT NULL DEFAULT '',
          status          TEXT NOT NULL DEFAULT 'pending'
                          CHECK (status IN ('pending','approved','rejected','applied','expired')),
          created_at      TEXT NOT NULL,
          resolved_at     TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_pending_changes_conv
          ON pending_changes (conversation_id, status);

        CREATE TABLE IF NOT EXISTS pending_questions (
          id              TEXT PRIMARY KEY,
          conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
          tool_use_id     TEXT,
          question        TEXT NOT NULL,
          options_json    TEXT,           -- nullable JSON list
          answer          TEXT,           -- nullable until answered
          status          TEXT NOT NULL DEFAULT 'pending'
                          CHECK (status IN ('pending','answered','expired')),
          created_at      TEXT NOT NULL,
          answered_at     TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_pending_questions_conv
          ON pending_questions (conversation_id, status);
        """
    )


# ----- Pending changes (propose_changes tool) -----

def create_pending_change(
    conn: sqlite3.Connection,
    conversation_id: str,
    tool_use_id: Optional[str],
    changes: list[dict],
    summary: str = "",
) -> str:
    """Persist a set of proposed file changes; return the change-set ID.

    `changes` is a list of {"path": str, "before": str|None, "after": str}
    dicts. `before` is None for new-file proposals.
    """
    cs_id = _new_id()
    conn.execute(
        "INSERT INTO pending_changes "
        "(id, conversation_id, tool_use_id, changes_json, summary, status, created_at) "
        "VALUES (?,?,?,?,?,?,?)",
        (cs_id, conversation_id, tool_use_id, json.dumps(changes), summary, "pending", _utc_now_iso()),
    )
    return cs_id


def get_pending_change(conn: sqlite3.Connection, change_id: str) -> Optional[dict]:
    row = conn.execute(
        "SELECT id, conversation_id, tool_use_id, changes_json, summary, "
        "       status, created_at, resolved_at "
        "FROM pending_changes WHERE id = ?",
        (change_id,),
    ).fetchone()
    if not row:
        return None
    out = dict(row)
    out["changes"] = json.loads(out.pop("changes_json"))
    return out


def list_pending_changes(conn: sqlite3.Connection, conversation_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT id, tool_use_id, summary, status, created_at, resolved_at "
        "FROM pending_changes WHERE conversation_id = ? ORDER BY created_at ASC",
        (conversation_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def resolve_pending_change(
    conn: sqlite3.Connection, change_id: str, status: str
) -> bool:
    if status not in ("approved", "rejected", "applied", "expired"):
        raise ValueError(f"invalid status: {status}")
    cur = conn.execute(
        "UPDATE pending_changes SET status = ?, resolved_at = ? "
        "WHERE id = ? AND status = 'pending'",
        (status, _utc_now_iso(), change_id),
    )
    return cur.rowcount > 0


# ----- Pending questions (ask_user tool) -----

def create_pending_question(
    conn: sqlite3.Connection,
    conversation_id: str,
    tool_use_id: Optional[str],
    question: str,
    options: Optional[list[str]] = None,
) -> str:
    q_id = _new_id()
    conn.execute(
        "INSERT INTO pending_questions "
        "(id, conversation_id, tool_use_id, question, options_json, status, created_at) "
        "VALUES (?,?,?,?,?,?,?)",
        (
            q_id, conversation_id, tool_use_id, question,
            json.dumps(options) if options else None,
            "pending", _utc_now_iso(),
        ),
    )
    return q_id


def get_pending_question(conn: sqlite3.Connection, question_id: str) -> Optional[dict]:
    row = conn.execute(
        "SELECT id, conversation_id, tool_use_id, question, options_json, "
        "       answer, status, created_at, answered_at "
        "FROM pending_questions WHERE id = ?",
        (question_id,),
    ).fetchone()
    if not row:
        return None
    out = dict(row)
    raw_opts = out.pop("options_json")
    out["options"] = json.loads(raw_opts) if raw_opts else None
    return out


def list_pending_questions(conn: sqlite3.Connection, conversation_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT id, tool_use_id, question, status, created_at, answered_at "
        "FROM pending_questions WHERE conversation_id = ? ORDER BY created_at ASC",
        (conversation_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def answer_pending_question(
    conn: sqlite3.Connection, question_id: str, answer: str
) -> bool:
    cur = conn.execute(
        "UPDATE pending_questions "
        "SET status = 'answered', answer = ?, answered_at = ? "
        "WHERE id = ? AND status = 'pending'",
        (answer, _utc_now_iso(), question_id),
    )
    return cur.rowcount > 0

