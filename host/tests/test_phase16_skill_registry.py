"""Phase 16 skill registry + HITL primitives — through the MCP tool surface.

Re-pointed in Phase 23 (Session 11) per the brief. The original test
called `skill_tools.run_skill / propose_changes / ask_user` directly;
this version drives the MCP-tool wrappers in `host/uja_mcp/tools/`. The
contract is unchanged — the call site moves from
`uja_host.tools.skill_tools` to `uja_mcp.tools.skills` and
`uja_mcp.tools.hitl`. The Phase 16 `run_skill` primitive is split per
ADR-002 D1 into the two MCP-idiomatic tools `list_skills` / `read_skill`,
so the catalog/load shape changes; both halves are still tested.

Run:
    cd host && python -m pytest tests/test_phase16_skill_registry.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from uja_host import config as host_config
from uja_host.db import (
    answer_pending_question,
    create_conversation,
    get_pending_change,
    get_pending_question,
    open_db,
    resolve_pending_change,
)
from uja_host.tools import skill_registry
from uja_host.tools.file_tools import ToolError
from uja_mcp.tools import hitl as mcp_hitl
from uja_mcp.tools import skills as mcp_skills


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _write_skill(root: Path, name: str, description: str, body: str = "# body") -> Path:
    sd = root / "skills" / name
    sd.mkdir(parents=True, exist_ok=True)
    md = sd / "SKILL.md"
    md.write_text(
        f'---\nname: {name}\ndescription: "{description}"\n---\n\n{body}\n',
        encoding="utf-8",
    )
    return md


@pytest.fixture
def root_with_skills(tmp_path: Path, monkeypatch) -> Path:
    """Project root pre-populated with three skills + one non-skill folder.

    Monkeypatches `host_config.get_project_root` so MCP tool functions
    resolve the root from config (their normal contract) without
    touching ~/.uja/config.json.
    """
    _write_skill(tmp_path, "alpha", "alpha skill desc")
    _write_skill(tmp_path, "beta", "beta skill desc")
    _write_skill(tmp_path, "gamma", "gamma skill desc")
    # A non-skill folder that should be ignored
    (tmp_path / "skills" / "not-a-skill").mkdir()
    (tmp_path / "skills" / "not-a-skill" / "README.md").write_text("not a SKILL.md")
    # Hidden dir should be ignored
    hidden = tmp_path / "skills" / ".hidden"
    hidden.mkdir()

    monkeypatch.setattr(host_config, "get_project_root", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def conversation_id(root_with_skills: Path) -> str:
    """An active conversation so propose_changes / ask_user resolve."""
    with open_db(root_with_skills) as conn:
        return create_conversation(conn, title="phase16 mcp tests")


# ---------------------------------------------------------------------------
# skill_registry (unchanged — direct calls, not through MCP boundary)
# ---------------------------------------------------------------------------

def test_registry_list_skills_finds_only_dirs_with_skill_md(root_with_skills: Path):
    found = skill_registry.list_skills(root_with_skills)
    names = sorted(s.name for s in found)
    assert names == ["alpha", "beta", "gamma"]
    assert all("desc" in s.description for s in found)


def test_registry_list_skills_empty_when_no_skills_dir(tmp_path: Path):
    assert skill_registry.list_skills(tmp_path) == []


def test_registry_get_skill_by_name(root_with_skills: Path):
    s = skill_registry.get_skill(root_with_skills, "beta")
    assert s is not None
    assert s.name == "beta"
    assert "body" in s.content
    assert s.location.startswith("skills/beta")


def test_registry_get_skill_missing_returns_none(root_with_skills: Path):
    assert skill_registry.get_skill(root_with_skills, "nonexistent") is None


def test_frontmatter_parser_handles_quoted_and_unquoted():
    fm, body = skill_registry._parse_frontmatter(
        '---\nname: x\ndescription: "quoted desc"\nfoo: bar\n---\nbody here\n'
    )
    assert fm == {"name": "x", "description": "quoted desc", "foo": "bar"}
    assert body == "body here\n"


def test_frontmatter_parser_no_frontmatter_returns_empty():
    fm, body = skill_registry._parse_frontmatter("# no frontmatter\nbody\n")
    assert fm == {}
    assert body.startswith("# no frontmatter")


# ---------------------------------------------------------------------------
# MCP tool: list_skills + read_skill (the run_skill split per ADR-002 D1)
# ---------------------------------------------------------------------------

def test_mcp_list_skills_returns_catalog(root_with_skills: Path):
    result = mcp_skills.list_skills()
    assert result["count"] == 3
    names = sorted(s["name"] for s in result["skills"])
    assert names == ["alpha", "beta", "gamma"]
    # Each entry carries a description and a relative location
    for s in result["skills"]:
        assert s["description"]
        assert s["location"].startswith("skills/")


def test_mcp_read_skill_returns_full_content(root_with_skills: Path):
    result = mcp_skills.read_skill(name="alpha")
    assert result["name"] == "alpha"
    assert "body" in result["content"]
    assert result["location"].startswith("skills/alpha")


def test_mcp_read_skill_unknown_raises_tool_error(root_with_skills: Path):
    with pytest.raises(ToolError) as exc:
        mcp_skills.read_skill(name="ghost")
    assert "ghost" in str(exc.value)
    # Helper enumerates available skills for the agent's recovery
    assert "alpha" in str(exc.value) or "Available" in str(exc.value)


def test_mcp_read_skill_empty_name_raises(root_with_skills: Path):
    with pytest.raises(ToolError):
        mcp_skills.read_skill(name="")


# ---------------------------------------------------------------------------
# MCP tool: propose_changes
# ---------------------------------------------------------------------------

def test_mcp_propose_changes_persists_and_returns_id(
    root_with_skills: Path, conversation_id: str
):
    (root_with_skills / "existing.txt").write_text("hello", encoding="utf-8")

    result = mcp_hitl.propose_changes(
        changes=[
            {"path": "existing.txt", "after": "hello world"},
            {"path": "newdir/created.txt", "after": "fresh"},
        ],
        summary="add a new file and edit an old one",
    )
    assert result["status"] == "pending"
    assert "change_set_id" in result
    assert result["files"] == ["existing.txt", "newdir/created.txt"]

    with open_db(root_with_skills) as conn:
        row = get_pending_change(conn, result["change_set_id"])
    assert row is not None
    assert row["status"] == "pending"
    assert row["summary"] == "add a new file and edit an old one"
    assert len(row["changes"]) == 2
    assert row["changes"][0]["before"] == "hello"
    assert row["changes"][1]["before"] is None


def test_mcp_propose_changes_does_not_apply_to_disk(
    root_with_skills: Path, conversation_id: str
):
    (root_with_skills / "untouched.txt").write_text("original", encoding="utf-8")
    mcp_hitl.propose_changes(
        changes=[{"path": "untouched.txt", "after": "modified"}],
    )
    assert (root_with_skills / "untouched.txt").read_text() == "original"


def test_mcp_propose_changes_sandbox_violation_raises(
    root_with_skills: Path, conversation_id: str
):
    with pytest.raises(ToolError) as exc:
        mcp_hitl.propose_changes(
            changes=[{"path": "../escape.txt", "after": "nope"}],
        )
    assert "sandbox" in str(exc.value)


def test_mcp_propose_changes_resolve_lifecycle(
    root_with_skills: Path, conversation_id: str
):
    res = mcp_hitl.propose_changes(
        changes=[{"path": "x.txt", "after": "x"}],
    )
    cs_id = res["change_set_id"]

    with open_db(root_with_skills) as conn:
        assert resolve_pending_change(conn, cs_id, "approved") is True
        # Second resolve attempt is a no-op
        assert resolve_pending_change(conn, cs_id, "applied") is False
        row = get_pending_change(conn, cs_id)
    assert row["status"] == "approved"
    assert row["resolved_at"] is not None


def test_mcp_propose_changes_legacy_diff_string(
    root_with_skills: Path, conversation_id: str
):
    """Legacy callers passing a unified-diff string still work."""
    res = mcp_hitl.propose_changes(diff="--- a\n+++ b\n@@ ... @@\n")
    assert res["status"] == "pending"
    with open_db(root_with_skills) as conn:
        row = get_pending_change(conn, res["change_set_id"])
    assert row["changes"][0]["raw_diff"] is True


def test_mcp_propose_changes_rejects_empty(
    root_with_skills: Path, conversation_id: str
):
    with pytest.raises(ToolError):
        mcp_hitl.propose_changes(changes=[])


# ---------------------------------------------------------------------------
# MCP tool: ask_user
# ---------------------------------------------------------------------------

def test_mcp_ask_user_persists(root_with_skills: Path, conversation_id: str):
    res = mcp_hitl.ask_user(
        question="Did you mean A or B?",
        options=["A", "B"],
    )
    assert res["status"] == "pending"
    qid = res["question_id"]

    with open_db(root_with_skills) as conn:
        row = get_pending_question(conn, qid)
    assert row is not None
    assert row["question"] == "Did you mean A or B?"
    assert row["options"] == ["A", "B"]
    assert row["status"] == "pending"


def test_mcp_ask_user_answer_round_trip(
    root_with_skills: Path, conversation_id: str
):
    res = mcp_hitl.ask_user(question="pick one")
    qid = res["question_id"]
    with open_db(root_with_skills) as conn:
        assert answer_pending_question(conn, qid, "the answer")
        # Second answer is a no-op
        assert answer_pending_question(conn, qid, "again") is False
        row = get_pending_question(conn, qid)
    assert row["status"] == "answered"
    assert row["answer"] == "the answer"


def test_mcp_ask_user_rejects_empty_question(
    root_with_skills: Path, conversation_id: str
):
    with pytest.raises(ToolError):
        mcp_hitl.ask_user(question="   ")


def test_mcp_ask_user_rejects_bad_options(
    root_with_skills: Path, conversation_id: str
):
    with pytest.raises(ToolError):
        mcp_hitl.ask_user(question="q", options=[1, 2, 3])  # type: ignore[arg-type]
