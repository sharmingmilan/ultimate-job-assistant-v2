"""Phase 17.5 HITL primitives — through the MCP tool surface.

Re-pointed in Phase 23 (Session 11) per the brief. The original test
drove the FastAPI routes (POST /api/changes/{id}/approve|reject and
POST /api/questions/{id}/answer) via fastapi.testclient. The chat-style
architecture is deprecated (ADR-002 D2/D3); the v0.2.x runtime is the
MCP server in `host/uja_mcp/`. This file calls the equivalent MCP tool
functions in `uja_mcp.tools.hitl` directly.

What changes from the original:
  - Call site: `client.post("/api/changes/<id>/approve")` →
    `mcp_hitl.approve_changes(change_set_id)`. Same for reject + answer.
  - Error contract: HTTPException(404/409/400) → ToolError raised by
    the tool function (FastMCP renders these as `is_error: true`
    structured payloads at the protocol layer; tested in
    test_mcp_server.py).
  - The two original `test_chat_*` tests at the bottom of the file
    drove the deprecated chat resume mode (POST /api/chat with empty
    body + conversation_id). The chat route has no MCP equivalent;
    those tests are dropped per ADR-002 D3 ("chat.py kept as deprecated
    reference, not maintained").

Run:
    cd host && python -m pytest tests/test_phase17_5.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from uja_host import config as host_config
from uja_host.db import (
    create_conversation,
    create_pending_change,
    create_pending_question,
    get_pending_change,
    get_pending_question,
    list_messages,
    open_db,
)
from uja_host.tools.file_tools import ToolError
from uja_mcp.tools import hitl as mcp_hitl


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch) -> Path:
    """Configured project root; MCP tools read it via host_config."""
    (tmp_path / "skills").mkdir()
    monkeypatch.setattr(host_config, "get_project_root", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def conv_id(project_root: Path) -> str:
    with open_db(project_root) as conn:
        return create_conversation(conn, title="phase17.5 mcp tests")


@pytest.fixture
def pending_change(project_root: Path, conv_id: str) -> str:
    """A pending change-set that creates one new file."""
    with open_db(project_root) as conn:
        return create_pending_change(
            conn,
            conversation_id=conv_id,
            tool_use_id=None,
            changes=[{
                "path": "notes/hello.md",
                "before": None,
                "after": "# Hello\n\nFrom the test.\n",
                "delete": False,
            }],
            summary="create notes/hello.md",
        )


@pytest.fixture
def pending_question(project_root: Path, conv_id: str) -> str:
    with open_db(project_root) as conn:
        return create_pending_question(
            conn,
            conversation_id=conv_id,
            tool_use_id=None,
            question="What is your favorite color?",
            options=None,
        )


# ---------------------------------------------------------------------------
# approve_changes
# ---------------------------------------------------------------------------


def test_approve_creates_new_file_inside_root(
    project_root: Path, pending_change: str, conv_id: str
):
    body = mcp_hitl.approve_changes(change_set_id=pending_change)
    assert body["status"] == "applied"
    assert body["count"] == 1
    assert body["paths_written"][0]["path"] == "notes/hello.md"
    assert body["paths_written"][0]["action"] == "created"

    # Disk side effect happened
    target = project_root / "notes" / "hello.md"
    assert target.exists()
    assert target.read_text() == "# Hello\n\nFrom the test.\n"

    # DB row marked applied
    with open_db(project_root) as conn:
        row = get_pending_change(conn, pending_change)
    assert row["status"] == "applied"
    assert row["resolved_at"] is not None

    # Synthesized user message appended to the conversation
    with open_db(project_root) as conn:
        msgs = list_messages(conn, conv_id)
    assert any(
        m["role"] == "user" and "approved change-set" in str(m["content"])
        for m in msgs
    ), f"no synthesized user message found; got: {msgs}"


def test_approve_overwrites_existing_file(
    project_root: Path, conv_id: str
):
    target = project_root / "config.txt"
    target.write_text("OLD")

    with open_db(project_root) as conn:
        change_id = create_pending_change(
            conn, conversation_id=conv_id, tool_use_id=None,
            changes=[{"path": "config.txt", "before": "OLD", "after": "NEW", "delete": False}],
            summary="overwrite config.txt",
        )

    body = mcp_hitl.approve_changes(change_set_id=change_id)
    assert body["paths_written"][0]["action"] == "edited"
    assert target.read_text() == "NEW"


def test_approve_handles_delete_for_existing_file(
    project_root: Path, conv_id: str
):
    target = project_root / "doomed.txt"
    target.write_text("bye")

    with open_db(project_root) as conn:
        change_id = create_pending_change(
            conn, conversation_id=conv_id, tool_use_id=None,
            changes=[{"path": "doomed.txt", "before": "bye", "after": None, "delete": True}],
            summary="delete doomed.txt",
        )

    body = mcp_hitl.approve_changes(change_set_id=change_id)
    assert body["paths_written"][0]["action"] == "deleted"
    assert not target.exists()


def test_approve_rejects_path_escape_via_sandbox(
    project_root: Path, conv_id: str
):
    # Stage a pending row with an escape-path. Bypass propose_changes
    # (which would reject this earlier) by inserting via the db helper.
    with open_db(project_root) as conn:
        change_id = create_pending_change(
            conn, conversation_id=conv_id, tool_use_id=None,
            changes=[{"path": "../../etc/passwd", "before": None, "after": "pwned", "delete": False}],
            summary="malicious",
        )

    with pytest.raises(ToolError) as exc:
        mcp_hitl.approve_changes(change_set_id=change_id)
    assert "sandbox" in str(exc.value).lower()


def test_approve_unknown_change_id_raises(project_root: Path):
    with pytest.raises(ToolError) as exc:
        mcp_hitl.approve_changes(change_set_id="does-not-exist")
    assert "not found" in str(exc.value)


def test_approve_double_apply_raises(
    project_root: Path, pending_change: str
):
    # First approve succeeds
    mcp_hitl.approve_changes(change_set_id=pending_change)
    # Second approve is rejected
    with pytest.raises(ToolError) as exc:
        mcp_hitl.approve_changes(change_set_id=pending_change)
    assert "applied" in str(exc.value)


# ---------------------------------------------------------------------------
# reject_changes
# ---------------------------------------------------------------------------


def test_reject_marks_row_without_disk_writes(
    project_root: Path, pending_change: str, conv_id: str
):
    body = mcp_hitl.reject_changes(change_set_id=pending_change)
    assert body["status"] == "rejected"

    # File should NOT exist
    assert not (project_root / "notes" / "hello.md").exists()

    # DB row marked rejected
    with open_db(project_root) as conn:
        row = get_pending_change(conn, pending_change)
    assert row["status"] == "rejected"

    # Synthesized user message reflects the rejection
    with open_db(project_root) as conn:
        msgs = list_messages(conn, conv_id)
    assert any(
        m["role"] == "user" and "rejected change-set" in str(m["content"])
        for m in msgs
    )


def test_reject_unknown_change_id_raises(project_root: Path):
    with pytest.raises(ToolError) as exc:
        mcp_hitl.reject_changes(change_set_id="nope")
    assert "not found" in str(exc.value)


def test_reject_then_approve_raises(
    project_root: Path, pending_change: str
):
    mcp_hitl.reject_changes(change_set_id=pending_change)
    with pytest.raises(ToolError) as exc:
        mcp_hitl.approve_changes(change_set_id=pending_change)
    assert "rejected" in str(exc.value)


# ---------------------------------------------------------------------------
# answer_question
# ---------------------------------------------------------------------------


def test_answer_records_and_synthesizes_user_message(
    project_root: Path, pending_question: str, conv_id: str
):
    body = mcp_hitl.answer_question(question_id=pending_question, answer="Periwinkle")
    assert body["status"] == "answered"
    assert body["conversation_id"] == conv_id

    # DB row updated
    with open_db(project_root) as conn:
        q = get_pending_question(conn, pending_question)
    assert q["status"] == "answered"
    assert q["answer"] == "Periwinkle"

    # Synthesized user message present
    with open_db(project_root) as conn:
        msgs = list_messages(conn, conv_id)
    assert any(
        m["role"] == "user" and "Periwinkle" in str(m["content"])
        for m in msgs
    )


def test_answer_unknown_question_raises(project_root: Path):
    with pytest.raises(ToolError) as exc:
        mcp_hitl.answer_question(question_id="nope", answer="anything")
    assert "not found" in str(exc.value)


def test_answer_double_answer_raises(
    project_root: Path, pending_question: str
):
    mcp_hitl.answer_question(question_id=pending_question, answer="first")
    with pytest.raises(ToolError) as exc:
        mcp_hitl.answer_question(question_id=pending_question, answer="second")
    assert "answered" in str(exc.value)


def test_answer_rejects_empty(
    project_root: Path, pending_question: str
):
    with pytest.raises(ToolError):
        mcp_hitl.answer_question(question_id=pending_question, answer="")
