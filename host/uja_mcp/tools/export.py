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
import re
import zipfile
from pathlib import Path
from typing import Iterable, Optional

from uja_host import config as host_config
from uja_host.sandbox import SandboxViolation, resolve_within_root
from uja_host.tools.file_tools import ToolError


# Per ADR-002 D4 + Session 12 brief R2.
ALLOWED_STATUSES = frozenset(
    {"open", "submitted", "interviewing", "offer", "closed", "rejected"}
)

# `<company>-<role-slug>-<YYYY>-<MM>`. The role-slug may contain hyphens;
# the trailing two hyphen-separated tokens always form `YYYY-MM`. Year
# matched permissively (any 4-digit) so 2026 + future years all parse;
# month constrained to 01-12 to catch typos like `2026-13`.
_ID_RE = re.compile(
    r"^(?P<company>[a-z0-9]+(?:[a-z0-9])*)"
    r"-(?P<role_slug>[a-z0-9]+(?:-[a-z0-9]+)*)"
    r"-(?P<year>\d{4})-(?P<month>0[1-9]|1[0-2])$"
)

# `kind` enum for manifest.files entries (per Session 12 brief Block 2).
KIND_DECODED_JD = "decoded_jd"
KIND_RESUME_DOCX = "resume_docx"
KIND_RESUME_PDF = "resume_pdf"
KIND_SCORE_BEFORE = "score_before"
KIND_SCORE_AFTER = "score_after"
KIND_SPEAKING_POINTS_MD = "speaking_points_md"
KIND_SPEAKING_POINTS_PDF = "speaking_points_pdf"
KIND_COVER_LETTER_MD = "cover_letter_md"
KIND_COVER_LETTER_PDF = "cover_letter_pdf"
KIND_PORTFOLIO = "portfolio"
KIND_NETWORKING = "networking"


def _root() -> Path:
    root = host_config.get_project_root()
    if root is None:
        raise ToolError(
            "project_root not configured. Set UJA_PROJECT_ROOT in the "
            "environment before launching the MCP server, or write "
            "~/.uja/config.json with a project_root field."
        )
    return root


def _parse_company_role(company_role: str) -> tuple[str, str, str]:
    """Split `<company>-<role-slug>-<YYYY-MM>` into its three parts.

    Returns `(company, role_slug, application_month)`. Raises `ToolError`
    on a malformed identifier. The naming convention is defined in
    `CLAUDE.md` and is load-bearing for filename matching downstream.
    """
    if not isinstance(company_role, str) or not company_role:
        raise ToolError("`company_role` is required and must be a string")
    m = _ID_RE.match(company_role)
    if not m:
        raise ToolError(
            f"`company_role` does not match the naming convention "
            f"`<company>-<role-slug>-<YYYY-MM>`: {company_role!r}"
        )
    return (
        m.group("company"),
        m.group("role_slug"),
        f"{m.group('year')}-{m.group('month')}",
    )


def _validate_status(status: str) -> str:
    if not isinstance(status, str) or not status:
        raise ToolError("`status` is required and must be a non-empty string")
    if status not in ALLOWED_STATUSES:
        raise ToolError(
            f"unknown status {status!r}; allowed: "
            f"{sorted(ALLOWED_STATUSES)}"
        )
    return status


# ---------------------------------------------------------------------------
# Deterministic zip writer (Block 2)
# ---------------------------------------------------------------------------


# ZIP epoch: 1980-01-01 00:00:00 (the earliest representable timestamp in
# the ZIP local file header format). Every entry uses this fixed value so
# zip bytes are insensitive to wall-clock time.
_ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)

# Deterministic Unix mode bits in `external_attr`. ZIP stores Unix file
# mode in the high 16 bits. 0o644 for files, 0o755 with the directory
# flag (0x10) for entries representing directories.
_FILE_EXTERNAL_ATTR = (0o644 << 16)
_DIR_EXTERNAL_ATTR = (0o755 << 16) | 0x10

# Compression: pin the level explicitly. The Python `zipfile` default
# changed in practice across CPython releases; pinning level=6 (the
# zlib default) keeps bytes stable across interpreter versions.
_COMPRESSION = zipfile.ZIP_DEFLATED
_COMPRESSLEVEL = 6


def _write_deterministic_zip(
    target_path: Path,
    entries: Iterable[tuple[str, bytes]],
) -> None:
    """Write `entries` to `target_path` with byte-identical output across runs.

    `entries` is an iterable of `(arcname, content_bytes)` tuples. The
    function:

      - sorts entries by `arcname` (insertion order is irrelevant);
      - rejects duplicate arcnames (a programming error);
      - writes each entry with `date_time=_ZIP_EPOCH`,
        `compress_type=_COMPRESSION`, `external_attr=_FILE_EXTERNAL_ATTR`;
      - sets `compresslevel=6` on the underlying `ZipFile` so deflate
        output is stable across CPython versions;
      - emits no global ZIP comment.

    The parent directory of `target_path` must already exist; the
    caller is responsible for that (the export pipeline routes through
    `resolve_within_root` and creates the dir explicitly).
    """
    sorted_entries = sorted(entries, key=lambda e: e[0])
    seen: set[str] = set()
    for arcname, _ in sorted_entries:
        if arcname in seen:
            raise ToolError(f"duplicate arcname in zip entries: {arcname!r}")
        seen.add(arcname)

    with zipfile.ZipFile(
        target_path,
        mode="w",
        compression=_COMPRESSION,
        compresslevel=_COMPRESSLEVEL,
    ) as zf:
        for arcname, content in sorted_entries:
            info = zipfile.ZipInfo(filename=arcname, date_time=_ZIP_EPOCH)
            info.compress_type = _COMPRESSION
            info.external_attr = _FILE_EXTERNAL_ATTR
            # No CREATE_SYSTEM override: zipfile sets it consistently per
            # Python version; what we control here (timestamps + mode +
            # compression) is enough for byte-identical output on a
            # given Python.
            zf.writestr(info, content)


# ---------------------------------------------------------------------------
# Manifest builder (Block 2)
# ---------------------------------------------------------------------------


_MANIFEST_SCHEMA_VERSION = 1


def _build_manifest(
    *,
    company: str,
    role_slug: str,
    application_month: str,
    status: str,
    files: list[dict],
) -> dict:
    """Assemble the in-zip `manifest.json` payload (schema v1).

    Per Session 12 brief R1: NO `generated_at` field. Wall-clock
    information lives in the per-row entry of `website/v2/exports/
    index.json` instead, where determinism is not contracted.

    `files` is a list of `{"path": str, "kind": str, "size": int}` rows
    sorted by `path` ascending so the manifest's diff is stable.
    """
    sorted_files = sorted(files, key=lambda f: f["path"])
    return {
        "schema_version": _MANIFEST_SCHEMA_VERSION,
        "company": company,
        "role_slug": role_slug,
        "application_month": application_month,
        "status": status,
        "files": sorted_files,
    }


def _serialize_manifest(manifest: dict) -> bytes:
    """JSON-encode the manifest with stable formatting (sort_keys, 2-space indent).

    The deterministic-zip contract bites here too: serialization must
    produce identical bytes across runs.
    """
    return (
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


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
