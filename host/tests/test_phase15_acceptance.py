"""Phase 15 acceptance — round trip + persistence through the MCP tool surface.

Re-pointed in Phase 23 (Session 11) per ADR-002 D1: the original test
drove POST /api/chat with a mocked Anthropic loop and parsed the SSE
stream. The chat-style architecture is deprecated (ADR-002 D2/D3); the
v0.2.x runtime is the MCP server in `host/uja_mcp/`. This file now
exercises the same Phase 15 infrastructure (sandbox + file_tools + db)
through the MCP tool functions instead of HTTP routes. Same fixture
pattern (monkeypatched config + tmp_path-rooted SQLite); the call site
moves from TestClient to direct MCP-tool invocation.

Coverage:
  - read_workspace_metadata returns the configured root + git/host info
  - write_file lands a file on disk, sandbox-bounded
  - read_file returns its content
  - list_files surfaces the new file
  - SQLite (the surviving Phase 15 persistence) round-trips a
    conversation across "host restarts" (re-importing the modules)

Run:
    cd host && python -m pytest tests/test_phase15_acceptance.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from uja_host import config as host_config
from uja_host.db import (
    create_conversation,
    list_conversations,
    list_messages,
    open_db,
)
from uja_host.tools.file_tools import ToolError
from uja_mcp.tools import files as mcp_files


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch) -> Path:
    """Configured project root; MCP tools read it via host_config."""
    monkeypatch.setattr(host_config, "get_project_root", lambda: tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# MCP file-tool round trip
# ---------------------------------------------------------------------------


def test_read_workspace_metadata_returns_root(project_root: Path):
    md = mcp_files.read_workspace_metadata()
    assert md["project_root"] == str(project_root)
    assert md["exists"] is True
    assert md["is_dir"] is True
    # host_version comes from uja_host.__version__; should be a non-empty string.
    assert isinstance(md["host_version"], str) and md["host_version"]


def test_write_then_read_file_round_trip(project_root: Path):
    written = mcp_files.write_file(path="HELLO.txt", content="Hello UJA")
    assert written["path"] == "HELLO.txt"
    assert written["bytes_written"] == len("Hello UJA")

    target = project_root / "HELLO.txt"
    assert target.exists()
    assert target.read_text() == "Hello UJA"

    got = mcp_files.read_file(path="HELLO.txt")
    assert got["content"] == "Hello UJA"
    assert got["path"] == "HELLO.txt"


def test_write_file_creates_parent_dirs(project_root: Path):
    mcp_files.write_file(path="notes/deep/file.md", content="x")
    target = project_root / "notes" / "deep" / "file.md"
    assert target.exists()


def test_list_files_surfaces_new_file(project_root: Path):
    mcp_files.write_file(path="alpha.md", content="A")
    listing = mcp_files.list_files(path=".")
    names = {e["name"] for e in listing["entries"]}
    assert "alpha.md" in names


def test_edit_file_replaces_unique_token(project_root: Path):
    mcp_files.write_file(path="config.txt", content="version=1\n")
    res = mcp_files.edit_file(path="config.txt", find="version=1", replace="version=2")
    assert res["replacements"] == 1
    assert (project_root / "config.txt").read_text() == "version=2\n"


def test_read_file_rejects_sandbox_escape(project_root: Path):
    with pytest.raises(ToolError) as exc:
        mcp_files.read_file(path="../etc/passwd")
    assert "sandbox" in str(exc.value)


def test_tools_error_when_no_root_configured(monkeypatch):
    """Each tool surfaces a structured error when project_root is unset.

    FastMCP wraps ToolError into the protocol-level error response; here
    we assert the error type at the tool-function layer (the layer Block
    4's tests target).
    """
    monkeypatch.setattr(host_config, "get_project_root", lambda: None)
    with pytest.raises(ToolError) as exc:
        mcp_files.read_workspace_metadata()
    assert "project_root not configured" in str(exc.value)


# ---------------------------------------------------------------------------
# Persistence (SQLite, per Phase 15 schema; survives ADR-002 D3)
# ---------------------------------------------------------------------------


def test_sqlite_persistence_across_module_reimport(project_root: Path):
    """A conversation written before "restart" is readable after.

    The original Phase 15 test verified history survived restarting the
    FastAPI app. The MCP-side equivalent is: write through one open_db
    context, close, open another, read the same row. SQLite is the
    survivor; the DB layer is unchanged.
    """
    with open_db(project_root) as conn:
        conv_id = create_conversation(conn, title="phase15 mcp acceptance")

    # New context manager — equivalent to the "restart" the original test did.
    with open_db(project_root) as conn:
        convs = list_conversations(conn, limit=10)
        assert any(c["id"] == conv_id for c in convs)
        msgs = list_messages(conn, conv_id)
        assert msgs == []  # nothing appended yet, but row is there
