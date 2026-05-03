"""Path sandbox for the Ultimate Job Assistant host.

Per ADR-001 §D5, every file-tool call must validate that the resolved
absolute path stays within the project root. This module is the single
source of truth for that check.

Design notes:
- pathlib.Path.resolve() follows symlinks and normalizes ".." traversal.
- We use is_relative_to() (3.9+) for the boundary check.
- Both the project root AND the candidate path are resolved before
  comparison, so symlinks pointing outside the root are rejected.
- Empty strings, NUL bytes, and paths that resolve outside the root all
  raise SandboxViolation.
- Callers should treat SandboxViolation as a programming/security error,
  not a normal control-flow signal.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union


class SandboxViolation(Exception):
    """Raised when a path resolves outside the project root."""


PathLike = Union[str, Path]


def resolve_within_root(project_root: PathLike, candidate: PathLike) -> Path:
    """Resolve `candidate` to an absolute Path inside `project_root`.

    `candidate` may be relative (interpreted against project_root) or
    absolute. Symlinks are followed; if the resolved target sits outside
    project_root, SandboxViolation is raised.

    Returns the resolved absolute Path on success.
    """
    if candidate is None:
        raise SandboxViolation("path is required")

    candidate_str = str(candidate)
    if "\x00" in candidate_str:
        raise SandboxViolation("path contains NUL byte")
    if candidate_str.strip() == "":
        raise SandboxViolation("path is empty")

    root = Path(project_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SandboxViolation(f"project root does not exist or is not a directory: {root}")

    cand = Path(candidate_str).expanduser()
    if not cand.is_absolute():
        cand = root / cand

    # resolve(strict=False) handles paths that don't yet exist (write_file
    # creates them). We still resolve any existing parents so symlink
    # escapes are caught.
    resolved = cand.resolve()

    if resolved == root:
        return resolved
    try:
        # is_relative_to was added in 3.9
        is_inside = resolved.is_relative_to(root)
    except AttributeError:  # pragma: no cover — keepalive for <3.9
        is_inside = str(resolved).startswith(str(root) + "/")

    if not is_inside:
        raise SandboxViolation(
            f"path resolves outside project root: {resolved} (root: {root})"
        )

    return resolved


def is_within_root(project_root: PathLike, candidate: PathLike) -> bool:
    """Boolean variant of resolve_within_root for non-error-path checks."""
    try:
        resolve_within_root(project_root, candidate)
        return True
    except SandboxViolation:
        return False
