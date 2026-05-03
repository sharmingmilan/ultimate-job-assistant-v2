"""Phase 16 tool implementations: run_skill, propose_changes, ask_user.

Replaces the Phase 15 skill_stubs.py module. These three tools are the
host primitives that bridge Claude's agent loop to (1) the project's
SKILL.md library, (2) human approval of proposed file edits, and (3)
human-answered clarifying questions. Persistence lives in SQLite per
ADR-001 §D7 schema v2.

Design contracts:

  run_skill(project_root, name?, inputs?)
      - If `name` is omitted/empty: returns the catalog of available
        skills (name + description + location) so Claude can pick one.
      - Otherwise: returns the full SKILL.md content + the inputs Claude
        passed. Claude follows the SKILL.md instructions in subsequent
        turns; the host does NOT interpret the skill.

  propose_changes(project_root, changes, summary?)
      - Persists a list of {path, before, after} edits as a pending
        change-set. Returns {change_set_id, status: 'pending', ...}.
      - The chat loop yields the change-set ID to the UI; the UI renders
        the diff and posts approve/reject back via /api/changes.
      - propose_changes does NOT apply the edits — that happens only on
        approval, via a separate endpoint.

  ask_user(project_root, question, options?)
      - Persists a pending question. Returns {question_id, status:
        'pending', ...}.
      - The chat loop yields the question ID; the UI renders an input
        card; the answer comes back via /api/questions and unblocks the
        loop.

ToolError is raised for bad inputs (missing kwargs, sandbox violations);
the dispatcher in tools/__init__.py converts it to is_error=True.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from uja_host import config as host_config
from uja_host.db import (
    open_db,
    create_pending_change,
    create_pending_question,
    list_conversations,
)
from uja_host.sandbox import resolve_within_root, SandboxViolation
from uja_host.tools.file_tools import ToolError
from uja_host.tools.skill_registry import list_skills, get_skill

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# run_skill
# ---------------------------------------------------------------------------

def run_skill(
    project_root: Path,
    name: Optional[str] = None,
    inputs: Optional[dict] = None,
) -> dict:
    """Surface the skill catalog OR a single skill's SKILL.md content.

    Skills-as-Tools (ADR D1): the host returns SKILL.md content; Claude
    follows the instructions in subsequent turns of the same chat loop.
    """
    if not name:
        # Catalog mode — return name + description + location for each skill
        skills = list_skills(project_root)
        return {
            "mode": "catalog",
            "count": len(skills),
            "skills": [
                {"name": s.name, "description": s.description, "location": s.location}
                for s in skills
            ],
            "next_step": (
                "Call run_skill again with `name` set to one of the listed skills "
                "to retrieve its SKILL.md content."
            ),
        }

    skill = get_skill(project_root, name)
    if skill is None:
        available = [s.name for s in list_skills(project_root)]
        raise ToolError(
            f"skill '{name}' not found. Available: {available}"
        )

    return {
        "mode": "load",
        "skill": {
            "name": skill.name,
            "description": skill.description,
            "location": skill.location,
            "content": skill.content,
        },
        "inputs": inputs or {},
        "guidance": (
            "Follow the instructions in `skill.content` to complete the user's "
            "request. Use file tools (read_file, write_file, edit_file, "
            "list_files) for any I/O the SKILL.md prescribes. Use "
            "propose_changes for multi-file edits that need user approval. "
            "Use ask_user for any clarifying questions the SKILL.md tells you "
            "to ask."
        ),
    }


# ---------------------------------------------------------------------------
# propose_changes
# ---------------------------------------------------------------------------

def _normalize_changes(
    project_root: Path,
    changes: Any,
) -> list[dict]:
    """Coerce the model's input into a canonical [{path, before, after}, ...].

    Accepts:
      [{"path": "a.txt", "before": "...", "after": "..."}, ...]
      [{"path": "a.txt", "after": "..."}]                     # new file
      [{"path": "a.txt", "content": "..."}]                   # alias for after
      [{"path": "a.txt", "delete": true}]                     # delete intent

    Validates each path against the sandbox. Reads the current file
    content for `before` if not supplied (and if the file exists).
    """
    if not isinstance(changes, list) or not changes:
        raise ToolError("`changes` must be a non-empty list of edits")

    out: list[dict] = []
    for i, ch in enumerate(changes):
        if not isinstance(ch, dict):
            raise ToolError(f"changes[{i}] must be an object, got {type(ch).__name__}")
        path = ch.get("path")
        if not path or not isinstance(path, str):
            raise ToolError(f"changes[{i}].path is required (got {path!r})")

        try:
            resolved = resolve_within_root(project_root, path)
        except SandboxViolation as e:
            raise ToolError(f"changes[{i}]: sandbox: {e}") from None

        # Resolve `before`: if given, trust it; else read from disk if exists.
        before = ch.get("before")
        if before is None:
            if resolved.exists() and resolved.is_file():
                try:
                    before = resolved.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    before = None  # binary or unreadable
            else:
                before = None  # new file

        # `after` is content; `delete=true` is a special case.
        is_delete = bool(ch.get("delete"))
        if is_delete:
            after = None
        else:
            after = ch.get("after")
            if after is None:
                after = ch.get("content")
            if not isinstance(after, str):
                raise ToolError(
                    f"changes[{i}]: `after` (or `content`) must be a string, "
                    f"or pass `delete: true` to remove the file"
                )

        out.append({
            "path": str(resolved.relative_to(project_root)),
            "before": before,
            "after": after,
            "delete": is_delete,
        })
    return out


def _summarize_changes(normalized: list[dict]) -> str:
    """One-line summary of a change-set, for SQLite.summary."""
    if not normalized:
        return "(empty change-set)"
    parts = []
    for ch in normalized[:5]:
        if ch["delete"]:
            parts.append(f"delete {ch['path']}")
        elif ch["before"] is None:
            parts.append(f"create {ch['path']}")
        else:
            parts.append(f"edit {ch['path']}")
    extra = "" if len(normalized) <= 5 else f" (+{len(normalized) - 5} more)"
    return ", ".join(parts) + extra


def _resolve_active_conversation_id(project_root: Path) -> Optional[str]:
    """Best-effort lookup of the most recent conversation.

    The chat loop in api/chat.py knows the conversation_id directly, but
    the tool dispatch signature only carries (project_root, **input).
    Falling back to "the most recently updated conversation" is correct
    for the only call site that exists today (the active chat stream).
    A future refactor can thread conversation_id through the dispatcher
    if multi-conversation parallelism becomes a concern.
    """
    try:
        with open_db(project_root) as conn:
            convs = list_conversations(conn, limit=1)
            return convs[0]["id"] if convs else None
    except Exception:  # pragma: no cover — DB not yet initialized
        return None


def propose_changes(
    project_root: Path,
    changes: Any = None,
    summary: str = "",
    diff: Optional[str] = None,  # back-compat: legacy unified-diff string
) -> dict:
    """Persist a multi-file change-set as a pending approval.

    Returns the change-set ID + a structured representation for the UI to
    render. Does NOT apply the edits — only an explicit approval (via the
    /api/changes endpoint, Phase 17) does that.
    """
    # Back-compat: if `changes` is missing but `diff` is supplied, accept
    # the legacy string and surface it as a single "raw_diff" entry. The
    # frontend renders a code block; humans approve/reject; nothing on
    # disk happens until applied.
    if changes is None and diff is not None:
        normalized = [{
            "path": "(unified-diff)",
            "before": None,
            "after": diff,
            "delete": False,
            "raw_diff": True,
        }]
        if not summary:
            summary = "raw unified diff (legacy mode)"
    else:
        normalized = _normalize_changes(project_root, changes)
        if not summary:
            summary = _summarize_changes(normalized)

    conv_id = _resolve_active_conversation_id(project_root)
    if conv_id is None:
        raise ToolError(
            "propose_changes requires an active conversation; the chat "
            "loop should always have created one before tool dispatch."
        )

    with open_db(project_root) as conn:
        change_set_id = create_pending_change(
            conn,
            conversation_id=conv_id,
            tool_use_id=None,  # Phase 17 will thread the tool_use_id through dispatch
            changes=normalized,
            summary=summary,
        )

    return {
        "tool": "propose_changes",
        "change_set_id": change_set_id,
        "status": "pending",
        "summary": summary,
        "files": [c["path"] for c in normalized],
        "next_step": (
            "Wait for the user to approve or reject this change-set in the UI "
            "(or via /api/changes/<id>/approve). Do not assume approval — "
            "another assistant turn will resume only after the user responds."
        ),
    }


# ---------------------------------------------------------------------------
# ask_user
# ---------------------------------------------------------------------------

def ask_user(
    project_root: Path,
    question: str,
    options: Optional[list[str]] = None,
) -> dict:
    """Persist a pending question; the chat loop pauses for an answer."""
    if not isinstance(question, str) or not question.strip():
        raise ToolError("`question` must be a non-empty string")
    if options is not None:
        if not isinstance(options, list) or not all(isinstance(o, str) for o in options):
            raise ToolError("`options`, if provided, must be a list of strings")

    conv_id = _resolve_active_conversation_id(project_root)
    if conv_id is None:
        raise ToolError(
            "ask_user requires an active conversation; the chat loop "
            "should have created one before tool dispatch."
        )

    with open_db(project_root) as conn:
        question_id = create_pending_question(
            conn,
            conversation_id=conv_id,
            tool_use_id=None,
            question=question.strip(),
            options=options,
        )

    return {
        "tool": "ask_user",
        "question_id": question_id,
        "status": "pending",
        "question": question.strip(),
        "options": options,
        "next_step": (
            "Wait for the user to answer in the UI (or via "
            "/api/questions/<id>/answer). Do not invent an answer."
        ),
    }
