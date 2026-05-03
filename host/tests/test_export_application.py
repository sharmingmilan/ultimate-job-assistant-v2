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


# ---------------------------------------------------------------------------
# Block 3 — folder walker + minimum-viable validation + sandbox bounds
# ---------------------------------------------------------------------------


from uja_host import config as host_config  # noqa: E402
from uja_host.tools.file_tools import ToolError  # noqa: E402


_TEST_ID = "netflix-data-analyst-2026-04"


def _seed_min_viable(root: Path) -> None:
    """Drop the bare-minimum decoded JD + resume DOCX into `root`."""
    (root / "decoded-jds").mkdir(parents=True, exist_ok=True)
    (root / "decoded-jds" / f"{_TEST_ID}.md").write_text(
        "# Decoded JD\n\nminimum-viable fixture\n", encoding="utf-8"
    )
    (root / "resumes").mkdir(parents=True, exist_ok=True)
    # Real DOCX files are zips themselves; we use stable opaque bytes
    # because the export pipeline doesn't introspect them.
    (root / "resumes" / f"{_TEST_ID}.docx").write_bytes(
        b"PK\x03\x04fake-docx-fixture\x00\x00"
    )


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch) -> Path:
    """Configured project root for export tests."""
    monkeypatch.setattr(host_config, "get_project_root", lambda: tmp_path)
    return tmp_path


def test_export_minimum_viable_decoded_jd_and_resume_required(project_root: Path):
    """Both decoded JD and resume DOCX must exist; either missing → ToolError."""
    # Both present → success.
    _seed_min_viable(project_root)
    result = export.export_application(_TEST_ID)
    assert result["company_role"] == _TEST_ID
    assert (project_root / "website/v2/exports" / f"{_TEST_ID}.zip").exists()

    # Drop the decoded JD → ToolError.
    (project_root / "decoded-jds" / f"{_TEST_ID}.md").unlink()
    with pytest.raises(ToolError) as exc:
        export.export_application(_TEST_ID)
    assert "decoded-jds" in str(exc.value)

    # Drop the resume DOCX → ToolError (re-seed JD first).
    _seed_min_viable(project_root)
    (project_root / "resumes" / f"{_TEST_ID}.docx").unlink()
    with pytest.raises(ToolError) as exc:
        export.export_application(_TEST_ID)
    assert "resumes" in str(exc.value)


def test_export_optional_outputs_are_silently_omitted(project_root: Path):
    """Missing scores/cover-letter/portfolio/networking → omitted (not errored)."""
    _seed_min_viable(project_root)
    result = export.export_application(_TEST_ID)
    files = result["manifest"]["files"]
    kinds = {f["kind"] for f in files}
    # Only the two required kinds appear; nothing optional sneaks in.
    assert kinds == {export.KIND_DECODED_JD, export.KIND_RESUME_DOCX}
    paths = [f["path"] for f in files]
    assert paths == sorted(paths)
    assert not any("scores/" in p for p in paths)
    assert not any("cover-letter/" in p for p in paths)
    assert not any("portfolio/" in p for p in paths)
    assert not any("networking/" in p for p in paths)


def test_export_includes_all_optional_slots_when_present(project_root: Path):
    """All optional single-file slots flow into the manifest when on disk."""
    _seed_min_viable(project_root)
    # Resume PDF.
    (project_root / "resumes" / f"{_TEST_ID}.pdf").write_bytes(b"%PDF-1.4\n%fake\n")
    # Scores: before + after.
    (project_root / "scores").mkdir(parents=True, exist_ok=True)
    (project_root / "scores" / f"{_TEST_ID}-before.md").write_text(
        "# Score before\n", encoding="utf-8"
    )
    (project_root / "scores" / f"{_TEST_ID}-after.md").write_text(
        "# Score after\n", encoding="utf-8"
    )
    # Speaking points: md + pdf.
    (project_root / "speaking-points").mkdir(parents=True, exist_ok=True)
    (project_root / "speaking-points" / f"{_TEST_ID}.md").write_text(
        "# Speaking points\n", encoding="utf-8"
    )
    (project_root / "speaking-points" / f"{_TEST_ID}.pdf").write_bytes(
        b"%PDF-1.4\n%speaking\n"
    )
    # Cover letter: md + pdf.
    (project_root / "cover-letters").mkdir(parents=True, exist_ok=True)
    (project_root / "cover-letters" / f"{_TEST_ID}.md").write_text(
        "# Cover letter\n", encoding="utf-8"
    )
    (project_root / "cover-letters" / f"{_TEST_ID}.pdf").write_bytes(
        b"%PDF-1.4\n%cover\n"
    )

    result = export.export_application(_TEST_ID)
    kinds = {f["kind"] for f in result["manifest"]["files"]}
    assert kinds == {
        export.KIND_DECODED_JD,
        export.KIND_RESUME_DOCX,
        export.KIND_RESUME_PDF,
        export.KIND_SCORE_BEFORE,
        export.KIND_SCORE_AFTER,
        export.KIND_SPEAKING_POINTS_MD,
        export.KIND_SPEAKING_POINTS_PDF,
        export.KIND_COVER_LETTER_MD,
        export.KIND_COVER_LETTER_PDF,
    }


def test_export_paths_are_sandbox_bounded(project_root: Path, tmp_path_factory):
    """Symlink shenanigans pointing outside the project root are rejected."""
    _seed_min_viable(project_root)

    # Plant an external file that the symlink will point at.
    outside = tmp_path_factory.mktemp("outside") / "leak.md"
    outside.write_text("# secret\n", encoding="utf-8")

    # Replace decoded-jds/<id>.md with a symlink to the outside file.
    (project_root / "decoded-jds" / f"{_TEST_ID}.md").unlink()
    (project_root / "decoded-jds" / f"{_TEST_ID}.md").symlink_to(outside)

    with pytest.raises(ToolError) as exc:
        export.export_application(_TEST_ID)
    msg = str(exc.value).lower()
    # Either the sandbox check rejects the symlink target or the
    # required-file check rejects the dangling/escaping link.
    assert "sandbox" in msg or "outside" in msg or "decoded-jds" in msg


def test_export_portfolio_subfolder_recursion(project_root: Path):
    """`portfolio/<id>/` recurses into the zip preserving subfolder shape."""
    _seed_min_viable(project_root)
    pf = project_root / "portfolio" / _TEST_ID
    pf.mkdir(parents=True)
    (pf / "README.md").write_text("# Project README\n", encoding="utf-8")
    sub = pf / "data"
    sub.mkdir()
    (sub / "raw.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (sub / "notes.md").write_text("# notes\n", encoding="utf-8")

    result = export.export_application(_TEST_ID)
    portfolio_paths = sorted(
        f["path"] for f in result["manifest"]["files"]
        if f["kind"] == export.KIND_PORTFOLIO
    )
    assert portfolio_paths == [
        "portfolio/README.md",
        "portfolio/data/notes.md",
        "portfolio/data/raw.csv",
    ]


def test_export_unrelated_portfolio_subfolder_ignored(project_root: Path):
    """Other `portfolio/<other-id>/` subfolders are not pulled into the zip (R3)."""
    _seed_min_viable(project_root)
    other = project_root / "portfolio" / "google-some-other-2026-04"
    other.mkdir(parents=True)
    (other / "scratch.md").write_text("# scratch\n", encoding="utf-8")

    result = export.export_application(_TEST_ID)
    paths = [f["path"] for f in result["manifest"]["files"]]
    assert not any(p.startswith("portfolio/") for p in paths)


def test_export_networking_loose_glob(project_root: Path):
    """Networking folder picks up multiple files matching `<id>*.md`."""
    _seed_min_viable(project_root)
    net = project_root / "networking"
    net.mkdir()
    (net / f"{_TEST_ID}-outreach.md").write_text("# o\n", encoding="utf-8")
    (net / f"{_TEST_ID}-followups.md").write_text("# f\n", encoding="utf-8")
    # Files for OTHER applications must not be included.
    (net / "google-other-2026-04-outreach.md").write_text("# x\n", encoding="utf-8")

    result = export.export_application(_TEST_ID)
    net_paths = sorted(
        f["path"] for f in result["manifest"]["files"]
        if f["kind"] == export.KIND_NETWORKING
    )
    assert net_paths == [
        f"networking/{_TEST_ID}-followups.md",
        f"networking/{_TEST_ID}-outreach.md",
    ]


def test_export_status_allowlist(project_root: Path):
    """Valid statuses accepted; unknown raises ToolError."""
    _seed_min_viable(project_root)
    for s in {"open", "submitted", "interviewing", "offer", "closed", "rejected"}:
        result = export.export_application(_TEST_ID, status=s)
        assert result["manifest"]["status"] == s

    with pytest.raises(ToolError):
        export.export_application(_TEST_ID, status="draft")


def test_export_zip_contains_manifest_and_readme(project_root: Path):
    """The zip top-level contains <id>/manifest.json and <id>/README.md."""
    _seed_min_viable(project_root)
    export.export_application(_TEST_ID)
    zpath = project_root / "website/v2/exports" / f"{_TEST_ID}.zip"
    with zipfile.ZipFile(zpath) as zf:
        names = zf.namelist()
        assert f"{_TEST_ID}/manifest.json" in names
        assert f"{_TEST_ID}/README.md" in names
        # Manifest is well-formed and matches what the function returned.
        with zf.open(f"{_TEST_ID}/manifest.json") as f:
            parsed = json.loads(f.read().decode("utf-8"))
        assert parsed["company"] == "netflix"
        assert parsed["role_slug"] == "data-analyst"
        assert "generated_at" not in parsed  # R1 enforcement
        # README has no timestamp (R1 spirit).
        with zf.open(f"{_TEST_ID}/README.md") as f:
            readme = f.read().decode("utf-8")
        # Cheap timestamp-shape guard: no ISO-8601 date prefix.
        assert "2026-" not in readme.replace("2026-04", ""), (
            "README must not embed wall-clock timestamps"
        )


def test_export_returns_sha256_of_zip_bytes(project_root: Path):
    """`sha256` field matches a recomputed digest of the zip on disk."""
    _seed_min_viable(project_root)
    result = export.export_application(_TEST_ID)
    zpath = project_root / "website/v2/exports" / f"{_TEST_ID}.zip"
    expected = hashlib.sha256(zpath.read_bytes()).hexdigest()
    assert result["sha256"] == expected


def test_export_bytes_byte_identical_across_runs(project_root: Path):
    """End-to-end determinism: re-running yields byte-identical zip bytes."""
    _seed_min_viable(project_root)
    r1 = export.export_application(_TEST_ID, status="submitted")
    sha1 = r1["sha256"]
    r2 = export.export_application(_TEST_ID, status="submitted")
    sha2 = r2["sha256"]
    assert sha1 == sha2, "same inputs + same status must produce identical bytes"


def test_export_rejects_malformed_id(project_root: Path):
    with pytest.raises(ToolError):
        export.export_application("Netflix Data Analyst 2026/04")

