"""Stub implementations for the skill-related tools.

Phase 15 intentionally does NOT wire these — they require the skill
registry (Phase 16) and the human-in-the-loop UX (Phase 17). The stubs
return a structured `not_implemented` payload so the model gets a clear
signal rather than a crash.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


_NOT_IMPL = {
    "status": "not_implemented",
    "phase": "Phase 15 ships file tools only; skill tools land in Phase 16.",
}


def run_skill(project_root: Path, name: str, inputs: dict | None = None) -> dict:
    return {**_NOT_IMPL, "tool": "run_skill", "requested": {"name": name, "inputs": inputs or {}}}


def propose_changes(project_root: Path, diff: str) -> dict:
    return {**_NOT_IMPL, "tool": "propose_changes", "diff_chars": len(diff or "")}


def ask_user(project_root: Path, question: str, options: list[str] | None = None) -> dict:
    return {
        **_NOT_IMPL,
        "tool": "ask_user",
        "question": question,
        "options": options or [],
    }
