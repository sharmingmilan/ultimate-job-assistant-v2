"""Skill registry: discover skills/*/SKILL.md and surface them as tools.

Per ADR-001 §D1 (Skills-as-Tools): the host registers a fixed tool
catalog with the Anthropic API; the agent loop stays inside Claude.
SKILL.md files are the source of truth — the host's job is to find them
and return their content so Claude can follow the instructions.

Discovery walks <project_root>/skills/*/SKILL.md, parses YAML
frontmatter (name + description), and exposes:

    list_skills(project_root)        → [{name, description, location}]
    get_skill(project_root, name)    → {name, description, location, content}

`run_skill` (in skill_tools.py) calls these to answer "what skills exist"
and "what does this skill do".
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from uja_host.sandbox import resolve_within_root, SandboxViolation


SKILLS_DIR = "skills"
SKILL_FILE = "SKILL.md"


@dataclass
class Skill:
    name: str
    description: str
    location: str  # path relative to project root
    content: str   # full SKILL.md body (frontmatter stripped from view but kept in content)

    def to_dict(self) -> dict:
        return asdict(self)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Pull a leading YAML-like frontmatter block from a SKILL.md.

    SKILL.md frontmatter in this project is consistently:

        ---
        name: foo
        description: "..."
        ---

    We don't need a real YAML parser — `name` and `description` are the
    only keys we read, and they're always single-line. Quoted strings are
    unwrapped; the rest is taken verbatim.

    Returns (frontmatter_dict, body_after_frontmatter). If no frontmatter
    delimiter is present, returns ({}, text).
    """
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n---", 2)
    if len(parts) < 2:
        return {}, text
    # parts[0] is "---" + first line; parts[1] is the frontmatter body
    fm_block = parts[0].lstrip("-").strip("\n")
    rest = parts[1]
    # Strip leading newline from `rest` if present
    if rest.startswith("\n"):
        rest = rest[1:]

    fm: dict = {}
    for line in fm_block.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val.startswith('"') and val.endswith('"') and len(val) >= 2:
            val = val[1:-1]
        if val.startswith("'") and val.endswith("'") and len(val) >= 2:
            val = val[1:-1]
        fm[key] = val
    return fm, rest


def _read_skill_file(project_root: Path, skill_dir: Path) -> Optional[Skill]:
    """Read one skills/<name>/SKILL.md. Returns None if invalid."""
    skill_md = skill_dir / SKILL_FILE
    if not skill_md.exists() or not skill_md.is_file():
        return None
    try:
        text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    fm, _body = _parse_frontmatter(text)
    name = fm.get("name") or skill_dir.name
    description = fm.get("description") or ""
    rel = skill_md.relative_to(project_root)
    return Skill(
        name=name,
        description=description,
        location=str(rel),
        content=text,
    )


def list_skills(project_root: Path) -> list[Skill]:
    """Discover every skills/*/SKILL.md under the project root.

    Sandbox-bounded: the skills/ directory must resolve inside
    project_root. Hidden directories (dotfiles) are skipped.
    """
    try:
        skills_root = resolve_within_root(project_root, SKILLS_DIR)
    except SandboxViolation:
        return []
    if not skills_root.exists() or not skills_root.is_dir():
        return []

    found: list[Skill] = []
    for child in sorted(skills_root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        skill = _read_skill_file(project_root, child)
        if skill is not None:
            found.append(skill)
    return found


def get_skill(project_root: Path, name: str) -> Optional[Skill]:
    """Find a skill by name (matches frontmatter `name` first, then directory name)."""
    for s in list_skills(project_root):
        if s.name == name:
            return s
    # Fallback: directory-name match (handles edge cases where frontmatter
    # name diverges from the folder name).
    try:
        skills_root = resolve_within_root(project_root, SKILLS_DIR)
    except SandboxViolation:
        return None
    candidate_dir = skills_root / name
    if candidate_dir.is_dir():
        return _read_skill_file(project_root, candidate_dir)
    return None
