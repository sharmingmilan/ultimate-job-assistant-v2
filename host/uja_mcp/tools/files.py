"""Files MCP tools — read/write/edit/list + workspace metadata.

Thin facade over `host/uja_host/tools/file_tools.py` for the MCP
boundary (ADR-002 D1 tool surface). Each function:

  - resolves the project root via `host_config.get_project_root()`,
  - raises `ToolError` (the surviving error type from Phase 15) if no
    root is configured, which FastMCP surfaces as a structured error,
  - delegates the actual work to the surviving file-tool implementation.

Logic stays in `host/uja_host/`; this layer only adapts the call shape
(no project-root arg) and the configuration entrypoint.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from uja_host import config as host_config
from uja_host.tools import file_tools
from uja_host.tools.file_tools import ToolError


def _root() -> Path:
    root = host_config.get_project_root()
    if root is None:
        raise ToolError(
            "project_root not configured. Set UJA_PROJECT_ROOT in the "
            "environment before launching the MCP server, or write "
            "~/.uja/config.json with a project_root field."
        )
    return root


def read_file(path: str) -> dict:
    """Read a UTF-8 text file inside the project root.

    Returns the file content, byte size, and detected encoding. Refuses
    files larger than 1 MB; use `list_files` for directory exploration
    instead.
    """
    return file_tools.read_file(_root(), path)


def write_file(path: str, content: str) -> dict:
    """Create or overwrite a UTF-8 text file inside the project root.

    Parent directories are created if needed. Returns the relative path
    written and the byte count. Sandbox-bounded: the resolved path must
    stay under the project root.
    """
    return file_tools.write_file(_root(), path, content)


def edit_file(path: str, find: str, replace: str) -> dict:
    """Replace a unique `find` string in a file with `replace`.

    Fails if `find` is missing OR appears more than once — provide
    surrounding context if your target token is not unique.
    """
    return file_tools.edit_file(_root(), path, find, replace)


def list_files(path: str = ".", glob: Optional[str] = None) -> dict:
    """List files and directories under `path` (relative to project root).

    Optional fnmatch-style `glob` filter on entry names. Hidden dotfiles
    are skipped by default.
    """
    return file_tools.list_files(_root(), path, glob)


def read_workspace_metadata() -> dict:
    """Return the project root path, git branch, and host version.

    Cheap, read-only, sandbox-free. Use this at the start of a session
    to orient yourself before touching any files.
    """
    return file_tools.read_workspace_metadata(_root())
