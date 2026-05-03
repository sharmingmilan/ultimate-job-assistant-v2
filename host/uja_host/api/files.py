"""GET /api/files — read-only HTTP surface over the project root.

Phase 17 carves a thin HTTP API out of the existing tool implementations
so the Materials tab can browse and preview files. All paths route
through the sandbox; nothing escapes the project root.

Endpoints:
  GET /api/files/tree?path=<rel>   list directory entries
  GET /api/files/raw?path=<rel>    return raw bytes (Content-Type sniffed)
  GET /api/files/text?path=<rel>   return UTF-8 text + size + encoding
"""

from __future__ import annotations

import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from uja_host import config as host_config
from uja_host.sandbox import resolve_within_root, SandboxViolation
from uja_host.tools import file_tools as ft

router = APIRouter(prefix="/api/files", tags=["files"])


def _root() -> Path:
    root = host_config.get_project_root()
    if root is None:
        raise HTTPException(status_code=409, detail="project_root not configured")
    return root


def _safe(root: Path, path: str) -> Path:
    try:
        return resolve_within_root(root, path)
    except SandboxViolation as e:
        raise HTTPException(status_code=400, detail=f"sandbox: {e}")


@router.get("/tree")
def tree(path: str = Query(default=".")) -> dict:
    """Recursive listing one level deep at `path`."""
    try:
        return ft.list_files(_root(), path=path)
    except ft.ToolError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/text")
def text(path: str = Query(...)) -> dict:
    """Return UTF-8 text decode for editor preview. Capped at MAX_READ_BYTES."""
    try:
        return ft.read_file(_root(), path=path)
    except ft.ToolError as e:
        # Distinguish "too big" from "missing" for cleaner client UX.
        msg = str(e).lower()
        if "refusing to read" in msg:
            raise HTTPException(status_code=413, detail=str(e))
        if "directory" in msg:
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/raw")
def raw(path: str = Query(...)) -> Response:
    """Return raw file bytes with sniffed Content-Type. Used for PDF/DOCX previews."""
    root = _root()
    p = _safe(root, path)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"file does not exist: {path}")
    if p.is_dir():
        raise HTTPException(status_code=400, detail=f"path is a directory: {path}")
    if p.stat().st_size > 25_000_000:  # 25 MB ceiling for binary previews
        raise HTTPException(status_code=413, detail="file exceeds 25 MB raw cap")
    ctype, _ = mimetypes.guess_type(p.name)
    return Response(content=p.read_bytes(), media_type=ctype or "application/octet-stream")
