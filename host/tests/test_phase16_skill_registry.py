"""Phase 16 unit tests — skill discovery and the three skill tools.

Run:
    cd host && python -m pytest tests/test_phase16_skill_registry.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from uja_host.tools import skill_registry, skill_tools, dispatch_tool
from uja_host.tools.file_tools import ToolError
from uja_host.db import (
    open_db, create_conversation,
    get_pending_change, list_pending_changes, resolve_pending_change,
    get_pending_question, list_pending_questions, answer_pending_question,
)


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
def root_with_skills(tmp_path: Path) -> Path:
    _write_skill(tmp_path, "alpha", "alpha skill desc")
    _write_skill(tmp_path, "beta", "beta skill desc")
    _write_skill(tmp_path, "gamma", "gamma skill desc")
    # A non-skill folder that should be ignored
    (tmp_path / "skills" / "not-a-skill").mkdir()
    (tmp_path / "skills" / "not-a-skill" / "README.md").write_text("not a SKILL.md")
    # Hidden dir should be ignored
    hidden = tmp_path / "skills" / ".hidden"
    hidden.mkdir()
    return tmp_path


@pytest.fixture
def conversation_id(root_with_skills: Path) -> str:
    """Set up an active conversation so propose_changes / ask_user resolve."""
    with open_db(root_with_skills) as conn:
        return create_conversation(conn, title="phase16 tests")


# ---------------------------------------------------------------------------
# skill_registry
# ---------------------------------------------------------------------------

def test_list_skills_finds_only_dirs_with_skill_md(root_with_skills: Path):
    skills = skill_registry.list_skills(root_with_skills)
    names = sorted(s.name for s in skills)
    assert names == ["alpha", "beta", "gamma"]
    assert all("desc" in s.description for s in skills)


def test_list_skills_empty_when_no_skills_dir(tmp_path: Path):
    assert skill_registry.list_skills(tmp_path) == []


def test_get_skill_by_name(root_with_skills: Path):
    s = skill_registry.get_skill(root_with_skills, "beta")
    assert s is not None
    assert s.name == "beta"
    assert "body" in s.content
    assert s.location.startswith("skills/beta")


def test_get_skill_missing_returns_none(root_with_skills: Path):
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
# run_skill
# ---------------------------------------------------------------------------

def test_run_skill_catalog_mode(root_with_skills: Path):
    result = skill_tools.run_skill(root_with_skills)
    assert result["mode"] == "catalog"
    assert result["count"] == 3
    names = sorted(s["name"] for s in result["skills"])
    assert names == ["alpha", "beta", "gamma"]


def test_run_skill_load_mode(root_with_skills: Path):
    result = skill_tools.run_skill(root_with_skills, name="alpha", inputs={"foo": "bar"})
    assert result["mode"] == "load"
    assert result["skill"]["name"] == "alpha"
    assert "body" in result["skill"]["content"]
    assert result["inputs"] == {"foo": "bar"}


def test_run_skill_unknown_raises(root_with_skills: Path):
    with pytest.raises(ToolError) as exc:
        skill_tools.run_skill(root_with_skills, name="ghost")
    assert "ghost" in str(exc.value)


def test_run_skill_via_dispatcher_returns_is_error_for_unknown(root_with_skills: Path):
    """The dispatch layer should surface ToolError as is_error=True, not crash."""
    result, is_err = dispatch_tool(root_with_skills, "run_skill", {"name": "ghost"})
    assert is_err is True
    assert "ghost" in result["error"]


# ---------------------------------------------------------------------------
# propose_changes
# ---------------------------------------------------------------------------

def test_propose_changes_persists_and_returns_id(
    root_with_skills: Path, conversation_id: str
):
    # Existing file we'll edit + a new file we'll create
    (root_with_skills / "existing.txt").write_text("hello", encoding="utf-8")

    result = skill_tools.propose_changes(
        root_with_skills,
        changes=[
            {"path": "existing.txt", "after": "hello world"},
            {"path": "newdir/created.txt", "after": "fresh"},
        ],
        summary="add a new file and edit an old one",
    )
    assert result["status"] == "pending"
    assert "change_set_id" in result
    assert result["files"] == ["existing.txt", "newdir/created.txt"]

    # Round-trip through SQLite
    with open_db(root_with_skills) as conn:
        row = get_pending_change(conn, result["change_set_id"])
    assert row is not None
    assert row["status"] == "pending"
    assert row["summary"] == "add a new file and edit an old one"
    assert len(row["changes"]) == 2
    # `before` populated from disk for the existing file
    assert row["changes"][0]["before"] == "hello"
    # New-file proposal has before=None
    assert row["changes"][1]["before"] is None


def test_propose_changes_does_not_apply_to_disk(
    root_with_skills: Path, conversation_id: str
):
    (root_with_skills / "untouched.txt").write_text("original", encoding="utf-8")
    skill_tools.propose_changes(
        root_with_skills,
        changes=[{"path": "untouched.txt", "after": "modified"}],
    )
    # File on disk must be unchanged
    assert (root_with_skills / "untouched.txt").read_text() == "original"


def test_propose_changes_sandbox_violation_raises(
    root_with_skills: Path, conversation_id: str
):
    with pytest.raises(ToolError) as exc:
        skill_tools.propose_changes(
            root_with_skills,
            changes=[{"path": "../escape.txt", "after": "nope"}],
        )
    assert "sandbox" in str(exc.value)


def test_propose_changes_resolve_lifecycle(
    root_with_skills: Path, conversation_id: str
):
    res = skill_tools.propose_changes(
        root_with_skills,
        changes=[{"path": "x.txt", "after": "x"}],
    )
    cs_id = res["change_set_id"]

    with open_db(root_with_skills) as conn:
        assert resolve_pending_change(conn, cs_id, "approved") is True
        # Second resolve attempt is a no-op (status already left 'pending')
        assert resolve_pending_change(conn, cs_id, "applied") is False
        row = get_pending_change(conn, cs_id)
    assert row["status"] == "approved"
    assert row["resolved_at"] is not None


def test_propose_changes_legacy_diff_string(
    root_with_skills: Path, conversation_id: str
):
    """Legacy callers passing a unified-diff string still work."""
    res = skill_tools.propose_changes(
        root_with_skills,
        diff="--- a\n+++ b\n@@ ... @@\n",
    )
    assert res["status"] == "pending"
    with open_db(root_with_skills) as conn:
        row = get_pending_change(conn, res["change_set_id"])
    assert row["changes"][0]["raw_diff"] is True


def test_propose_changes_rejects_empty(root_with_skills: Path, conversation_id: str):
    with pytest.raises(ToolError):
        skill_tools.propose_changes(root_with_skills, changes=[])


# ---------------------------------------------------------------------------
# ask_user
# ---------------------------------------------------------------------------

def test_ask_user_persists(root_with_skills: Path, conversation_id: str):
    res = skill_tools.ask_user(
        root_with_skills,
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


def test_ask_user_answer_round_trip(root_with_skills: Path, conversation_id: str):
    res = skill_tools.ask_user(root_with_skills, question="pick one")
    qid = res["question_id"]
    with open_db(root_with_skills) as conn:
        assert answer_pending_question(conn, qid, "the answer")
        # Second answer is a no-op (status already left 'pending')
        assert answer_pending_question(conn, qid, "again") is False
        row = get_pending_question(conn, qid)
    assert row["status"] == "answered"
    assert row["answer"] == "the answer"


def test_ask_user_rejects_empty_question(
    root_with_skills: Path, conversation_id: str
):
    with pytest.raises(ToolError):
        skill_tools.ask_user(root_with_skills, question="   ")


def test_ask_user_rejects_bad_options(
    root_with_skills: Path, conversation_id: str
):
    with pytest.raises(ToolError):
        skill_tools.ask_user(root_with_skills, question="q", options=[1, 2, 3])  # type: ignore[arg-type]
