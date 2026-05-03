"""POST /api/chat — streaming Claude chat with the host tool catalog.

Implements the agent loop in a single request: the user posts one
message, the server loops Anthropic API calls + tool execution until
stop_reason == 'end_turn'. Every event is streamed back as SSE so the
frontend can render incrementally. Every message and tool invocation
is persisted to SQLite so the conversation survives a restart.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Iterator

import anthropic
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from uja_host import config as host_config, keystore
from uja_host.db import (
    open_db, create_conversation, append_message, list_messages,
    append_tool_invocation, get_conversation,
)
from uja_host.tools import (
    ANTHROPIC_TOOL_DEFS, dispatch_tool, tool_result_content,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])
log = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_TOOL_ITERATIONS = 12  # generous; protects against runaway loops
SYSTEM_PROMPT = (
    "You are the agent inside Ultimate Job Assistant's local web app. "
    "You have file tools scoped to the user's project root. Use read_file, "
    "write_file, edit_file, list_files, and read_workspace_metadata to "
    "help the user manage their job-application materials. The skill "
    "tools (run_skill, propose_changes, ask_user) are not yet wired — they "
    "will return a not_implemented payload. Be concise."
)


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    message: str = Field(..., min_length=1)
    model: str | None = None


def _sse(event: str, data: Any) -> bytes:
    payload = data if isinstance(data, str) else json.dumps(data, default=str)
    return f"event: {event}\ndata: {payload}\n\n".encode("utf-8")


def _to_anthropic_messages(stored_msgs: list[dict]) -> list[dict]:
    """Convert SQLite-stored messages into Anthropic /v1/messages shape."""
    out: list[dict] = []
    for m in stored_msgs:
        if m["role"] in ("user", "assistant"):
            out.append({"role": m["role"], "content": m["content"]})
    return out


@router.post("")
def post_chat(body: ChatRequest):
    root = host_config.get_project_root()
    if root is None:
        raise HTTPException(status_code=409, detail="project_root not configured")
    api_key = keystore.get_api_key()
    if not api_key:
        raise HTTPException(status_code=409, detail="api_key not configured")

    model = body.model or DEFAULT_MODEL

    # Resolve / create conversation BEFORE streaming starts
    with open_db(root) as conn:
        if body.conversation_id:
            conv = get_conversation(conn, body.conversation_id)
            if not conv:
                raise HTTPException(status_code=404, detail="conversation_id not found")
            conv_id = body.conversation_id
        else:
            conv_id = create_conversation(conn, title=body.message[:60])
        # Persist user turn
        append_message(conn, conv_id, "user", body.message)

    def event_stream() -> Iterator[bytes]:
        try:
            yield _sse("conversation", {"conversation_id": conv_id})

            client = anthropic.Anthropic(api_key=api_key)

            for iteration in range(MAX_TOOL_ITERATIONS):
                with open_db(root) as conn:
                    history = _to_anthropic_messages(list_messages(conn, conv_id))

                yield _sse("iteration", {"n": iteration, "messages_so_far": len(history)})

                # Non-streaming call for v1 simplicity. Streaming-deltas can be
                # layered on top of this once the loop is proven.
                response = client.messages.create(
                    model=model,
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    tools=ANTHROPIC_TOOL_DEFS,
                    messages=history,
                )

                # Persist the assistant turn (full content blocks)
                content_blocks = [b.model_dump() for b in response.content]
                with open_db(root) as conn:
                    msg_id = append_message(conn, conv_id, "assistant", content_blocks)

                # Stream the assistant's text + tool_use plan to the client
                for block in response.content:
                    bt = block.type
                    if bt == "text":
                        yield _sse("text", {"text": block.text})
                    elif bt == "tool_use":
                        yield _sse("tool_use", {
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        })

                if response.stop_reason != "tool_use":
                    yield _sse("end_turn", {"stop_reason": response.stop_reason})
                    return

                # Execute every tool_use block; build a single user message
                # carrying every tool_result block.
                tool_results = []
                with open_db(root) as conn:
                    for block in response.content:
                        if block.type != "tool_use":
                            continue
                        result, is_err = dispatch_tool(root, block.name, block.input)
                        append_tool_invocation(
                            conn, conv_id, msg_id, block.name,
                            block.input, result, is_err,
                        )
                        yield _sse("tool_result", {
                            "tool_use_id": block.id,
                            "name": block.name,
                            "is_error": is_err,
                            "content": result,
                        })
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_result_content(result),
                            "is_error": is_err,
                        })
                    append_message(conn, conv_id, "user", tool_results)

            yield _sse("error", {
                "error": f"Hit MAX_TOOL_ITERATIONS={MAX_TOOL_ITERATIONS}; aborting loop.",
            })

        except anthropic.APIError as e:
            log.warning("anthropic API error: %s", keystore.redact_secrets(str(e)))
            yield _sse("error", {"error": f"anthropic_api_error: {type(e).__name__}"})
        except Exception as e:  # pragma: no cover — fence
            log.exception("chat stream crashed")
            yield _sse("error", {"error": f"server_error: {type(e).__name__}"})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
