"""HITL MCP tools — propose / approve / reject changes + ask / answer.

Implements the human-in-the-loop tool surface from ADR-002 D1. Splits
into two halves:

  - "Outbound" tools (`propose_changes`, `ask_user`) wrap
    `host/uja_host/tools/skill_tools.py`. They persist a pending row in
    SQLite (no disk side effects) and return the row id; the agent
    pauses while a human resolves it elsewhere.

  - "Inbound" tools (`approve_changes`, `reject_changes`,
    `answer_question`) re-implement the small bit of business logic that
    the Phase 17.5 FastAPI route handlers in `host/uja_host/api/changes.py`
    and `host/uja_host/api/questions.py` carry. The deprecated FastAPI
    routes stay as-is in the deprecated tree per ADR-002 D3 — this
    module owns the MCP-side equivalent. Errors raise `ToolError`
    (FastMCP renders them as structured `is_error: true` payloads)
    instead of `HTTPException`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from uja_host import config as host_config
from uja_host.db import (
    answer_pending_question,
    append_message,
    get_pending_change,
    get_pending_question,
    open_db,
    resolve_pending_change,
)
from uja_host.sandbox import SandboxViolation, resolve_within_root
from uja_host.tools import skill_tools
from uja_host.tools.file_tools import ToolError


def _root() -> Path:
    root = host_config.get_project_root()
    if root is None:
        raise ToolError("project_root not configured")
    return root


# ---------------------------------------------------------------------------
# Outbound — propose_changes / ask_user (delegates to surviving primitives)
# ---------------------------------------------------------------------------


def propose_changes(
    changes: Optional[list] = None,
    summary: str = "",
    diff: Optional[str] = None,
) -> dict:
    """Persist a list of proposed file changes as a pending change-set.

    `changes` is a list of `{path, before?, after, delete?}` dicts.
    `before` is auto-populated from disk if omitted (or set to None for
    new-file proposals). The change-set is stored in SQLite under the
    most recent conversation; nothing lands on disk until
    `approve_changes` is called.

    Returns `{change_set_id, status: "pending", summary, files,
    next_step}`. Pause the agent loop after calling this — wait for the
    human's approve/reject decision before assuming the edit landed.
    """
    return skill_tools.propose_changes(
        _root(), changes=changes, summary=summary, diff=diff,
    )


def ask_user(question: str, options: Optional[list[str]] = None) -> dict:
    """Ask the human user a clarifying question; pause until they answer.

    Persists a pending question; the row id is returned. Use `options`
    for multiple-choice; omit for free-form text. Do NOT invent the
    answer — the next agent turn only resumes once the human responds.
    """
    return skill_tools.ask_user(_root(), question=question, options=options)


# ---------------------------------------------------------------------------
# Inbound — approve_changes / reject_changes / answer_question
# ---------------------------------------------------------------------------


def _apply_one_change(root: Path, edit: dict) -> dict:
    """Resolve and write a single change-set edit (sandbox-bounded).

    Mirrors host/uja_host/api/changes.py:_apply_one_change but raises
    ToolError instead of HTTPException so FastMCP can surface it
    cleanly.
    """
    rel_path = edit["path"]
    try:
        resolved = resolve_within_root(root, rel_path)
    except SandboxViolation as e:
        raise ToolError(f"sandbox: {rel_path}: {e}") from None

    if edit.get("delete"):
        if resolved.exists():
            resolved.unlink()
            return {"path": rel_path, "action": "deleted"}
        return {"path": rel_path, "action": "delete-noop (file did not exist)"}

    after = edit.get("after")
    if after is None:
        raise ToolError(f"change for {rel_path} has no `after` content")

    resolved.parent.mkdir(parents=True, exist_ok=True)
    is_new = not resolved.exists()
    resolved.write_text(after, encoding="utf-8")
    return {"path": rel_path, "action": "created" if is_new else "edited"}


def approve_changes(change_set_id: str) -> dict:
    """Apply a previously-proposed change-set through the sandbox.

    Idempotent against re-resolution: a non-pending row raises
    ToolError with the current status rather than re-applying. Each
    edit is sandbox-checked; a violation aborts the apply (partial
    writes from earlier edits in the same set are reflected in
    `paths_written`).

    On success, appends a synthesized user message to the conversation
    so the agent loop, on its next turn, sees that the change landed.
    """
    if not change_set_id:
        raise ToolError("`change_set_id` is required")
    root = _root()
    with open_db(root) as conn:
        change = get_pending_change(conn, change_set_id)
        if not change:
            raise ToolError(f"change_id not found: {change_set_id}")
        if change["status"] != "pending":
            raise ToolError(
                f"change-set already resolved (status={change['status']})"
            )

        paths_written: list[dict] = []
        for edit in change["changes"]:
            paths_written.append(_apply_one_change(root, edit))

        if not resolve_pending_change(conn, change_set_id, "applied"):
            raise ToolError("change-set status changed during apply")

        landed = ", ".join(f"{p['action']}: {p['path']}" for p in paths_written)
        append_message(
            conn,
            change["conversation_id"],
            "user",
            f"[user approved change-set {change_set_id}] {landed}",
        )

    return {
        "change_id": change_set_id,
        "status": "applied",
        "conversation_id": change["conversation_id"],
        "paths_written": paths_written,
        "count": len(paths_written),
    }


def reject_changes(change_set_id: str) -> dict:
    """Mark a change-set rejected; no files are written.

    Idempotent against re-resolution. Appends a synthesized user
    message reflecting the rejection so the agent loop can react on its
    next turn.
    """
    if not change_set_id:
        raise ToolError("`change_set_id` is required")
    root = _root()
    with open_db(root) as conn:
        change = get_pending_change(conn, change_set_id)
        if not change:
            raise ToolError(f"change_id not found: {change_set_id}")
        if change["status"] != "pending":
            raise ToolError(
                f"change-set already resolved (status={change['status']})"
            )
        if not resolve_pending_change(conn, change_set_id, "rejected"):
            raise ToolError("change-set status changed during reject")

        append_message(
            conn,
            change["conversation_id"],
            "user",
            f"[user rejected change-set {change_set_id}] no files were written; "
            f"adjust the proposal or proceed without these edits.",
        )

    return {
        "change_id": change_set_id,
        "status": "rejected",
        "conversation_id": change["conversation_id"],
    }


def answer_question(question_id: str, answer: str) -> dict:
    """Record an answer to a pending `ask_user` question.

    Idempotent against re-resolution. Appends a synthesized user
    message carrying the answer text so the agent loop, on its next
    turn, picks up the response.
    """
    if not question_id:
        raise ToolError("`question_id` is required")
    if not isinstance(answer, str) or not answer:
        raise ToolError("`answer` must be a non-empty string")

    root = _root()
    with open_db(root) as conn:
        question = get_pending_question(conn, question_id)
        if not question:
            raise ToolError(f"question_id not found: {question_id}")
        if question["status"] != "pending":
            raise ToolError(
                f"question already resolved (status={question['status']})"
            )

        if not answer_pending_question(conn, question_id, answer):
            raise ToolError("question status changed during answer")

        append_message(
            conn,
            question["conversation_id"],
            "user",
            f"[user answered question {question_id}] {answer}",
        )

    return {
        "question_id": question_id,
        "status": "answered",
        "conversation_id": question["conversation_id"],
    }
