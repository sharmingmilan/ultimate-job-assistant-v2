"""File-system tools (Phase 15 fully implements these).

All paths route through uja_host.sandbox so nothing escapes the project root.
Each tool returns a plain JSON-serializable dict. Errors are raised as
ToolError, which the dispatch layer converts to the Anthropic
tool_result {is_error: True, content: ...} shape.
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Any

from uja_host.sandbox import resolve_within_root, SandboxViolation


class ToolError(Exception):
    """Tool-level error surfaced to the model as a structured tool_result."""


MAX_READ_BYTES = 1_000_000  # 1 MB cap per ADR-001 spirit ("read a file under root")


def _safe(project_root: Path, path: str) -> Path:
    try:
        return resolve_within_root(project_root, path)
    except SandboxViolation as e:
        raise ToolError(f"sandbox: {e}") from None


def read_file(project_root: Path, path: str) -> dict:
    p = _safe(project_root, path)
    if not p.exists():
        raise ToolError(f"file does not exist: {path}")
    if p.is_dir():
        raise ToolError(f"path is a directory, not a file: {path}")
    size = p.stat().st_size
    if size > MAX_READ_BYTES:
        raise ToolError(
            f"file is {size} bytes; refusing to read more than {MAX_READ_BYTES}. "
            "Use list_files for directory exploration."
        )
    try:
        text = p.read_text(encoding="utf-8")
        encoding = "utf-8"
    except UnicodeDecodeError:
        # Fall back to latin-1 lossless byte-string for binaries (rare in this project).
        text = p.read_bytes().decode("latin-1")
        encoding = "latin-1 (binary)"
    return {
        "path": str(p.relative_to(project_root)),
        "size_bytes": size,
        "encoding": encoding,
        "content": text,
    }


def write_file(project_root: Path, path: str, content: str) -> dict:
    p = _safe(project_root, path)
    if p.is_dir():
        raise ToolError(f"path is a directory: {path}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {
        "path": str(p.relative_to(project_root)),
        "bytes_written": len(content.encode("utf-8")),
        "created": True,
    }


def edit_file(project_root: Path, path: str, find: str, replace: str) -> dict:
    p = _safe(project_root, path)
    if not p.exists() or p.is_dir():
        raise ToolError(f"file does not exist: {path}")
    text = p.read_text(encoding="utf-8")
    occurrences = text.count(find)
    if occurrences == 0:
        raise ToolError(f"`find` string not found in {path}")
    if occurrences > 1:
        raise ToolError(
            f"`find` string is not unique in {path} ({occurrences} matches). "
            "Provide more surrounding context to disambiguate."
        )
    new_text = text.replace(find, replace, 1)
    p.write_text(new_text, encoding="utf-8")
    return {
        "path": str(p.relative_to(project_root)),
        "replacements": 1,
        "bytes_after": len(new_text.encode("utf-8")),
    }


def list_files(project_root: Path, path: str = ".", glob: str | None = None) -> dict:
    p = _safe(project_root, path)
    if not p.exists():
        raise ToolError(f"path does not exist: {path}")
    if not p.is_dir():
        raise ToolError(f"path is not a directory: {path}")

    entries = []
    for child in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        if child.name.startswith(".") and child.name not in (".github",):
            # skip dotfiles (incl. .uja DB dir, .git, .venv) by default
            continue
        if glob and not fnmatch.fnmatch(child.name, glob):
            continue
        entries.append({
            "name": child.name,
            "type": "dir" if child.is_dir() else "file",
            "size_bytes": child.stat().st_size if child.is_file() else None,
        })
    return {
        "path": str(p.relative_to(project_root)) if p != project_root else ".",
        "entries": entries,
        "count": len(entries),
    }


def read_workspace_metadata(project_root: Path) -> dict:
    """Returns project root + lightweight environment info.

    Intentionally cheap and read-only.
    """
    return {
        "project_root": str(project_root),
        "exists": project_root.exists(),
        "is_dir": project_root.is_dir(),
        "git_branch": _git_branch(project_root),
        "host_version": _host_version(),
    }


def _git_branch(project_root: Path) -> str | None:
    head = project_root / ".git" / "HEAD"
    if not head.exists():
        return None
    try:
        text = head.read_text().strip()
    except OSError:
        return None
    if text.startswith("ref: refs/heads/"):
        return text[len("ref: refs/heads/"):]
    return text  # detached HEAD


def _host_version() -> str:
    try:
        from uja_host import __version__
        return __version__
    except Exception:  # pragma: no cover
        return "unknown"
