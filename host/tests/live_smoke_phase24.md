# Phase 24 live smoke checklist — `export_application` end-to-end

**Purpose.** Verify that `export_application` registers cleanly with
Cowork as a 13th tool on the `uja` MCP server, walks a real
per-application folder, writes a deterministic zip to
`website/v2/exports/`, and updates `website/v2/exports/index.json`.

Run AFTER the Phase 24 PR merges to `main` and the `v0.2.2` tag is cut.
Total time: ~10 minutes. Mirrors the shape of `live_smoke_phase23.md`.

---

## Prereqs

- A clean checkout of `main` at the `v0.2.2` tag.
- Python 3.11+ on PATH; the venv created by `start-uja-mcp.sh` is
  already populated with the `mcp` SDK.
- Cowork (Claude desktop) installed, signed in, and registered against
  the `uja` MCP server per Phase 23's smoke setup. If you have not
  done that, walk through `live_smoke_phase23.md` first.
- A project folder containing at least one fully-shaped
  per-application bundle. The example below assumes
  `netflix-data-analyst-2026-04`. Substitute your own id where
  appropriate.

Minimum-viable on disk for that id:

```
<project-root>/
├── decoded-jds/netflix-data-analyst-2026-04.md
└── resumes/netflix-data-analyst-2026-04.docx
```

Optional add-ons (any subset works):

```
resumes/netflix-data-analyst-2026-04.pdf
scores/netflix-data-analyst-2026-04-before.md
scores/netflix-data-analyst-2026-04-after.md
speaking-points/netflix-data-analyst-2026-04.md
speaking-points/netflix-data-analyst-2026-04.pdf
cover-letters/netflix-data-analyst-2026-04.md
cover-letters/netflix-data-analyst-2026-04.pdf
portfolio/netflix-data-analyst-2026-04/<files...>
networking/netflix-data-analyst-2026-04-outreach.md
```

---

## Smoke checks

Run each prompt below in a Cowork chat against the `uja` server.
Pass = the indicated tool is called and returns a sane payload.

### 1. tools/list — does Cowork see 13 tools (export_application present)?

> _Prompt:_ "List the MCP tools the `uja` server exposes."

Pass: Cowork lists 13 tools. The 12 from Phase 23 plus
`export_application`.

Fail: still 12. Cowork has a stale tool catalog — restart Cowork or
re-trigger the MCP refresh. If still 12 after restart, the launcher
is pointing at an older venv; re-run `start-uja-mcp.sh` and re-paste
the snippet into Cowork's MCP config.

### 2. happy path — export an application

> _Prompt:_ "Use the uja MCP server's export_application tool to bundle
> netflix-data-analyst-2026-04 with status 'submitted'."

Pass: Cowork calls `export_application` and returns a payload shaped
like:

```json
{
  "company_role": "netflix-data-analyst-2026-04",
  "zip_path": "website/v2/exports/netflix-data-analyst-2026-04.zip",
  "size_bytes": 12345,
  "sha256": "<hex>",
  "manifest": { "schema_version": 1, ... },
  "index_entry": { "filename": "netflix-data-analyst-2026-04.zip", ... }
}
```

Verify on disk:

```bash
ls -la <project-root>/website/v2/exports/
# Expect: netflix-data-analyst-2026-04.zip + index.json
```

Fail: `isError: true` with a "missing required file" message means the
decoded JD or resume DOCX is not where the pipeline expects it. Check
the paths against the prereq layout.

### 3. zip layout — manifest + README + per-output-type subfolders

```bash
unzip -l <project-root>/website/v2/exports/netflix-data-analyst-2026-04.zip
```

Pass: every entry is under
`netflix-data-analyst-2026-04/`. Top-level entries include
`manifest.json` and `README.md`. Per-output-type subfolders
(`decoded-jd/`, `resume/`, etc.) appear only for the files that
actually exist on disk.

```bash
unzip -p <project-root>/website/v2/exports/netflix-data-analyst-2026-04.zip \
  netflix-data-analyst-2026-04/manifest.json | python3 -m json.tool
```

Pass: `schema_version: 1`, `company`, `role_slug`, `application_month`,
`status`, `files: [...]`. NO `generated_at` field (Session 12 brief R1).

### 4. index.json — site data source updated

```bash
cat <project-root>/website/v2/exports/index.json
```

Pass: `{"schema_version": 1, "exports": [{"filename": "...", ...}]}`
with one row matching the export. The row carries `generated_at` (real
UTC timestamp ending in `Z`), `manifest_path` (zip-relative URL
fragment), and `size_bytes` matching `ls -l` of the zip.

### 5. determinism — re-run produces byte-identical zip bytes

> _Prompt:_ "Re-run the same export_application call again with the
> same inputs."

Pass: the tool returns; the zip on disk has the same sha256 as before:

```bash
shasum -a 256 <project-root>/website/v2/exports/netflix-data-analyst-2026-04.zip
# Run, save the digest. Re-run the export. Run shasum again.
# The two digests MUST be identical (Session 12 brief R1).
```

`index.json` will have changed (`generated_at` advanced; `size_bytes`
and `status` may have changed if the on-disk content shifted) — that
is intentional. The determinism contract applies only to the zip
itself.

### 6. status flow — re-export with a different status updates in place

> _Prompt:_ "Re-run export_application for the same id but with status
> 'interviewing'."

Pass: `index.json` still has exactly one row for that filename; its
`status` field is now `interviewing`. No duplicate row appended.

```bash
python3 -c "import json; idx=json.load(open('<project-root>/website/v2/exports/index.json')); rows=[r for r in idx['exports'] if r['filename']=='netflix-data-analyst-2026-04.zip']; print(len(rows), rows[0]['status'])"
# Expect: 1 interviewing
```

---

## Cleanup

Optional:

```bash
rm <project-root>/website/v2/exports/netflix-data-analyst-2026-04.zip
# Reset index.json by editing it directly; the next export will recreate.
```

---

## Reporting

If any check above fails, capture:

- The Cowork stderr log for the `uja` server (path varies by OS).
- The exact error text from the failed tool call.
- The line in this checklist that failed.
- For check 5: both sha256 digests if they differ.

Open an issue (or comment on the v0.2.2 tag PR) with that bundle. The
Phase 25 brief inherits any architectural surprises surfaced here —
particularly anything about the `index.json` shape that the v2 site
renderer needs to know.
