"""Export pipeline MCP tool — `export_application` (ADR-002 D4, Phase 24).

This is the only net-new capability in v0.2.x — the rest of the MCP
tool surface is a thin facade over surviving `host/uja_host/` code, but
the export pipeline has no FastAPI predecessor. Lives in the MCP layer
because that's the only place it's invoked from.

Walks the per-output-type folders (`decoded-jds/`, `resumes/`, etc.)
under the project root for a given `<company>-<role-slug>-<YYYY-MM>`
identifier, validates the minimum-viable set (decoded JD + resume
DOCX), and writes a deterministic zip to `website/v2/exports/<id>.zip`.
Idempotently maintains `website/v2/exports/index.json`, the v2 site's
data source.

Determinism contract (per ADR-002 D4 + Session 12 brief R1): re-running
`export_application` against the same on-disk state and the same
`status` produces byte-identical zip output. Achieved by sorted entry
ordering, fixed `compresslevel=6`, zeroed entry timestamps, deterministic
`external_attr`, and omission of `generated_at` from the in-zip
`manifest.json`. The site-level `index.json` carries `generated_at` and
has no determinism contract.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Iterable, Optional

from uja_host import config as host_config
from uja_host.sandbox import SandboxViolation, resolve_within_root
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


def export_application(
    company_role: str,
    status: str = "submitted",
) -> dict:
    """Bundle a per-application zip into `website/v2/exports/`.

    Walks the per-output-type folders under the project root for the
    given `<company>-<role-slug>-<YYYY-MM>` identifier and writes a
    deterministic zip plus a manifest. Updates `website/v2/exports/
    index.json` (the v2 site's data source) idempotently — re-running
    against the same `<id>` updates the existing row in place.

    Inputs (Session 12 brief R2 / R3 enforced):
      - `company_role`: the `<company>-<role-slug>-<YYYY-MM>` identifier.
        Validated against the naming convention; a `ToolError` is raised
        on a malformed value.
      - `status`: explicit caller-provided application status, in
        `{open, submitted, interviewing, offer, closed, rejected}`.
        Defaults to "submitted". Unknown values raise `ToolError`. Per
        R2, the export pipeline does NOT parse `tracker.md` to derive
        status — Cowork passes the current value.

    Outputs: a dict shaped like

        {
          "company_role": "<id>",
          "zip_path": "website/v2/exports/<id>.zip",
          "size_bytes": <int>,
          "sha256": "<hex>",
          "manifest": {... in-zip manifest payload ...},
          "index_entry": {... row written to exports/index.json ...},
        }

    Error modes:
      - Missing `decoded-jds/<id>.md`: `ToolError`.
      - Missing `resumes/<id>.docx`: `ToolError`.
      - Unknown status: `ToolError`.
      - Sandbox violation on any resolved path: `ToolError`.

    Determinism (R1): `manifest.json` carries no wall-clock timestamp.
    Re-running with the same on-disk state and the same `status`
    produces byte-identical zip bytes (verified by sha256 in the
    protocol-level test).
    """
    raise NotImplementedError(
        "Phase 24 Block 1 placeholder; Block 2-4 fill this in."
    )
