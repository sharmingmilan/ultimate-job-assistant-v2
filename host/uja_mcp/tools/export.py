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
from datetime import datetime, timezone
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


# ---------------------------------------------------------------------------
# Folder walker + minimum-viable validation (Block 3)
# ---------------------------------------------------------------------------


# Mapping per ADR-002 D4 zip layout + Session 12 brief Block 3 table.
# Each tuple: (project-root subpath, in-zip subfolder, file-pattern, kind).
# Required entries are enforced explicitly in `_walk_application_files`;
# this table only describes optional single-file slots.
_OPTIONAL_FILE_SLOTS: tuple[tuple[str, str, str, str], ...] = (
    ("resumes",          "resume",          "{id}.pdf",        KIND_RESUME_PDF),
    ("scores",           "scores",          "{id}-before.md",  KIND_SCORE_BEFORE),
    ("scores",           "scores",          "{id}-after.md",   KIND_SCORE_AFTER),
    ("speaking-points",  "speaking-points", "{id}.md",         KIND_SPEAKING_POINTS_MD),
    ("speaking-points",  "speaking-points", "{id}.pdf",        KIND_SPEAKING_POINTS_PDF),
    ("cover-letters",    "cover-letter",    "{id}.md",         KIND_COVER_LETTER_MD),
    ("cover-letters",    "cover-letter",    "{id}.pdf",        KIND_COVER_LETTER_PDF),
)


def _resolve_relative(root: Path, rel: str) -> Path:
    """Sandbox-bounded resolve helper that raises ToolError on violation."""
    try:
        return resolve_within_root(root, rel)
    except SandboxViolation as e:
        raise ToolError(f"sandbox: {rel}: {e}") from None


def _read_optional_file(root: Path, rel: str) -> Optional[bytes]:
    """Read a file under the project root if it exists and is a regular file.

    Returns None if absent. Sandbox violations raise ToolError so symlink
    shenanigans are rejected even for optional slots.
    """
    resolved = _resolve_relative(root, rel)
    if not resolved.exists():
        return None
    if not resolved.is_file():
        # Optional slot occupied by a directory or device file: surface
        # rather than silently swallow — the caller's expectation that
        # `<id>.md` is a file is part of the convention.
        raise ToolError(f"expected a regular file at {rel}, found a non-file")
    return resolved.read_bytes()


def _walk_application_files(
    root: Path, company_role: str
) -> list[tuple[str, str, bytes]]:
    """Collect every per-output-type file that belongs in the export zip.

    Returns a list of `(in_zip_path, kind, content_bytes)` rows where
    `in_zip_path` is relative to the zip's top-level `<id>/` directory
    (so manifest paths and zip arcnames match the `<id>/<in_zip_path>`
    pattern downstream).

    Order:
      1. Required: decoded JD `.md` (raises ToolError if absent).
      2. Required: resume DOCX (raises ToolError if absent).
      3. Optional single-file slots from `_OPTIONAL_FILE_SLOTS`, in
         table order — included only if the source file exists.
      4. Optional portfolio subfolder (`portfolio/<id>/`), recursive
         copy preserving in-folder relative paths (R3: strict prefix,
         singular).
      5. Optional networking files (`networking/<id>*.md`), sorted by
         filename.

    Sandbox-bounded throughout — every read goes through
    `resolve_within_root`.
    """
    rows: list[tuple[str, str, bytes]] = []

    # 1. Decoded JD (required).
    decoded_rel = f"decoded-jds/{company_role}.md"
    decoded_bytes = _read_optional_file(root, decoded_rel)
    if decoded_bytes is None:
        raise ToolError(
            f"missing required file: {decoded_rel}. "
            f"The export pipeline requires a decoded JD before bundling."
        )
    rows.append(
        (f"decoded-jd/{company_role}.md", KIND_DECODED_JD, decoded_bytes)
    )

    # 2. Resume DOCX (required).
    resume_rel = f"resumes/{company_role}.docx"
    resume_bytes = _read_optional_file(root, resume_rel)
    if resume_bytes is None:
        raise ToolError(
            f"missing required file: {resume_rel}. "
            f"The export pipeline requires the targeted resume DOCX."
        )
    rows.append(
        (f"resume/{company_role}.docx", KIND_RESUME_DOCX, resume_bytes)
    )

    # 3. Optional single-file slots in table order.
    for src_dir, dst_subfolder, pattern, kind in _OPTIONAL_FILE_SLOTS:
        filename = pattern.format(id=company_role)
        rel = f"{src_dir}/{filename}"
        content = _read_optional_file(root, rel)
        if content is None:
            continue
        rows.append((f"{dst_subfolder}/{filename}", kind, content))

    # 4. Optional portfolio subfolder (R3: strict prefix match, singular).
    portfolio_rel = f"portfolio/{company_role}"
    portfolio_resolved = _resolve_relative(root, portfolio_rel)
    if portfolio_resolved.exists() and portfolio_resolved.is_dir():
        for sub_path in sorted(
            portfolio_resolved.rglob("*"),
            key=lambda p: p.relative_to(portfolio_resolved).as_posix(),
        ):
            if not sub_path.is_file():
                continue
            # Re-check sandbox on each resolved file path: rglob can
            # follow symlinks pointing outside the root.
            try:
                sub_path_resolved = resolve_within_root(root, sub_path)
            except SandboxViolation as e:
                raise ToolError(f"sandbox: portfolio/{sub_path.name}: {e}") from None
            rel_inside = sub_path_resolved.relative_to(
                portfolio_resolved
            ).as_posix()
            content = sub_path_resolved.read_bytes()
            rows.append(
                (f"portfolio/{rel_inside}", KIND_PORTFOLIO, content)
            )

    # 5. Optional networking files matching `<id>*.md`.
    networking_resolved = _resolve_relative(root, "networking")
    if networking_resolved.exists() and networking_resolved.is_dir():
        candidates = sorted(
            networking_resolved.glob(f"{company_role}*.md"),
            key=lambda p: p.name,
        )
        for net_path in candidates:
            if not net_path.is_file():
                continue
            try:
                net_resolved = resolve_within_root(root, net_path)
            except SandboxViolation as e:
                raise ToolError(f"sandbox: networking/{net_path.name}: {e}") from None
            content = net_resolved.read_bytes()
            rows.append(
                (f"networking/{net_path.name}", KIND_NETWORKING, content)
            )

    return rows


# ---------------------------------------------------------------------------
# README renderer (Block 3) — human-readable in-zip index.
# ---------------------------------------------------------------------------


# Friendly labels for the manifest's `kind` enum, used by the README.
_KIND_LABELS: dict[str, str] = {
    KIND_DECODED_JD: "Decoded job description",
    KIND_RESUME_DOCX: "Resume (DOCX)",
    KIND_RESUME_PDF: "Resume (PDF)",
    KIND_SCORE_BEFORE: "Resume score (before)",
    KIND_SCORE_AFTER: "Resume score (after)",
    KIND_SPEAKING_POINTS_MD: "Speaking points (markdown)",
    KIND_SPEAKING_POINTS_PDF: "Speaking points (PDF)",
    KIND_COVER_LETTER_MD: "Cover letter (markdown)",
    KIND_COVER_LETTER_PDF: "Cover letter (PDF)",
    KIND_PORTFOLIO: "Portfolio file",
    KIND_NETWORKING: "Networking note",
}


def _render_readme(
    *,
    company: str,
    role_slug: str,
    application_month: str,
    status: str,
    files: list[dict],
) -> bytes:
    """Build the human-readable in-zip `README.md`.

    Lists the files included with kind labels and sizes. Carries no
    timestamp (R1 spirit: the entire zip is byte-deterministic). Tone
    matches `host/frontend/README.md` — short, plain, no marketing.
    """
    lines: list[str] = []
    lines.append(f"# {company} - {role_slug} ({application_month})")
    lines.append("")
    lines.append(f"Application package, status: {status}.")
    lines.append("")
    lines.append("## Contents")
    lines.append("")
    sorted_files = sorted(files, key=lambda f: f["path"])
    for f in sorted_files:
        label = _KIND_LABELS.get(f["kind"], f["kind"])
        lines.append(f"- `{f['path']}` - {label} ({f['size']} bytes)")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "Generated by the Ultimate Job Assistant export pipeline "
        "(ADR-002 D4)."
    )
    lines.append(
        "Zip bytes are deterministic - re-running the export against "
        "the same on-disk state produces byte-identical output."
    )
    lines.append("")
    return "\n".join(lines).encode("utf-8")


# ---------------------------------------------------------------------------
# Public entrypoint (Block 3 implementation; index.json call lands in Block 4)
# ---------------------------------------------------------------------------


_EXPORTS_REL = "website/v2/exports"
_INDEX_REL = "website/v2/exports/index.json"
_INDEX_SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Site-level index.json maintenance (Block 4)
# ---------------------------------------------------------------------------


def _now_iso_z() -> str:
    """UTC ISO-8601 timestamp with `Z` suffix.

    Matches the example timestamp in ADR-002 D4 (`2026-05-03T12:34:56Z`).
    Lives in `index.json` only — never inside the deterministic zip.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_existing_index(root: Path) -> dict:
    """Load the current `website/v2/exports/index.json` or stub a fresh one.

    Returns a dict shaped `{"schema_version": 1, "exports": [...]}`.
    Raises ToolError if the on-disk file is unparseable JSON.
    """
    index_path = _resolve_relative(root, _INDEX_REL)
    if not index_path.exists():
        return {"schema_version": _INDEX_SCHEMA_VERSION, "exports": []}
    try:
        parsed = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ToolError(
            f"website/v2/exports/index.json is malformed: {e}. "
            f"Either restore from git or delete the file and re-export."
        ) from None
    if not isinstance(parsed, dict):
        raise ToolError(
            "website/v2/exports/index.json must be a JSON object"
        )
    return parsed


def _write_index(root: Path, index: dict) -> None:
    """Persist index.json with stable JSON formatting.

    Determinism: same dict content -> same bytes (sort_keys=True,
    indent=2, trailing newline). The `generated_at` timestamps inside
    rows still vary across runs by design — that field is the only
    legitimate non-determinism source in this layer (R1 lets us
    sacrifice index.json determinism to keep the zip determinism
    contract clean).
    """
    index_path = _resolve_relative(root, _INDEX_REL)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(index, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    )
    index_path.write_text(payload, encoding="utf-8")


def _sort_index_exports(rows: list[dict]) -> list[dict]:
    """Sort exports rows by `application_month` desc, then `company` asc.

    Python's `sorted` is stable, so a two-pass sort with the secondary
    key applied first lands the desired ordering with the simplest
    code path.
    """
    by_company = sorted(rows, key=lambda r: r.get("company", ""))
    return sorted(
        by_company,
        key=lambda r: r.get("application_month", ""),
        reverse=True,
    )


def _update_exports_index(
    root: Path,
    *,
    company_role: str,
    company: str,
    role_slug: str,
    application_month: str,
    status: str,
    size_bytes: int,
) -> dict:
    """Append-or-update the row for `<company_role>.zip` in `index.json`.

    Identity is `filename`. If a row with the same filename exists, it
    is replaced in place (same list slot semantically — the row is
    rebuilt from the current values). If absent, the row is appended.
    Either way, the rows list is sorted before writing so the file's
    diff is stable across re-runs.

    Returns the new (or updated) row.
    """
    index = _read_existing_index(root)

    schema = index.get("schema_version")
    if schema != _INDEX_SCHEMA_VERSION:
        raise ToolError(
            f"website/v2/exports/index.json schema_version mismatch: "
            f"expected {_INDEX_SCHEMA_VERSION}, got {schema!r}"
        )

    exports = index.get("exports", [])
    if not isinstance(exports, list):
        raise ToolError(
            "website/v2/exports/index.json `exports` field is not a list"
        )

    filename = f"{company_role}.zip"
    new_row: dict = {
        "filename": filename,
        "company": company,
        "role": role_slug,
        "application_month": application_month,
        "status": status,
        "size_bytes": size_bytes,
        "generated_at": _now_iso_z(),
        "manifest_path": f"{filename}#manifest.json",
    }

    updated = False
    rebuilt: list[dict] = []
    for row in exports:
        if isinstance(row, dict) and row.get("filename") == filename:
            rebuilt.append(new_row)
            updated = True
        else:
            rebuilt.append(row)
    if not updated:
        rebuilt.append(new_row)

    index["exports"] = _sort_index_exports(rebuilt)
    index["schema_version"] = _INDEX_SCHEMA_VERSION
    _write_index(root, index)
    return new_row


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
    company, role_slug, application_month = _parse_company_role(company_role)
    status = _validate_status(status)
    root = _root()

    rows = _walk_application_files(root, company_role)
    manifest_files = [
        {"path": in_zip_path, "kind": kind, "size": len(content)}
        for in_zip_path, kind, content in rows
    ]

    manifest = _build_manifest(
        company=company,
        role_slug=role_slug,
        application_month=application_month,
        status=status,
        files=manifest_files,
    )
    manifest_bytes = _serialize_manifest(manifest)
    readme_bytes = _render_readme(
        company=company,
        role_slug=role_slug,
        application_month=application_month,
        status=status,
        files=manifest_files,
    )

    # Compose zip arcnames under the top-level `<id>/` directory so the
    # zip extracts into a single named folder (ADR-002 D4 layout).
    zip_entries: list[tuple[str, bytes]] = []
    for in_zip_path, _kind, content in rows:
        zip_entries.append((f"{company_role}/{in_zip_path}", content))
    zip_entries.append((f"{company_role}/manifest.json", manifest_bytes))
    zip_entries.append((f"{company_role}/README.md", readme_bytes))

    # Ensure the exports dir exists, then write the zip via the sandbox.
    exports_dir = _resolve_relative(root, _EXPORTS_REL)
    exports_dir.mkdir(parents=True, exist_ok=True)
    zip_rel = f"{_EXPORTS_REL}/{company_role}.zip"
    zip_path = _resolve_relative(root, zip_rel)
    _write_deterministic_zip(zip_path, zip_entries)

    size_bytes = zip_path.stat().st_size
    sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()

    index_entry = _update_exports_index(
        root,
        company_role=company_role,
        company=company,
        role_slug=role_slug,
        application_month=application_month,
        status=status,
        size_bytes=size_bytes,
    )

    return {
        "company_role": company_role,
        "zip_path": zip_rel,
        "size_bytes": size_bytes,
        "sha256": sha256,
        "manifest": manifest,
        "index_entry": index_entry,
    }
