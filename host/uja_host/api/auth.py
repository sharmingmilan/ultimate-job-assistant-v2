"""Demoted per ADR-002 D3.

API-key write endpoint. Kept for a possible future headless export mode
per ADR-002 §Phasing impact. Not registered on the default MCP tool
surface in v0.2.x. The legacy FastAPI surface still serves these routes
unchanged today; a future v0.2.x change is expected to make them return
410 Gone, but that gate is not yet implemented.

API key management. The actual key never leaves the OS keychain.
"""

from __future__ import annotations

import logging

import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from uja_host import keystore

router = APIRouter(prefix="/api/auth", tags=["auth"])
log = logging.getLogger(__name__)


class SetKeyRequest(BaseModel):
    api_key: str = Field(..., min_length=10)
    test_connection: bool = True


class KeyStatusResponse(BaseModel):
    has_key: bool
    using_memory_fallback: bool


class TestConnectionResponse(BaseModel):
    ok: bool
    error: str | None = None


@router.get("/key", response_model=KeyStatusResponse)
def get_key_status() -> KeyStatusResponse:
    return KeyStatusResponse(
        has_key=keystore.has_api_key(),
        using_memory_fallback=keystore.using_memory_fallback(),
    )


@router.put("/key", response_model=KeyStatusResponse)
def put_key(body: SetKeyRequest) -> KeyStatusResponse:
    try:
        keystore.set_api_key(body.api_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if body.test_connection:
        try:
            client = anthropic.Anthropic(api_key=body.api_key)
            client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=8,
                messages=[{"role": "user", "content": "ping"}],
            )
        except Exception as e:
            keystore.clear_api_key()
            log.warning("API key test failed; cleared key. %s", keystore.redact_secrets(str(e)))
            raise HTTPException(status_code=400, detail=f"test_connection failed: {type(e).__name__}")
    return KeyStatusResponse(
        has_key=keystore.has_api_key(),
        using_memory_fallback=keystore.using_memory_fallback(),
    )


@router.delete("/key", response_model=KeyStatusResponse)
def delete_key() -> KeyStatusResponse:
    keystore.clear_api_key()
    return KeyStatusResponse(has_key=False, using_memory_fallback=keystore.using_memory_fallback())
