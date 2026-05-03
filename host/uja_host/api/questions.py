"""Phase 17.5 — pending-question answer endpoint.

The skill_tools.ask_user primitive persists pending questions in
SQLite. The chat loop yields a tool_use to the UI, the UI renders an
input card, and the user answers via this endpoint. The answer is
stored and a synthesized user message is appended to the conversation
so that when /api/chat is next invoked (with an empty message body to
resume), the agent reads the answer in history and continues.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from uja_host import config as host_config
from uja_host.db import (
    open_db,
    get_pending_question,
    answer_pending_question,
    append_message,
)

router = APIRouter(prefix="/api/questions", tags=["questions"])
log = logging.getLogger(__name__)


class AnswerBody(BaseModel):
    answer: str = Field(..., min_length=1, max_length=8000)


class AnswerResponse(BaseModel):
    question_id: str
    status: str
    conversation_id: str


def _require_root() -> Path:
    root = host_config.get_project_root()
    if root is None:
        raise HTTPException(status_code=409, detail="project_root not configured")
    return root


@router.post("/{question_id}/answer", response_model=AnswerResponse)
def answer_question(question_id: str, body: AnswerBody) -> AnswerResponse:
    root = _require_root()
    with open_db(root) as conn:
        question = get_pending_question(conn, question_id)
        if not question:
            raise HTTPException(status_code=404, detail="question_id not found")
        if question["status"] != "pending":
            raise HTTPException(
                status_code=409,
                detail=f"question already resolved (status={question['status']})",
            )

        if not answer_pending_question(conn, question_id, body.answer):
            raise HTTPException(status_code=409, detail="question status changed during answer")

        # Synthesize a user message carrying the answer text so the agent loop
        # picks it up on the next /api/chat invocation. We use a plain text
        # user message (not a tool_result block) because the original
        # ask_user tool_use already has its tool_result from chat.py's loop
        # ("status: pending"); a second tool_result for the same tool_use_id
        # would be invalid per the Anthropic API.
        append_message(
            conn,
            question["conversation_id"],
            "user",
            f"[user answered question {question_id}] {body.answer}",
        )

    return AnswerResponse(
        question_id=question_id,
        status="answered",
        conversation_id=question["conversation_id"],
    )
