"""MCP-protocol tests — `tools/list` + `tools/call` shape, error contract.

Phase 23 net-new tests covering the FastMCP-registered tool surface
(ADR-002 D1). Earlier tests (`test_phase15_acceptance.py`,
`test_phase16_skill_registry.py`, `test_phase17_5.py`) call the tool
functions directly. This file drives them through the registered
`FastMCP` instance — the same path Cowork hits over JSON-RPC stdio —
so we know the schema generation, annotations, and protocol-level
error wrapping all work.

What's covered:
  - `list_tools()` registers all 12 tools from ADR-002 D1.
  - Each tool carries the expected `ToolAnnotations`.
  - Each tool has a generated input schema reflecting its signature.
  - A happy-path file tool call returns a `CallToolResult` with
    `isError=False` and a JSON-encoded TextContent.
  - A bad-args call returns `isError=True` (FastMCP wraps Pydantic
    validation errors at the protocol layer).
  - A ToolError raised by tool logic surfaces as `isError=True`
    (verified for an unconfigured project root).
  - HITL round-trip through the protocol layer:
    `propose_changes` → `approve_changes`.

Run:
    cd host && python -m pytest tests/test_mcp_server.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolRequest, CallToolRequestParams

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from uja_host import config as host_config
from uja_host.db import create_conversation, open_db
from uja_mcp.server import build_server


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch) -> Path:
    """Project root with a couple of test fixtures."""
    (tmp_path / "skills").mkdir()
    monkeypatch.setattr(host_config, "get_project_root", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def server(project_root: Path) -> FastMCP:
    return build_server()


async def _call_tool_via_protocol(server: FastMCP, name: str, arguments: dict):
    """Drive a CallToolRequest through the underlying MCP server's handler.

    Uses the protocol-layer entry point so we exercise the FastMCP
    error-wrapping behavior (ToolError → isError=True). FastMCP's
    public `call_tool()` raises the underlying exception; the protocol
    handler is the path Cowork actually hits.
    """
    handler = server._mcp_server.request_handlers[CallToolRequest]
    req = CallToolRequest(
        method="tools/call",
        params=CallToolRequestParams(name=name, arguments=arguments),
    )
    return await handler(req)


# ---------------------------------------------------------------------------
# tools/list registration + shape
# ---------------------------------------------------------------------------


EXPECTED_TOOL_NAMES = {
    # Files (5)
    "read_file", "write_file", "edit_file", "list_files",
    "read_workspace_metadata",
    # Skills (2)
    "list_skills", "read_skill",
    # HITL (5)
    "propose_changes", "approve_changes", "reject_changes",
    "ask_user", "answer_question",
}


@pytest.mark.anyio
async def test_list_tools_registers_full_d1_surface(server: FastMCP):
    tools = await server.list_tools()
    names = {t.name for t in tools}
    assert names == EXPECTED_TOOL_NAMES, (
        f"missing: {EXPECTED_TOOL_NAMES - names}; "
        f"extra: {names - EXPECTED_TOOL_NAMES}"
    )
    assert len(tools) == 12, "ADR-002 D1 specifies 12 tools (export deferred to Phase 24)"


@pytest.mark.anyio
async def test_list_tools_carry_titles_and_annotations(server: FastMCP):
    tools = {t.name: t for t in await server.list_tools()}

    # Read tools should be readOnly=True.
    for ro_name in ("read_file", "list_files", "read_workspace_metadata",
                    "list_skills", "read_skill"):
        ann = tools[ro_name].annotations
        assert ann is not None, f"{ro_name} missing annotations"
        assert ann.readOnlyHint is True, f"{ro_name} should be readOnlyHint=True"
        assert ann.title, f"{ro_name} missing title"

    # Mutating tools should be readOnly=False.
    for mut_name in ("write_file", "edit_file", "approve_changes", "answer_question"):
        ann = tools[mut_name].annotations
        assert ann is not None
        assert ann.readOnlyHint is False, f"{mut_name} should be readOnlyHint=False"


@pytest.mark.anyio
async def test_list_tools_input_schemas_reflect_signatures(server: FastMCP):
    tools = {t.name: t for t in await server.list_tools()}

    rf = tools["read_file"].inputSchema
    assert "path" in rf["properties"]
    assert rf["required"] == ["path"]

    wf = tools["write_file"].inputSchema
    assert set(wf["required"]) == {"path", "content"}

    ef = tools["edit_file"].inputSchema
    assert set(ef["required"]) == {"path", "find", "replace"}


# ---------------------------------------------------------------------------
# tools/call — happy path
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_call_read_workspace_metadata_returns_text_content(
    server: FastMCP, project_root: Path
):
    result = await _call_tool_via_protocol(server, "read_workspace_metadata", {})
    payload = result.root
    assert payload.isError is False, payload.content
    assert payload.content, "expected at least one content block"
    text = payload.content[0].text
    parsed = json.loads(text)
    assert parsed["project_root"] == str(project_root)


@pytest.mark.anyio
async def test_call_write_file_round_trip_through_protocol(
    server: FastMCP, project_root: Path
):
    await _call_tool_via_protocol(
        server, "write_file", {"path": "GREETING.md", "content": "Hello via MCP"}
    )
    assert (project_root / "GREETING.md").read_text() == "Hello via MCP"

    read = await _call_tool_via_protocol(
        server, "read_file", {"path": "GREETING.md"}
    )
    parsed = json.loads(read.root.content[0].text)
    assert parsed["content"] == "Hello via MCP"


# ---------------------------------------------------------------------------
# tools/call — error contract (isError=True at protocol layer)
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_call_read_file_missing_required_arg_is_protocol_error(server: FastMCP):
    """Missing required arg → Pydantic validation → isError=True payload."""
    result = await _call_tool_via_protocol(server, "read_file", {})
    payload = result.root
    assert payload.isError is True, "expected isError=True for missing arg"
    assert payload.content
    assert "path" in payload.content[0].text.lower()


@pytest.mark.anyio
async def test_call_unknown_tool_is_protocol_error(server: FastMCP):
    result = await _call_tool_via_protocol(server, "nonexistent_tool", {})
    payload = result.root
    assert payload.isError is True


@pytest.mark.anyio
async def test_call_propagates_tool_error_for_unconfigured_root(
    monkeypatch, project_root: Path
):
    """ToolError raised by tool logic → isError=True at the protocol layer."""
    server = build_server()
    monkeypatch.setattr(host_config, "get_project_root", lambda: None)
    result = await _call_tool_via_protocol(server, "read_workspace_metadata", {})
    payload = result.root
    assert payload.isError is True
    assert "project_root not configured" in payload.content[0].text


# ---------------------------------------------------------------------------
# HITL round trip through protocol layer
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_hitl_round_trip_propose_then_approve(
    server: FastMCP, project_root: Path
):
    # propose_changes needs an active conversation
    with open_db(project_root) as conn:
        create_conversation(conn, title="mcp protocol test")

    proposed = await _call_tool_via_protocol(
        server,
        "propose_changes",
        {
            "changes": [{"path": "PROPOSED.md", "after": "draft"}],
            "summary": "create PROPOSED.md",
        },
    )
    p_payload = proposed.root
    assert p_payload.isError is False, p_payload.content
    p_parsed = json.loads(p_payload.content[0].text)
    cs_id = p_parsed["change_set_id"]
    assert p_parsed["status"] == "pending"
    # No disk side effect yet
    assert not (project_root / "PROPOSED.md").exists()

    approved = await _call_tool_via_protocol(
        server, "approve_changes", {"change_set_id": cs_id}
    )
    a_payload = approved.root
    assert a_payload.isError is False, a_payload.content
    a_parsed = json.loads(a_payload.content[0].text)
    assert a_parsed["status"] == "applied"
    assert (project_root / "PROPOSED.md").read_text() == "draft"


# ---------------------------------------------------------------------------
# anyio backend selection (FastMCP uses anyio under the hood)
# ---------------------------------------------------------------------------


@pytest.fixture
def anyio_backend():
    return "asyncio"
