"""Phase 17.5 unit tests — change-set approve/reject + question answer.

Exercises:
  - POST /api/changes/{id}/approve — applies edits, sandbox bounds, idempotency
  - POST /api/changes/{id}/reject — no disk writes, idempotency
  - POST /api/questions/{id}/answer — records answer, synthesizes user msg
  - POST /api/chat resume mode — empty body allowed when conversation_id set

Run:
    cd host && python -m pytest tests/test_phase17_5.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from uja_host import config as host_config
from uja_host.db import (
    open_db,
    create_conversation,
    create_pending_change,
    create_pending_question,
    get_pending_change,
    get_pending_question,
    list_messages,
)
from uja_host.main import create_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch) -> Path:
    """Configured project root for the host. Patches the global config so
    /api/* endpoints find a root without relying on ~/.uja/config.json."""
    (tmp_path / "skills").mkdir()  # silence skill registry warnings if any
    monkeypatch.setattr(host_config, "get_project_root", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def client(project_root: Path) -> TestClient:
    app = create_app()
    return TestClient(app)


@pytest.fixture
def conv_id(project_root: Path) -> str:
    with open_db(project_root) as conn:
        return create_conversation(conn, title="phase17.5 tests")


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
# POST /api/changes/{id}/approve
# ---------------------------------------------------------------------------


def test_approve_creates_new_file_inside_root(
    client: TestClient, project_root: Path, pending_change: str, conv_id: str
):
    r = client.post(f"/api/changes/{pending_change}/approve")
    assert r.status_code == 200, r.text
    body = r.json()
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
    client: TestClient, project_root: Path, conv_id: str
):
    target = project_root / "config.txt"
    target.write_text("OLD")

    with open_db(project_root) as conn:
        change_id = create_pending_change(
            conn, conversation_id=conv_id, tool_use_id=None,
            changes=[{"path": "config.txt", "before": "OLD", "after": "NEW", "delete": False}],
            summary="overwrite config.txt",
        )

    r = client.post(f"/api/changes/{change_id}/approve")
    assert r.status_code == 200
    assert r.json()["paths_written"][0]["action"] == "edited"
    assert target.read_text() == "NEW"


def test_approve_handles_delete_for_existing_file(
    client: TestClient, project_root: Path, conv_id: str
):
    target = project_root / "doomed.txt"
    target.write_text("bye")

    with open_db(project_root) as conn:
        change_id = create_pending_change(
            conn, conversation_id=conv_id, tool_use_id=None,
            changes=[{"path": "doomed.txt", "before": "bye", "after": None, "delete": True}],
            summary="delete doomed.txt",
        )

    r = client.post(f"/api/changes/{change_id}/approve")
    assert r.status_code == 200
    assert r.json()["paths_written"][0]["action"] == "deleted"
    assert not target.exists()


def test_approve_rejects_path_escape_via_sandbox(
    client: TestClient, project_root: Path, conv_id: str
):
    # Stage a pending row with an escape-path. We bypass propose_changes (which
    # would reject this earlier) by inserting directly via the db helper.
    with open_db(project_root) as conn:
        change_id = create_pending_change(
            conn, conversation_id=conv_id, tool_use_id=None,
            changes=[{"path": "../../etc/passwd", "before": None, "after": "pwned", "delete": False}],
            summary="malicious",
        )

    r = client.post(f"/api/changes/{change_id}/approve")
    assert r.status_code == 400
    assert "sandbox" in r.text.lower()


def test_approve_404_for_unknown_change_id(client: TestClient, project_root: Path):
    r = client.post("/api/changes/does-not-exist/approve")
    assert r.status_code == 404


def test_approve_409_when_already_applied(
    client: TestClient, project_root: Path, pending_change: str
):
    # First approve succeeds
    r1 = client.post(f"/api/changes/{pending_change}/approve")
    assert r1.status_code == 200
    # Second approve should 409
    r2 = client.post(f"/api/changes/{pending_change}/approve")
    assert r2.status_code == 409
    assert "applied" in r2.text


# ---------------------------------------------------------------------------
# POST /api/changes/{id}/reject
# ---------------------------------------------------------------------------


def test_reject_marks_row_without_disk_writes(
    client: TestClient, project_root: Path, pending_change: str, conv_id: str
):
    r = client.post(f"/api/changes/{pending_change}/reject")
    assert r.status_code == 200
    body = r.json()
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


def test_reject_404_for_unknown_change_id(client: TestClient):
    r = client.post("/api/changes/nope/reject")
    assert r.status_code == 404


def test_reject_409_when_already_resolved(
    client: TestClient, project_root: Path, pending_change: str
):
    client.post(f"/api/changes/{pending_change}/reject")
    r = client.post(f"/api/changes/{pending_change}/approve")
    assert r.status_code == 409


# ---------------------------------------------------------------------------
# POST /api/questions/{id}/answer
# ---------------------------------------------------------------------------


def test_answer_records_and_synthesizes_user_message(
    client: TestClient, project_root: Path, pending_question: str, conv_id: str
):
    r = client.post(f"/api/questions/{pending_question}/answer", json={"answer": "Periwinkle"})
    assert r.status_code == 200, r.text
    body = r.json()
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


def test_answer_404_for_unknown_question(client: TestClient):
    r = client.post("/api/questions/nope/answer", json={"answer": "anything"})
    assert r.status_code == 404


def test_answer_409_when_already_answered(
    client: TestClient, pending_question: str
):
    client.post(f"/api/questions/{pending_question}/answer", json={"answer": "first"})
    r = client.post(f"/api/questions/{pending_question}/answer", json={"answer": "second"})
    assert r.status_code == 409


def test_answer_422_on_empty_body(client: TestClient, pending_question: str):
    r = client.post(f"/api/questions/{pending_question}/answer", json={"answer": ""})
    assert r.status_code == 422  # pydantic min_length=1 violation


# ---------------------------------------------------------------------------
# POST /api/chat — resume mode (empty message on existing conv allowed)
# ---------------------------------------------------------------------------


def test_chat_rejects_empty_message_for_new_conversation(
    client: TestClient, project_root: Path
):
    """No conversation_id + empty message is still 400 (or 409 if no API key)
    — the empty-message path is ONLY for resume on an existing conv."""
    # Need an API key configured for the request to even reach the validation
    # we care about. Patch the keystore lookup so chat.py doesn't 409 on auth.
    with patch("uja_host.api.chat.keystore.get_api_key", return_value="sk-ant-test"):
        r = client.post("/api/chat", json={"message": ""})
    # Either 400 (our new explicit reject) or 422 (pydantic) is fine — both
    # signal the request is malformed for resume-without-conv.
    assert r.status_code in (400, 422), r.text


def test_chat_accepts_empty_message_for_existing_conversation(
    client: TestClient, project_root: Path, conv_id: str
):
    """Empty message + existing conv_id should pass the validation gate. The
    request will still 502/raise once it tries to call Anthropic (we have no
    real key), but the GATE we care about — body validation + conv lookup —
    must succeed."""
    with patch("uja_host.api.chat.keystore.get_api_key", return_value="sk-ant-test"):
        r = client.post("/api/chat", json={"message": "", "conversation_id": conv_id})
    # 200 means the streaming response started (subsequent failure would be in
    # the stream body). A 4xx means the request was rejected at the gate.
    # We accept 200 here as proof the empty-message + conv_id path is allowed.
    assert r.status_code == 200, f"empty-resume request was rejected: {r.status_code} {r.text}"
