"""Host configuration: ~/.uja/config.json + project root selection.

Per ADR-001 §D5/§D7 the project root is chosen once via a native folder
picker on first launch and persisted to ~/.uja/config.json. The SQLite
database lives at <project_root>/.uja/state.db, so we need this bootstrap
config OUTSIDE the project root to know where to find the DB on subsequent
launches (chicken-and-egg).

This module is intentionally tiny: it owns reading and writing the
bootstrap file, validating the chosen root, and offering a CLI fallback
(via --project-root) for headless environments where tkinter isn't
available.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".uja"
CONFIG_FILE = CONFIG_DIR / "config.json"
CONFIG_SCHEMA_VERSION = 1


@dataclass
class HostConfig:
    project_root: Optional[str] = None
    schema_version: int = CONFIG_SCHEMA_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def load_config() -> HostConfig:
    """Read ~/.uja/config.json. Returns an empty HostConfig if missing."""
    if not CONFIG_FILE.exists():
        return HostConfig()
    try:
        raw = json.loads(CONFIG_FILE.read_text())
    except json.JSONDecodeError:
        # Corrupt config — surface it; do not silently overwrite.
        raise
    return HostConfig(
        project_root=raw.get("project_root"),
        schema_version=raw.get("schema_version", CONFIG_SCHEMA_VERSION),
    )


def save_config(cfg: HostConfig) -> None:
    """Atomically write ~/.uja/config.json with chmod 600."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cfg.to_dict(), indent=2))
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass  # best effort on Windows
    tmp.replace(CONFIG_FILE)


def set_project_root(path: str) -> HostConfig:
    """Validate and persist the project root.

    Raises ValueError if the path doesn't exist, isn't a directory, or
    isn't writable.
    """
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise ValueError(f"project root does not exist: {p}")
    if not p.is_dir():
        raise ValueError(f"project root is not a directory: {p}")
    if not os.access(p, os.W_OK):
        raise ValueError(f"project root is not writable: {p}")

    cfg = load_config()
    cfg.project_root = str(p)
    save_config(cfg)
    return cfg


def get_project_root() -> Optional[Path]:
    cfg = load_config()
    if cfg.project_root is None:
        return None
    return Path(cfg.project_root)


def pick_project_root_via_dialog() -> Optional[str]:  # pragma: no cover
    """Open a native folder picker. Returns None if user cancels.

    Best-effort across platforms via tkinter.filedialog. If tkinter is
    unavailable (headless), returns None — caller should fall back to a
    CLI prompt or --project-root flag.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return None

    root = tk.Tk()
    root.withdraw()
    root.update()
    try:
        chosen = filedialog.askdirectory(
            title="Choose your Ultimate Job Assistant folder",
            mustexist=True,
        )
    finally:
        root.destroy()
    return chosen or None
