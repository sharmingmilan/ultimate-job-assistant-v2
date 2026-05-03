"""Skills MCP tools — `list_skills` and `read_skill`.

Per ADR-002 D1, the Phase 16 `run_skill` primitive is split into two
MCP-idiomatic tools: a catalog tool (`list_skills`) and a content tool
(`read_skill`). Cowork picks a skill from the catalog, reads its
SKILL.md, and follows the instructions in subsequent turns — the
Skills-as-Tools contract from ADR-001 D1, with a sharper boundary.

Wraps `host/uja_host/tools/skill_registry.py`.
"""

from __future__ import annotations

from pathlib import Path

from uja_host import config as host_config
from uja_host.tools import skill_registry
from uja_host.tools.file_tools import ToolError


def _root() -> Path:
    root = host_config.get_project_root()
    if root is None:
        raise ToolError("project_root not configured")
    return root


def list_skills() -> dict:
    """Return the catalog of skills in the project's `skills/` directory.

    Each entry has `name`, `description`, and `location` (relative path
    to the SKILL.md). Use this to discover what skills are available;
    follow up with `read_skill(name)` to retrieve the full instructions
    for one of them.
    """
    root = _root()
    skills = skill_registry.list_skills(root)
    return {
        "count": len(skills),
        "skills": [
            {
                "name": s.name,
                "description": s.description,
                "location": s.location,
            }
            for s in skills
        ],
    }


def read_skill(name: str) -> dict:
    """Return the full SKILL.md content + metadata for one skill.

    Match is by frontmatter `name` first, then by directory name. Raises
    a tool error with the available-skills list if the name is unknown.
    """
    if not name or not isinstance(name, str):
        raise ToolError("`name` is required")
    root = _root()
    skill = skill_registry.get_skill(root, name)
    if skill is None:
        available = [s.name for s in skill_registry.list_skills(root)]
        raise ToolError(f"skill '{name}' not found. Available: {available}")
    return {
        "name": skill.name,
        "description": skill.description,
        "location": skill.location,
        "content": skill.content,
    }
