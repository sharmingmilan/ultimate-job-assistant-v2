# Session 12 brief — Phase 24 (export pipeline, target v0.2.2)

**Target:** ship the `export_application(company_role, status)` MCP tool per ADR-002 D4. Walks per-output-type folders, validates a minimum-viable set, writes a deterministic per-application zip to `website/v2/exports/`, updates `website/v2/exports/index.json`. Tag `v0.2.2` end of session.

**Estimated time:** 2.5-3.5 hours. Smaller surface than Phase 23 (no protocol scaffold to stand up) but more design-decision density (determinism contract, manifest schema, idempotency on re-run).

**Surface:** intended for a Claude Code Dispatch session launched via `bash scripts/dispatch-session.sh 12`. Equally executable from a regular Cowork session.

**Prerequisite:** Session 11 (Phase 23 MCP server scaffold, v0.2.1) must be merged. The `build_server()` factoring from Phase 23 Block 3 is what lets Phase 24 tests drive `tools/call` for `export_application` against the same registration without process state.

---

## You are an autonomous Phase 24 implementation agent

You are not waiting for the originating Cowork session to approve every micro-decision. You are the planner, executor, evaluator, and quality gate. Drive Phase 24 to a tagged `v0.2.2` release.

If something genuinely blocks you (an ambiguity the orientation files don't resolve, a determinism property you can't satisfy without changing the ADR contract), surface it and ask. Do not improvise around the ADR; do improvise around incidental issues.

**If the brief and the orientation files disagree, the orientation files win.** This brief is a derived plan, not a re-statement of the ADR. ADR-002 D4 + SPEC §14 Phase 24 row are the source of truth.

---

## Orientation — read in this order before any code

1. **`CLAUDE.md`** — project structure, working principles (HITL / Atomic / Deterministic / Evidence-based), Dispatch-session pattern, credential handling pattern, doc freshness protocol.
2. **`SPEC.md` §14** — committed phase plan. You are implementing **Phase 24**. Phase 25 (v2 site rebuild) is the next session; do not start Phase 25 work in this session.
3. **`docs/ADR-002-architecture-rethink.md`** — load-bearing for this session.
   - **§D4** is the export pipeline contract: zip layout, `manifest.json` schema v1, where the zip gets built, how the site indexes itself, the `exports/index.json` schema v1, the determinism contract.
   - **§D1** for the MCP tool surface (where `export_application` slots in — last row of the table).
   - **§Open questions deferred from this ADR** — two of those (#2 "Export status field source-of-truth" and the absence of a `tracker.md` extension model) are resolved in this brief's "Resolved decisions" section below.
4. **`SESSION_LOG.md` Sessions 9 + 10 + 11 entries** — Session 9 = ADR-002 ship + v0.2.0 tag; Session 10 = Phase 22.5 deprecation marking (first Dispatch run); Session 11 = Phase 23 MCP server scaffold + v0.2.1 ship (second Dispatch run). Pay attention to Session 11's "Phase 24 input" sub-bullet under "Deferred to next session" — that's the architectural roadmap from the agent that just finished Phase 23.
5. **`host/uja_mcp/server.py`** — see how existing tools are registered. `export_application` adds one more `add_tool(...)` block in the same shape, with `ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)` (it writes new files but the operation is idempotent against re-runs by the determinism contract).
6. **`host/uja_mcp/tools/__init__.py`** + **`host/uja_mcp/tools/files.py`** + **`host/uja_mcp/tools/hitl.py`** — the existing facade pattern. `export.py` follows the same conventions: `_root()` helper, `ToolError` for bad inputs, plain Python (no FastMCP imports) so tests can call directly.
7. **`host/tests/test_mcp_server.py`** — protocol-level test pattern. `_call_tool_via_protocol(server, "export_application", {...})` is the call shape Phase 24's protocol-level test should mirror.
8. **`host/uja_host/sandbox.py`** + **`host/uja_host/tools/file_tools.py`** — sandbox helpers. The export pipeline reads from the project root (sandbox-bounded) and writes to `website/v2/exports/` (also under the project root, so the same sandbox covers it).
9. **`host/uja_host/db.py`** — current schema is v2. Phase 24 does NOT add a schema v3 `exports` table; `index.json` is the single source of truth for export rows (matches ADR-002 D4 language: "Maintained by the `export_application` MCP tool. Append-only on success.").
10. **The (possibly empty) v2 site state** — `website/v2/index.html`, `website/v2/exports/` (likely doesn't exist yet — Phase 24 creates it), `scripts/sync_to_public_v2.py` (Phase 24 does NOT touch the allowlist; Phase 25 owns that change per SPEC §14).
11. **The naming convention** — `[company]-[role-slug]-[YYYY-MM].[ext]`, defined in `CLAUDE.md`. The `company_role` argument to the MCP tool is exactly this triple (`<company>-<role-slug>-<YYYY-MM>`); see Block 2.

You may skip the deprecated tree (`host/uja_host/api/chat.py`, `api/conversations.py`, `host/frontend/`) — Phase 24 does not touch any of them.

---

## Resolved decisions (the three ambiguities Session 12 inherited from ADR-002)

These were genuine open questions when Phase 23 shipped. The originating Cowork session resolved them ahead of Phase 24. Implementer follows them as-decided; rationale preserved in case an edge case forces a revisit.

### R1 — `manifest.json` omits `generated_at`

**Decision:** the per-application `manifest.json` (inside the zip) does NOT carry a `generated_at` field. The information lives in the per-entry row of `website/v2/exports/index.json` instead (which has no determinism constraint).

**Why:** ADR-002 D4 commits to "Re-running `export_application` against the same on-disk state produces byte-identical output." A wall-clock `generated_at` inside the zip violates byte-identicality. Omitting it is the cleanest fix; the writeback timestamp lives in the site-level index.json where determinism is not contracted.

**How to apply:** the Block 2 manifest builder must not emit `generated_at`. ADR-002 D4's example manifest schema-v1 line `"generated_at": "2026-05-03T12:34:56Z"` is superseded by R1; flag this in the Block 2 commit message so a future reader who sees the ADR sample doesn't think the implementation drifted.

### R2 — `status` is an explicit input to `export_application`

**Decision:** the MCP tool signature is `export_application(company_role: str, status: str = "submitted") -> dict`. The caller (Cowork) is responsible for passing the current application status. The export pipeline does NOT parse `tracker.md` to derive status.

**Why:** ADR-002 §Open questions deferred from this ADR explicitly punted "Export status field source-of-truth" to Phase 24. Reading `tracker.md` would couple the export tool to the tracker's evolving shape (the v0.4.0 workflow tracker is going to reshape that file). The explicit-input pattern keeps the MCP tool single-purpose (zip + index update) and matches the rest of the surface.

**How to apply:** the function takes `status` as a string. Validate it against an allowlist `{"open", "submitted", "interviewing", "offer", "closed", "rejected"}` and raise `ToolError` for unknown values. The status flows into both the per-application `manifest.json` (`status` field) and the `exports/index.json` row (`status` field) — they stay in lockstep within a single export call. If a re-export passes a different status, the in-place update from Block 4 picks up the new value; both surfaces update together.

### R3 — Portfolio subfolder identity: strict prefix match, singular

**Decision:** Phase 24 looks for exactly one folder, `portfolio/<id>/`, where `<id>` equals the `company_role` argument. If present, its contents are recursively included in the zip under `portfolio/`. If absent, the portfolio section is silently omitted (it's optional per the minimum-viable set).

**Why:** ADR-002 D4's portfolio layout (`portfolio/<project-slug>/`) didn't pin down whether one application can have multiple project subfolders. The strict-prefix-singular contract is tighter, easier to test, and matches the current convention in `CLAUDE.md` (one application = one portfolio folder). Multi-project-per-application is a real future case but no current real applications hit it; defer until v0.2.4 if it comes up.

**How to apply:** Block 3's portfolio walker resolves exactly `portfolio/<id>/` and recurses inside. No glob, no scan. Unknown subfolders under `portfolio/` are not touched.

---

## Deliverable — Block-by-Block

### Block 1 — `host/uja_mcp/tools/export.py` skeleton + `tools/__init__.py` update

- Create `host/uja_mcp/tools/export.py` with:
  - Module docstring (4-8 lines): what it implements (ADR-002 D4), why it lives in the MCP layer not `host/uja_host/` (it's a net-new capability with no FastAPI predecessor; lives where it's used), the determinism contract one-liner.
  - `_root()` helper (same shape as `tools/files.py`).
  - `export_application(company_role: str, status: str = "submitted") -> dict` — function with full docstring describing inputs (per R2), outputs, error modes, the determinism contract (per R1). Body is a single `raise NotImplementedError` placeholder for Block 1; Block 2-3 fill it in.
- Update `host/uja_mcp/tools/__init__.py`:
  - Replace the `# Note: export_application is Phase 24 ...` placeholder with the live entry: `export.py — export_application. Walks per-output-type folders, writes a deterministic zip to website/v2/exports/, updates exports/index.json. ADR-002 D4.`
- Atomic commit on branch `phase24/export-pipeline` (umbrella branch, all blocks land as atomic commits on it).

### Block 2 — Deterministic zip writer + `manifest.json` schema

- Implement the deterministic zip writer as a pure function inside `tools/export.py` (or a `_zip.py` sibling if you prefer; both are fine). Contract:
  - Input: an in-memory list of `(arcname, bytes)` tuples and a target output path.
  - Sort the input by `arcname` before writing.
  - Use `zipfile.ZipFile(..., compression=zipfile.ZIP_DEFLATED, compresslevel=6)` (pin the compression level explicitly — the default differs across Python versions in practice).
  - Zero the timestamps in each entry's `ZipInfo` (`date_time = (1980, 1, 1, 0, 0, 0)` — the ZIP epoch).
  - Set `ZipInfo.external_attr` deterministically (e.g. `0o644 << 16` for files, `0o755 << 16 | 0x10` for directories) so file mode bits don't drift.
  - No global ZIP comment.
- Implement the `manifest.json` v1 builder (separate pure function). Schema follows ADR-002 D4 verbatim **with R1 applied** (no `generated_at` field). Required keys: `schema_version`, `company`, `role_slug`, `application_month`, `files` (list of `{path, kind, size}`), `status`. Per-file `kind` enum: `decoded_jd`, `resume_docx`, `resume_pdf`, `score_before`, `score_after`, `speaking_points_md`, `speaking_points_pdf`, `cover_letter_md`, `cover_letter_pdf`, `portfolio`, `networking`.
- Tests in `host/tests/test_export_application.py`:
  - `test_zip_bytes_are_deterministic_across_runs` — write same inputs twice, assert byte-identical (`hashlib.sha256` comparison).
  - `test_zip_bytes_are_deterministic_across_input_ordering` — shuffle the input list, assert byte-identical output.
  - `test_manifest_schema_v1_round_trip` — generate, load, validate every spec'd field is present and well-typed; assert `generated_at` is NOT present (R1 enforcement).
- Atomic commit.

### Block 3 — Per-output-type folder walk + minimum-viable set validation

- Implement the folder walker. For a given `<company>-<role-slug>-<YYYY-MM>` identifier, find files matching that pattern under each of the per-output-type folders. The mapping (from ADR-002 D4 zip layout):

  | Source folder | Target zip subfolder | Pattern |
  |---|---|---|
  | `decoded-jds/` | `decoded-jd/` | `<id>.md` |
  | `resumes/` | `resume/` | `<id>.docx` + `<id>.pdf` |
  | `scores/` | `scores/` | `<id>-before.md` + `<id>-after.md` (after is optional) |
  | `speaking-points/` | `speaking-points/` | `<id>.md` + `<id>.pdf` |
  | `cover-letters/` | `cover-letter/` | `<id>.md` + `<id>.pdf` (whole folder optional) |
  | `portfolio/<id>/` | `portfolio/` | recursive copy of exactly that one subfolder per R3 |
  | `networking/` | `networking/` | files matching `<id>*.md` (loose; networking is an open-shape folder per CLAUDE.md) |

- Implement minimum-viable set validation. Required (export fails with `ToolError` if missing): the decoded JD `.md` and the resume `.docx`. Everything else is optional and silently omitted from the zip if absent (recorded as such in `manifest.files` by simple absence — `kind` enum's optional values just don't appear).
- Validate `status` against the allowlist from R2: `{"open", "submitted", "interviewing", "offer", "closed", "rejected"}`. Unknown → `ToolError`.
- Generate the human-readable `README.md` inside the zip (one short markdown file listing what's included with the same per-output-type grouping, sorted deterministically). Body schema: see SPEC §14 Phase 24 row + ADR-002 D4. Keep it under 60 lines, no emoji, no marketing voice — same tone as `host/frontend/README.md`. The README must NOT include any timestamp (R1 spirit — the zip is deterministic top to bottom).
- All paths route through `resolve_within_root` (sandbox-bounded). The export reads from the project root and writes to `<root>/website/v2/exports/<id>.zip`; both endpoints are inside the root, so one sandbox covers it.
- Tests:
  - `test_export_minimum_viable_decoded_jd_and_resume_required` — fixture project with only the decoded JD and resume DOCX → success. Drop either → `ToolError`.
  - `test_export_optional_outputs_are_silently_omitted` — fixture with no scores/cover-letter/portfolio → manifest reflects absence; zip contains only the present files.
  - `test_export_paths_are_sandbox_bounded` — symlink shenanigans rejected.
  - `test_export_portfolio_subfolder_recursion` — `portfolio/<id>/` with multiple files copies into the zip preserving subfolder shape.
  - `test_export_status_allowlist` — valid statuses accepted; unknown status raises `ToolError`.
- Atomic commit.

### Block 4 — `website/v2/exports/index.json` maintenance

- After a successful export, append/update an entry in `<root>/website/v2/exports/index.json`. Schema v1 from ADR-002 D4 — including the per-row `generated_at` (this one IS a real timestamp; R1 affects only the per-app `manifest.json`, not the site-level index).
- Idempotency: if the export is re-run for the same `<id>`, **update** the existing row in place rather than appending a duplicate. Identity is the `filename` field. The row's `status` and `generated_at` and `size_bytes` all refresh.
- File doesn't exist on first run → create it with `{"schema_version": 1, "exports": []}` plus the new entry.
- Sort `exports` array by `application_month` descending, then `company` ascending, on every write — so the file's diff is stable across re-runs (even though `generated_at` itself is not).
- Tests:
  - `test_index_json_created_on_first_export` — empty `website/v2/exports/` → file appears with one entry.
  - `test_index_json_updated_in_place_on_re_export` — same `<id>` exported twice → one row, not two; status reflects the second call's value.
  - `test_index_json_sort_order_is_stable` — three exports across two months in random order → rows sorted descending by month.
- Atomic commit.

### Block 5 — Register `export_application` in `server.py` + protocol test + live smoke

- Add the `mcp.add_tool(export.export_application, name="export_application", annotations=ToolAnnotations(...))` block to `host/uja_mcp/server.py`. Suggested annotations: `readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False, title="Export Application Package"`. Update the server module docstring's tool-surface comment to include `export_application` (and remove the "Phase 24 deferred" note).
- Update `EXPECTED_TOOL_NAMES` in `host/tests/test_mcp_server.py` to 13 tools. Add one happy-path protocol-level test driving `tools/call` for `export_application` against a fully-populated fixture project, asserting `isError=False`, the manifest payload matches, the zip lands at the expected path, and (per R1) the zip is byte-identical to a re-run via sha256 compare.
- Add `host/tests/live_smoke_phase24.md` (Markdown checklist, mirror `live_smoke_phase23.md`'s shape — six checks max). Coverage: register MCP, `tools/list` shows 13 tools (export_application present), one happy-path export against a real per-application folder, verify zip exists at expected path, verify `index.json` updated, verify re-run is byte-identical (sha256 compare).
- Atomic commit.

### Block 6 — PR + tag

- Open one PR titled `Phase 24: export pipeline (export_application, target v0.2.2)` against `main` from `phase24/export-pipeline`. PR body: bullet list of files touched + a one-line rationale per file + acceptance-gate confirmation (pytest line count, zip determinism sha256 from a smoke run, MCP server starts cleanly with `export_application` in the tool list).
- **Do not merge yourself.** The originating Cowork session reviews + merges with `--no-ff`.
- **Do not tag yourself.** The Cowork session cuts the `v0.2.2` tag against the merge commit after merge — annotated tag, message references ADR-002 D4 + this brief.

---

## Working principles (verbatim from CLAUDE.md — non-negotiable)

- **Human-in-the-loop.** Anywhere the brief or ADR genuinely doesn't decide, ask before improvising. The three "Resolved decisions" above mean Phase 24 should not need to escalate on those specific axes.
- **Atomic.** One logical change per commit. Each Block above maps to one commit, not five.
- **Deterministic.** The zip's bytes are the load-bearing artifact of this phase. Tests must enforce byte-identical re-runs; the implementation must not lean on wall-clock time, environment vars, or insertion order. R1 is what makes this achievable inside the manifest.
- **Evidence-based.** Every code-shape decision should trace to either ADR-002 §D4, this brief's "Resolved decisions" section, or a concrete file in `host/uja_mcp/` you can cite by path + line. The ZIP determinism techniques (sorted ordering, fixed `compresslevel`, zeroed `date_time`, deterministic `external_attr`) are well-trodden ground; cite a reference if you go beyond what the Python `zipfile` docs provide.

If the brief and the orientation files disagree, the orientation files win.

---

## Branch + PR mechanics

- One umbrella branch: `phase24/export-pipeline`. Multiple atomic commits on it (one per Block above), one PR.
- PR mechanics: same as Phase 23. The `gh` CLI is still broken on this machine; PR creation + merge use `git credential fill` → REST API. Pattern is documented in Sessions 8-11 SESSION_LOG entries.
- Credential handling: same `.session-secrets/` pattern from CLAUDE.md "Credential handling pattern (Session 8 — load-bearing)". PAT lives in `.session-secrets/`, never in chat, stripped from origin URL after operations.
- If you cannot push to a feature branch (network or auth issue), output `git format-patch main..HEAD --stdout` at end of session.

---

## Success criteria

`v0.2.2` ships when ALL of the following hold:

1. `host/uja_mcp/tools/export.py` exists; implements `export_application(company_role: str, status: str = "submitted") -> dict` per Block 2-4 specs and the three resolved decisions.
2. `host/tests/test_export_application.py` exists and covers: deterministic-bytes-across-runs, deterministic-bytes-across-input-ordering, manifest schema v1 round-trip (including `generated_at` absence per R1), minimum-viable validation (positive + negative), optional-outputs handling, sandbox-bounded paths, portfolio subfolder recursion (R3), status allowlist (R2), `index.json` first-run / in-place-update / sort-order behavior.
3. `host/uja_mcp/server.py` registers `export_application` with appropriate `ToolAnnotations`. `EXPECTED_TOOL_NAMES` in `test_mcp_server.py` is 13. One new happy-path protocol-level test for `export_application` lands.
4. `host/tests/live_smoke_phase24.md` exists (≤ 200 lines, ≤ 6 checks, mirrors `live_smoke_phase23.md` shape).
5. `pytest -q` reports **55+ passing tests, 0 failed** (was 50 / 3 pre-Phase-24; expect ~5-10 new tests in Phase 24).
6. `python -m uja_mcp.server` still launches cleanly with the expanded tool surface.
7. Re-running `export_application` against the same on-disk inputs and the same `status` produces byte-identical zip output (verified by a `sha256sum` round-trip in the protocol-level test).
8. `website/v2/exports/` is created in the canonical repo with at least the empty `index.json` (`{"schema_version": 1, "exports": []}`) on first export. The directory is NOT in `.gitignore` (it ships); individual `*.zip` files inside it ARE NOT ignored either (the determinism contract makes them git-diffable). The Phase 25 question of mirroring this directory to deploy-source via `sync_to_public_v2.py` is explicitly out of scope.
9. The deprecated tree (`host/uja_host/api/chat.py`, `api/conversations.py`, `host/frontend/`) is unchanged from Session 11.
10. PR is open + ready for review; tag is cut by the originating Cowork session after merge.

---

## End-of-session deliverables (in your final message back)

1. The PR URL.
2. Block-by-block summary of what landed, with commit SHAs.
3. The `pytest -q` output line count + the test files that grew (`test_export_application.py`, `test_mcp_server.py`).
4. Confirmation that `python -m uja_mcp.server` boots cleanly with `export_application` registered (paste the first stderr log lines + the `tools/list` output if you ran one).
5. The sha256 of the smoke-test zip on first run AND on re-run, demonstrating byte-identicality.
6. Any ambiguity you resolved on your own + the rationale (in case the Cowork session disagrees). The three R1/R2/R3 axes should not need this; flag any other axis you encountered.
7. A note flagging Phase 25 as the next session's work + any architectural surprises that should inform Phase 25's brief (most likely: index.json shape decisions surfaced during Block 4, anything you discovered about per-application folder shapes that the v2 site renderer needs to know).

---

## Out of scope for this session

- The v2 site rebuild (Phase 25, target v0.2.3).
- `scripts/sync_to_public_v2.py` allowlist updates for `website/v2/exports/` (Phase 25).
- Any schema v3 SQLite `exports` table — `index.json` is the single source of truth per ADR-002 D4.
- Parsing `tracker.md` for status — R2 makes status an explicit input.
- Multi-project-per-application portfolio support — R3 makes it singular for v0.2.2.
- The v0.4.0 workflow tracker artifact (Track 7).
- ADR-003 / v0.3.0 reframe (parked).
- Any Tauri work.
- Touching the deprecated tree (`host/uja_host/api/chat.py`, `conversations.py`, `host/frontend/`) — unchanged from Session 11.
- Touching v1 canonical or v1 deploy-source.
- Touching v2 deploy-source.
- Live-smoke-testing the v0.2.1 build (`live_smoke_phase23.md`) — that's Milan's responsibility per Session 11.
- Custom domain (Phase 13 carryover, re-raised in Phase 25 per ADR-002 D4 implementation implications).

---

*End of brief.*
