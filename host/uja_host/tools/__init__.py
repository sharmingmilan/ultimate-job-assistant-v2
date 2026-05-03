"""Tool catalog for the host.

ANTHROPIC_TOOL_DEFS — list of dicts in Anthropic /v1/messages tool format.
TOOL_REGISTRY      — dict mapping tool name to a callable (project_root, **input) -> dict.

Phase 15 fully implements file tools and read_workspace_metadata.
Phase 16 wires real implementations of run_skill (skill catalog +
SKILL.md content load), propose_changes (persisted pending change-sets
for human approval), and ask_user (persisted pending questions).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from . import file_tools, skill_tools
from .file_tools import ToolError


# Anthropic tool definitions — kept in sync with the implementations below.
ANTHROPIC_TOOL_DEFS: list[dict] = [
    {
        "name": "read_file",
        "description": (
            "Read a UTF-8 text file inside the project root. Returns the file "
            "content, byte size, and encoding. Refuses files larger than 1 MB."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Path relative to the project root."}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Create or overwrite a UTF-8 text file inside the project root. "
            "Parent directories are created if needed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": (
            "Replace a unique `find` string in a file with `replace`. Fails if "
            "`find` is missing OR appears more than once. Provide surrounding "
            "context if your target token is not unique."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "find": {"type": "string"},
                "replace": {"type": "string"},
            },
            "required": ["path", "find", "replace"],
        },
    },
    {
        "name": "list_files",
        "description": (
            "List files and directories under `path` (relative to project root). "
            "Optional glob filter on names. Hides dotfiles by default."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "glob": {"type": "string", "description": "fnmatch pattern, e.g. *.md"},
            },
        },
    },
    {
        "name": "read_workspace_metadata",
        "description": (
            "Return the project root path, current git branch, and host version. "
            "Use this to orient yourself at the start of a conversation."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "run_skill",
        "description": (
            "Load a SKILL.md from the project's skills/ directory. With "
            "`name` omitted, returns the catalog of available skills + "
            "their descriptions so you can pick one. With `name` set, "
            "returns the full SKILL.md content + the inputs you passed; "
            "follow the SKILL.md instructions in subsequent turns. The "
            "agent loop stays in you, not in the host."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Skill name (e.g. 'orchestrator', 'resume-targeter'). Omit to list all available skills."},
                "inputs": {"type": "object", "description": "Optional inputs for the skill (per its SKILL.md contract)."},
            },
        },
    },
    {
        "name": "propose_changes",
        "description": (
            "Persist a list of proposed file changes as a pending change-set "
            "for human approval. Pass `changes`: a list of "
            "{path, before?, after, delete?} dicts. Returns a change_set_id; "
            "nothing is applied to disk until the user approves in the UI. "
            "Wait for the next turn before assuming the change landed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "changes": {
                    "type": "array",
                    "description": "List of edits. Each item: {path, before?, after, delete?}.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "before": {"type": "string"},
                            "after": {"type": "string"},
                            "delete": {"type": "boolean"},
                        },
                        "required": ["path"],
                    },
                },
                "summary": {"type": "string", "description": "Optional one-line summary of the change-set."},
                "diff": {"type": "string", "description": "Legacy: a unified-diff string (use `changes` for new code)."},
            },
        },
    },
    {
        "name": "ask_user",
        "description": (
            "Ask the user a clarifying question and pause until they answer. "
            "The chat loop returns the question_id; the UI renders an input "
            "card. Do NOT invent an answer — the next assistant turn only "
            "resumes once the user responds."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "options": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["question"],
        },
    },
]


# name -> (project_root, **input) -> dict
TOOL_REGISTRY: dict[str, Callable[..., dict]] = {
    "read_file": file_tools.read_file,
    "write_file": file_tools.write_file,
    "edit_file": file_tools.edit_file,
    "list_files": file_tools.list_files,
    "read_workspace_metadata": file_tools.read_workspace_metadata,
    "run_skill": skill_tools.run_skill,
    "propose_changes": skill_tools.propose_changes,
    "ask_user": skill_tools.ask_user,
}


def dispatch_tool(project_root: Path, name: str, tool_input: dict) -> tuple[Any, bool]:
    """Run a tool. Returns (result, is_error).

    The result is always a JSON-serializable structure. is_error matches
    the Anthropic tool_result.is_error flag — surface it as content even
    on error so the model can recover.
    """
    fn = TOOL_REGISTRY.get(name)
    if fn is None:
        return ({"error": f"unknown tool: {name}"}, True)
    try:
        return (fn(project_root, **(tool_input or {})), False)
    except ToolError as e:
        return ({"error": str(e), "tool": name}, True)
    except TypeError as e:
        # Wrong arg shape from the model
        return ({"error": f"bad arguments for {name}: {e}"}, True)
    except Exception as e:  # pragma: no cover — last-resort fence
        return ({"error": f"unexpected error in {name}: {type(e).__name__}: {e}"}, True)


def tool_result_content(result: Any) -> str:
    """Format a tool result as a string for the Anthropic tool_result content."""
    if isinstance(result, str):
        return result
    return json.dumps(result, indent=2, default=str)
