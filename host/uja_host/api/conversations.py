"""Conversation read endpoints (history, list, single)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from uja_host import config as host_config
from uja_host.db import (
    open_db, list_conversations, get_conversation, list_messages,
)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


def _require_root():
    root = host_config.get_project_root()
    if root is None:
        raise HTTPException(status_code=409, detail="project_root not configured")
    return root


@router.get("")
def list_all() -> dict[str, Any]:
    root = _require_root()
    with open_db(root) as conn:
        items = list_conversations(conn)
    return {"conversations": items, "count": len(items)}


@router.get("/{conv_id}")
def get_one(conv_id: str) -> dict[str, Any]:
    root = _require_root()
    with open_db(root) as conn:
        conv = get_conversation(conn, conv_id)
        if not conv:
            raise HTTPException(status_code=404, detail="conversation not found")
        msgs = list_messages(conn, conv_id)
    return {"conversation": conv, "messages": msgs}


@router.get("/{conv_id}/messages")
def get_messages(conv_id: str) -> dict[str, Any]:
    root = _require_root()
    with open_db(root) as conn:
        conv = get_conversation(conn, conv_id)
        if not conv:
            raise HTTPException(status_code=404, detail="conversation not found")
        msgs = list_messages(conn, conv_id)
    return {"conversation_id": conv_id, "messages": msgs, "count": len(msgs)}
