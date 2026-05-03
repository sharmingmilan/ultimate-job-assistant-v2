"""Phase 24 export pipeline tests.

Covers `export_application` end-to-end and the pure-function helpers it
delegates to. ADR-002 D4 + Session 12 brief.

Block 2 — deterministic zip writer + manifest builder schema.
Block 3 — folder walker + minimum-viable validation + sandbox bounds.
Block 4 — exports/index.json maintenance (first-run, in-place update,
          sort order).
Block 5's protocol-level happy-path test lives in test_mcp_server.py.

Run:
    cd host && python -m pytest tests/test_export_application.py -v
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from uja_mcp.tools import export


# ---------------------------------------------------------------------------
# Block 2 — deterministic zip writer
# ---------------------------------------------------------------------------


def _sample_entries() -> list[tuple[str, bytes]]:
    return [
        ("netflix-data-analyst-2026-04/decoded-jd/netflix-data-analyst-2026-04.md",
         b"# Decoded JD\n\nbody body body\n"),
        ("netflix-data-analyst-2026-04/manifest.json",
         b'{"schema_version": 1}\n'),
        ("netflix-data-analyst-2026-04/README.md",
         b"# Netflix - Data Analyst (2026-04)\n"),
        ("netflix-data-analyst-2026-04/resume/netflix-data-analyst-2026-04.docx",
         b"\x50\x4b\x03\x04\x00\x00fake-docx-bytes\x00"),
    ]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def test_zip_bytes_are_deterministic_across_runs(tmp_path: Path):
    a = tmp_path / "a.zip"
    b = tmp_path / "b.zip"
    export._write_deterministic_zip(a, _sample_entries())
    export._write_deterministic_zip(b, _sample_entries())
    assert _sha256(a) == _sha256(b), (
        "two zip writes with identical inputs must produce byte-identical "
        "output (the determinism contract)"
    )


def test_zip_bytes_are_deterministic_across_input_ordering(tmp_path: Path):
    a = tmp_path / "a.zip"
    b = tmp_path / "b.zip"
    entries = _sample_entries()
    # b receives the entries in reverse order; output must still match.
    export._write_deterministic_zip(a, entries)
    export._write_deterministic_zip(b, list(reversed(entries)))
    assert _sha256(a) == _sha256(b), (
        "input ordering must not affect output bytes (sort happens "
        "inside the writer)"
    )


def test_zip_writer_uses_zip_epoch_timestamps(tmp_path: Path):
    """date_time must be (1980, 1, 1, 0, 0, 0) for every entry."""
    out = tmp_path / "out.zip"
    export._write_deterministic_zip(out, _sample_entries())
    with zipfile.ZipFile(out) as zf:
        for info in zf.infolist():
            assert info.date_time == (1980, 1, 1, 0, 0, 0), (
                f"{info.filename} has non-epoch date_time {info.date_time}"
            )


def test_zip_writer_rejects_duplicate_arcnames(tmp_path: Path):
    out = tmp_path / "out.zip"
    entries = [
        ("a.txt", b"first"),
        ("a.txt", b"second"),
    ]
    with pytest.raises(Exception) as exc:
        export._write_deterministic_zip(out, entries)
    assert "duplicate" in str(exc.value).lower()


# ---------------------------------------------------------------------------
# Block 2 — manifest schema v1 round-trip
# ---------------------------------------------------------------------------


def test_manifest_schema_v1_round_trip():
    files = [
        {"path": "decoded-jd/netflix-data-analyst-2026-04.md",
         "kind": export.KIND_DECODED_JD, "size": 1234},
        {"path": "resume/netflix-data-analyst-2026-04.docx",
         "kind": export.KIND_RESUME_DOCX, "size": 28910},
    ]
    manifest = export._build_manifest(
        company="netflix",
        role_slug="data-analyst",
        application_month="2026-04",
        status="submitted",
        files=files,
    )

    # All required v1 keys present, well-typed.
    assert manifest["schema_version"] == 1
    assert isinstance(manifest["schema_version"], int)
    assert manifest["company"] == "netflix"
    assert manifest["role_slug"] == "data-analyst"
    assert manifest["application_month"] == "2026-04"
    assert manifest["status"] == "submitted"
    assert isinstance(manifest["files"], list)
    assert len(manifest["files"]) == 2
    for entry in manifest["files"]:
        assert set(entry.keys()) == {"path", "kind", "size"}
        assert isinstance(entry["path"], str)
        assert isinstance(entry["kind"], str)
        assert isinstance(entry["size"], int)

    # R1: no `generated_at` inside the in-zip manifest.
    assert "generated_at" not in manifest, (
        "Session 12 brief R1: manifest.json must omit generated_at — "
        "wall-clock data lives in website/v2/exports/index.json instead"
    )

    # JSON serialization round-trips losslessly.
    raw = export._serialize_manifest(manifest)
    decoded = json.loads(raw)
    assert decoded == manifest


def test_manifest_files_are_sorted_by_path():
    """Manifest determinism: files list is sorted ascending by path."""
    files = [
        {"path": "z/last.md", "kind": "x", "size": 1},
        {"path": "a/first.md", "kind": "x", "size": 1},
        {"path": "m/middle.md", "kind": "x", "size": 1},
    ]
    manifest = export._build_manifest(
        company="c", role_slug="r", application_month="2026-01",
        status="open", files=files,
    )
    paths = [f["path"] for f in manifest["files"]]
    assert paths == sorted(paths)


def test_serialize_manifest_is_byte_stable():
    """Same manifest dict → identical bytes across calls (sort_keys + indent)."""
    files = [
        {"path": "b.md", "kind": "x", "size": 2},
        {"path": "a.md", "kind": "x", "size": 1},
    ]
    m = export._build_manifest(
        company="c", role_slug="r", application_month="2026-01",
        status="open", files=files,
    )
    a = export._serialize_manifest(m)
    b = export._serialize_manifest(m)
    assert a == b
    assert a.endswith(b"\n"), "serialized manifest should end with a newline"


# ---------------------------------------------------------------------------
# Block 2 — id parser + status validator (used by Block 3+)
# ---------------------------------------------------------------------------


def test_parse_company_role_simple_id():
    assert export._parse_company_role("netflix-data-analyst-2026-04") == (
        "netflix", "data-analyst", "2026-04"
    )


def test_parse_company_role_multi_hyphen_role():
    assert export._parse_company_role(
        "disney-lead-data-analyst-2026-04"
    ) == ("disney", "lead-data-analyst", "2026-04")


@pytest.mark.parametrize("bad", [
    "",
    "Netflix-data-analyst-2026-04",  # uppercase company
    "netflix-data-analyst-2026-13",  # invalid month
    "netflix-2026-04",                # missing role-slug
    "netflix_data_analyst_2026_04",   # underscores
    "netflix-data-analyst-2026",      # missing month token
])
def test_parse_company_role_rejects_malformed(bad):
    from uja_host.tools.file_tools import ToolError
    with pytest.raises(ToolError):
        export._parse_company_role(bad)


def test_validate_status_accepts_allowlist():
    for s in {"open", "submitted", "interviewing", "offer", "closed", "rejected"}:
        assert export._validate_status(s) == s


def test_validate_status_rejects_unknown():
    from uja_host.tools.file_tools import ToolError
    with pytest.raises(ToolError):
        export._validate_status("draft")
    with pytest.raises(ToolError):
        export._validate_status("")
