"""Phase 17.5 — change-set approve / reject endpoints.

The skill_tools.propose_changes primitive persists pending change-sets
in SQLite (no disk writes). The chat loop yields a tool_use to the UI,
the UI renders the diff, and the user approves or rejects via these
endpoints. Approval applies every edit through the sandbox helper;
rejection just marks the row resolved with no disk side effects.

Both endpoints are idempotent against re-resolution: a non-pending
row returns 409 Conflict rather than re-applying.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from uja_host import config as host_config
from uja_host.db import (
    open_db,
    get_pending_change,
    resolve_pending_change,
    append_message,
)
from uja_host.sandbox import resolve_within_root, SandboxViolation

router = APIRouter(prefix="/api/changes", tags=["changes"])
log = logging.getLogger(__name__)


class ApproveResponse(BaseModel):
    change_id: str
    status: str
    conversation_id: str
    paths_written: list[dict]
    count: int


class RejectResponse(BaseModel):
    change_id: str
    status: str
    conversation_id: str


def _require_root() -> Path:
    root = host_config.get_project_root()
    if root is None:
        raise HTTPException(status_code=409, detail="project_root not configured")
    return root


def _apply_one_change(root: Path, edit: dict) -> dict:
    """Resolve + write a single change-set edit. Returns a record of what landed."""
    rel_path = edit["path"]
    try:
        resolved = resolve_within_root(root, rel_path)
    except SandboxViolation as e:
        # Sandbox violation here is a programming-or-attack signal. Surface as 400.
        raise HTTPException(status_code=400, detail=f"sandbox: {rel_path}: {e}") from None

    if edit.get("delete"):
        if resolved.exists():
            resolved.unlink()
            return {"path": rel_path, "action": "deleted"}
        return {"path": rel_path, "action": "delete-noop (file did not exist)"}

    after = edit.get("after")
    if after is None:
        # Defensive: should never happen since propose_changes._normalize_changes
        # rejects this case before it ever reaches the DB.
        raise HTTPException(status_code=400, detail=f"change for {rel_path} has no `after` content")

    resolved.parent.mkdir(parents=True, exist_ok=True)
    is_new = not resolved.exists()
    resolved.write_text(after, encoding="utf-8")
    return {"path": rel_path, "action": "created" if is_new else "edited"}


@router.post("/{change_id}/approve", response_model=ApproveResponse)
def approve_change(change_id: str) -> ApproveResponse:
    root = _require_root()
    with open_db(root) as conn:
        change = get_pending_change(conn, change_id)
        if not change:
            raise HTTPException(status_code=404, detail="change_id not found")
        if change["status"] != "pending":
            raise HTTPException(
                status_code=409,
                detail=f"change-set already resolved (status={change['status']})",
            )

        # Apply each edit. If any fails mid-stream the DB row stays pending —
        # acceptable for v1; partial-writes are surfaced via paths_written.
        paths_written: list[dict] = []
        for edit in change["changes"]:
            paths_written.append(_apply_one_change(root, edit))

        if not resolve_pending_change(conn, change_id, "applied"):
            # Lost a race with another approve/reject. Surface so the UI knows.
            raise HTTPException(status_code=409, detail="change-set status changed during apply")

        # Synthesize a user message so the agent loop, when next called with
        # an empty message body, sees that the change-set landed and can react.
        # Per Anthropic's API, multiple tool_results for the same tool_use_id
        # are invalid, so we use a plain text user message rather than another
        # tool_result block. The original tool_result (which said "pending") is
        # already in history from chat.py's loop.
        landed = ", ".join(f"{p['action']}: {p['path']}" for p in paths_written)
        append_message(
            conn,
            change["conversation_id"],
            "user",
            f"[user approved change-set {change_id}] {landed}",
        )

    return ApproveResponse(
        change_id=change_id,
        status="applied",
        conversation_id=change["conversation_id"],
        paths_written=paths_written,
        count=len(paths_written),
    )


@router.post("/{change_id}/reject", response_model=RejectResponse)
def reject_change(change_id: str) -> RejectResponse:
    root = _require_root()
    with open_db(root) as conn:
        change = get_pending_change(conn, change_id)
        if not change:
            raise HTTPException(status_code=404, detail="change_id not found")
        if change["status"] != "pending":
            raise HTTPException(
                status_code=409,
                detail=f"change-set already resolved (status={change['status']})",
            )
        if not resolve_pending_change(conn, change_id, "rejected"):
            raise HTTPException(status_code=409, detail="change-set status changed during reject")

        append_message(
            conn,
            change["conversation_id"],
            "user",
            f"[user rejected change-set {change_id}] no files were written; "
            f"adjust the proposal or proceed without these edits.",
        )

    return RejectResponse(
        change_id=change_id,
        status="rejected",
        conversation_id=change["conversation_id"],
    )
