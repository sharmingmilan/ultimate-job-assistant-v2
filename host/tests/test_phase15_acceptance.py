"""Phase 15 acceptance test (mocked Anthropic).

Proves end-to-end:
  1. POST /api/chat creates a conversation.
  2. The tool-use loop dispatches read_file + write_file against the project root.
  3. Files actually land on disk.
  4. After "restarting" the server (new TestClient), conversation history is restored from SQLite.

Run:
    cd host && python -m pytest tests/test_phase15_acceptance.py -v
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from uja_host import config as host_cfg, keystore
from uja_host.api import config as cfg_api  # noqa: F401  -- imported to take effect
from uja_host.main import create_app


def _redirect_home(tmp_home: Path):
    host_cfg.CONFIG_DIR = tmp_home / ".uja"
    host_cfg.CONFIG_FILE = host_cfg.CONFIG_DIR / "config.json"


def _block(type_, **kwargs):
    """Build a MagicMock that mimics an Anthropic content block."""
    m = MagicMock()
    m.type = type_
    for k, v in kwargs.items():
        setattr(m, k, v)
    if type_ == "tool_use":
        m.model_dump = lambda: {
            "type": "tool_use",
            "id": kwargs["id"],
            "name": kwargs["name"],
            "input": kwargs["input"],
        }
    elif type_ == "text":
        m.model_dump = lambda: {"type": "text", "text": kwargs["text"]}
    return m


def _mock_response(content_blocks, stop_reason="end_turn"):
    r = MagicMock()
    r.content = content_blocks
    r.stop_reason = stop_reason
    return r


def test_chat_round_trip_and_persistence(tmp_path: Path, monkeypatch):
    _redirect_home(tmp_path / "home")
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "README.md").write_text("Project README")

    keystore.set_api_key("sk-ant-test-" + "x" * 40)

    # Plan the model's behavior: turn 1 → tool_use (write HELLO.txt), turn 2 → final text
    fake_responses = iter([
        _mock_response(
            [_block("tool_use", id="tu_1", name="write_file",
                    input={"path": "HELLO.txt", "content": "Hello UJA"})],
            stop_reason="tool_use",
        ),
        _mock_response(
            [_block("text", text="Done. HELLO.txt is created.")],
            stop_reason="end_turn",
        ),
    ])

    fake_messages = MagicMock()
    fake_messages.create = MagicMock(side_effect=lambda **kw: next(fake_responses))
    fake_client = MagicMock()
    fake_client.messages = fake_messages

    app = create_app()
    client = TestClient(app)

    # Configure project root through the API (mirrors real flow)
    r = client.put("/api/config/project-root", json={"project_root": str(project_root)})
    assert r.status_code == 200, r.text

    with patch("uja_host.api.chat.anthropic.Anthropic", return_value=fake_client):
        r = client.post("/api/chat", json={"message": "Create HELLO.txt with content Hello UJA"})
        assert r.status_code == 200, r.text
        body = r.text

    # Should contain conversation id, a tool_use event, a tool_result event, and end_turn
    assert "event: conversation" in body
    assert "event: tool_use" in body
    assert "event: tool_result" in body
    assert "event: end_turn" in body, body

    # File should actually exist on disk
    assert (project_root / "HELLO.txt").read_text() == "Hello UJA"

    # Pull conversation_id from the SSE stream
    conv_id = None
    for line in body.splitlines():
        if line.startswith("data: ") and "conversation_id" in line:
            payload = json.loads(line[len("data: "):])
            conv_id = payload["conversation_id"]
            break
    assert conv_id

    # ----- "Restart" the server and verify persistence -----
    app2 = create_app()
    client2 = TestClient(app2)
    r2 = client2.get(f"/api/conversations/{conv_id}/messages")
    assert r2.status_code == 200, r2.text
    payload = r2.json()
    assert payload["count"] >= 3, payload  # user + assistant(tool_use) + user(tool_result) + assistant(text)
    roles = [m["role"] for m in payload["messages"]]
    assert roles[0] == "user"
    assert "assistant" in roles
    assert any(
        any(b.get("type") == "tool_use" for b in m["content"])
        for m in payload["messages"] if m["role"] == "assistant"
    ), "expected at least one assistant tool_use block in history"
