# Session 13 brief — Phase 25 (v2 site rebuild, target v0.2.3)

**Target:** rebuild `website/v2/` as a static three-section delivery hub — Application packages, Config templates, About — driven by `exports/index.json` and `templates/index.json` produced by Phase 24's `export_application` tool. Replace the "v0.2.0 is in the oven" placeholder. Tag `v0.2.3` end of session, **on top of the merged Phase 24 + Phase 25 stack**.

**Estimated time:** 3-4 hours. Two-block shape: a Canva MCP visual exploration block (or text-wireframe fallback) before the implementation block. Smaller code surface than Phase 24 (no MCP, no Python — pure HTML/CSS/JS) but more design density.

**Surface:** intended for a Claude Code Dispatch session launched via `bash scripts/dispatch-session.sh 13`. Equally executable from a regular Cowork session.

**Prerequisite — non-trivial:** Phase 24 (PR #7, branch `phase24/export-pipeline`, 5 commits, 87 tests passing) is **open against `main` but NOT merged**. Session 13 stacks on top of it. The Session 13 implementation worktree must branch from **`phase24/export-pipeline`**, not from `main`. Commits land on a new branch like `phase25/v2-site-rebuild` whose base is `phase24/export-pipeline`. The Phase 24 + Phase 25 work then reviews + merges as one combined unit, not as two independent PRs. The session brief itself (this doc) is pure docs and lives on a feature branch off `main` — separate concern.

---

## You are an autonomous Phase 25 implementation agent

You are not waiting for the originating Cowork session to approve every micro-decision. You are the planner, executor, evaluator, and quality gate. Drive Phase 25 to a tagged `v0.2.3` release stacked on top of Phase 24.

If something genuinely blocks you (an ambiguity the orientation files don't resolve, the Canva MCP isn't available and you need to choose a fallback, an `index.json` shape that differs from what this brief assumes), surface it and ask. Do not improvise around the ADR; do improvise around incidental issues.

**If the brief and the orientation files disagree, the orientation files win.** This brief is a derived plan, not a re-statement of the ADR. ADR-002 D4 + SPEC §14 Phase 25 row + the on-branch shape of `host/uja_mcp/tools/export.py` on `phase24/export-pipeline` are the source of truth.

---

## Orientation — read in this order before any code

1. **`CLAUDE.md`** — project structure, working principles (HITL / Atomic / Deterministic / Evidence-based), Dispatch-session pattern, doc freshness protocol.
2. **`SPEC.md` §14** — committed phase plan. You are implementing **Phase 25**.
3. **`docs/ADR-002-architecture-rethink.md` §D4** — load-bearing. The "What the site serves" subsection enumerates the three sections; "How the site indexes itself" pins the static `index.html` + small JS pattern; "Visual style" pins the guardrails (no hero with marketing claim, no gradient buttons, no emoji, no AI branding, system font stack, sky → pink gradient as accent only, `noindex` + `robots.txt: Disallow /`).
4. **`docs/session-12-brief.md`** — the immediate predecessor. Sections to internalize: "Resolved decisions" (R1 / R2 / R3 — the export schema reflects all three) and the manifest / index.json schemas in Block 2 + Block 4.
5. **The `phase24/export-pipeline` branch contents** — read these without checking out. The shape of what Phase 25 renders is committed at `origin/phase24/export-pipeline`:
   - `git show origin/phase24/export-pipeline:host/uja_mcp/tools/export.py` — read end-to-end. Critical sections: `_build_manifest` (in-zip manifest schema v1, no `generated_at`), `_update_exports_index` (the row schema Phase 25 renders), `_sort_index_exports` (sort order: `application_month` desc, then `company` asc — the renderer should NOT re-sort, just preserve), `_render_readme` (in-zip README; not relevant to the site renderer but useful for tone/voice reference).
   - `git show origin/phase24/export-pipeline:host/tests/test_export_application.py` — the row-shape contract under test (use the assertions in `test_index_json_*` as the schema spec).
6. **The actual `exports/index.json` row shape (committed in Phase 24)** — copied here for ground-truth reference, since Phase 25 renders this verbatim:
   ```json
   {
     "filename": "<company-role-slug-yyyy-mm>.zip",
     "company": "<lowercase-company>",
     "role": "<lowercase-role-slug>",
     "application_month": "YYYY-MM",
     "status": "open|submitted|interviewing|offer|closed|rejected",
     "size_bytes": <int>,
     "generated_at": "YYYY-MM-DDTHH:MM:SSZ",
     "manifest_path": "<filename>.zip#manifest.json"
   }
   ```
   The wrapper is `{"schema_version": 1, "exports": [...]}`. Empty array on first creation.
7. **`website/v2/index.html`** — the current placeholder ("v0.2.0 is in the oven"). Phase 25 replaces it end-to-end.
8. **`website/v2/`** directory shape — current contents: `index.html`, `netlify.toml`, `robots.txt`, `assets/` (logo.svg, favicon.svg, favicon-32.png, apple-touch-icon.png). After Phase 25: also `exports/index.json` (initial empty array — created at runtime by the export tool, but the directory must exist; commit a placeholder `index.json` so the renderer doesn't 404 on first deploy) and `templates/index.json` + `templates/<files>` (committed by Phase 25; see Block 3).
9. **`website/index.html`** (the v1 site, for stylistic reference) — confirms the existing brand pattern: Tailwind via the `@tailwindcss/browser@4` CDN script, `gradient-text` class for the sky → pink accent, system font stack, `noindex`. Phase 25 inherits this pattern (see "Resolved decision: framework choice" below — which contradicts a line in the user's instructions).
10. **`scripts/sync_to_public_v2.py`** — the allowlist. Current entry `("website/v2", "website")` rewrites src `website/v2/` → dst `website/`. So everything Phase 25 puts under `website/v2/` lands at the deploy-source root after sync. Phase 25 must verify the `("website/v2", "website")` rewrite still covers `exports/` and `templates/` recursively — `shutil.copytree` recurses by default, so no allowlist change is needed. (This contradicts the user's instruction; see "Resolved decision: allowlist update" below.)
11. **`references/cowork-mcp-config-snippet.json`** — confirms Phase 25 doesn't touch MCP. The renderer is pure static; the export tool (which Cowork invokes through the MCP server) is the only producer of `exports/index.json`.

---

## Resolved decisions

These were ambiguities surfaced from the Phase 24 ship + the Session 13 brief input. Resolved up-front so the Dispatch agent doesn't need to escalate.

### R1 — Display-name prettification is client-side, not a schema change

**Decision:** Phase 24's `index.json` rows store `company` and `role` in the canonical lowercase form (e.g. `"netflix"`, `"data-analyst"`). The Phase 25 renderer prettifies on display: company → Title Case (split on spaces, capitalize each word; the company field is single-token so it's just `.charAt(0).toUpperCase()`); role → kebab-to-Title-Case (split on `-`, capitalize each word, join with spaces).

**Why:** Round-tripping through Title Case in the export tool would couple the export pipeline's identity contract to display concerns. The lowercase canonical form is load-bearing for filename matching downstream (R2 / R3 from Session 12). Prettification at the edge is the right place — same reason CSS `text-transform: capitalize` exists.

**How to apply:** the renderer JS includes a small `prettify(kind, value)` helper. Two cases handled: `kind === "company"` and `kind === "role"`. No regex — a `split` / `map` / `join` is enough. Add a unit-style verification in `tests/site-renderer.test.html` (see Block 2 below) covering both cases plus the edge case of an already-Title-Cased input (idempotent).

**Do NOT** revert Phase 24's lowercase choice. The schema stays as-is.

### R2 — `manifest_path` is metadata, not a render input

**Decision:** Phase 24's `manifest_path` field uses the URL-fragment style `"<filename>.zip#manifest.json"`. Phase 25's cards do **not** fetch + unzip the zip to read `manifest.json` on render. The card data — `company`, `role`, `application_month`, `status`, `size_bytes`, `filename` — is already fully present in the `index.json` row.

**Why:** Reading inside a zip from the browser would require a JS unzip dependency (jszip ~30 KB minified) for marginal value. The site is a delivery hub; the user clicks the download link to get the manifest. `manifest_path` exists for downstream tooling that wants to lazy-load detail; v0.2.3's cards don't need it.

**How to apply:** the renderer ignores `manifest_path` entirely. Document this in a code comment at the top of `app.js` so a future developer who wonders "why is this field unused" knows it's deliberate.

### R3 — Empty-state handling is friendly, not error-y

**Decision:** when `exports/index.json` is missing, has `{"schema_version": 1, "exports": []}`, or returns a non-200 status, the Application Packages section renders a friendly empty-state block (no thrown errors, no console spam). Same for `templates/index.json`.

**Why:** the v1 site's first deploy had nothing in `downloads/` either, and the muscle memory is "it should look intentional, not broken." The status here is "first deploy / no exports yet" — the right UI is a one-line note + maybe a faint how-to hint, not a stack trace.

**How to apply:** wrap the fetch in `try { ... } catch { renderEmptyState(section); return; }`. The empty-state renderer for "Application packages" is one paragraph: "No application packages yet. The export pipeline writes them here as Cowork emits them." For "Config templates": "No config templates published yet."

If `index.json` is present but malformed (parse error), surface it as a console warning AND the friendly empty state. Don't crash the page.

### R4 — Framework choice: keep Tailwind via CDN browser script (overrides user instruction)

**Decision:** The renderer continues the v1 / v2-placeholder pattern of using `@tailwindcss/browser@4` via CDN, plus a small inline `<style>` block for the brand gradient. **NOT** a hand-rolled CSS file. **NOT** a build step.

**Why this overrides a line in the user's instructions:** the brief input I was given said "Tailwind is NOT brought in for the v2 site (v1 didn't have it...)". Inspecting `website/index.html` (the v1 production site) shows it DOES use Tailwind via the browser CDN script. So does the current v2 placeholder. Switching to a hand-rolled CSS file would diverge from the established pattern, force me to reinvent the spacing / color / responsive utilities Tailwind already gives us, and risk visual drift from the brand. The user's instruction had a factual premise that doesn't hold up; the corrected decision is "match the v1 site's framework choice."

**How to apply:** keep the `<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>` line. Keep the inline `<style>` block scoped to the `.gradient-text` and any custom utilities that don't have a Tailwind equivalent. No npm, no build, no bundler.

**If the orchestrator (Cowork session) wants the truly framework-free path,** the answer is "rip out Tailwind from v1 first as a Phase 26-ish cleanup," not "diverge in Phase 25."

### R5 — `sync_to_public_v2.py` allowlist update is a NO-OP for Phase 25 (overrides user instruction)

**Decision:** Phase 25 does NOT need to touch `scripts/sync_to_public_v2.py`. The existing entry `("website/v2", "website")` already recursively syncs everything under `website/v2/` (including `exports/` and `templates/`) to deploy-source root via `shutil.copytree`. No allowlist line to add.

**Why this overrides a line in the user's instructions:** I checked `scripts/sync_to_public_v2.py`. The `copy_one` function calls `shutil.copytree(src, dst, dirs_exist_ok=True)` for directory entries, which recurses. The existing `("website/v2", "website")` entry is sufficient. Adding `("website/v2/exports", "website/exports")` would be redundant and could create double-copy edge cases (the EXCLUDE_DST list operates on dst paths; an explicit nested entry wouldn't break things but adds maintenance for nothing).

**How to apply:** the Phase 25 implementation does not modify `scripts/sync_to_public_v2.py`. If a smoke test of the sync (Block 4 below) reveals that `exports/` or `templates/` is NOT propagating, surface it and we'll add the entry.

### R6 — Commit a placeholder `exports/index.json` so the renderer doesn't 404 on first deploy

**Decision:** Phase 25 commits an empty-but-valid `website/v2/exports/index.json` containing `{"schema_version": 1, "exports": []}`. The export tool (Phase 24) overwrites this file in place on first export.

**Why:** without this file, the very first Netlify deploy after Phase 25 lands will 404 on `./exports/index.json` and trigger R3's empty-state branch. That's correct behavior, but the friendly-empty-state path is for "no exports yet"; pre-committing the empty file matches the schema and avoids the 404 entry in browser dev tools. Also lets the renderer-test asserts that the JSON shape is parsed correctly without needing a fixture.

**How to apply:** create `website/v2/exports/index.json` in Block 1 with the empty-array payload + final newline. Do NOT add `exports/*.zip` or future zips to `.gitignore` — they're git-tracked artifacts (per Session 12 brief Success Criterion 8: "individual `*.zip` files inside it ARE NOT ignored either"). The empty index file goes in the same commit as the rest of Block 1.

---

## Deliverable — Block-by-Block

### Block 1 — Visual exploration + design lock

**Goal:** lock the visual direction before writing HTML/CSS. Per ADR-002 quality bar ("Canva MCP exploration before building, not after") and Session 9's quality bar reaffirmation.

- Try the **Canva MCP** first. Ask the user (or the dispatched session's environment) whether the Canva MCP is available. If yes: produce 2-3 design directions as Canva designs covering the three sections (Application packages / Config templates / About). Each direction should pin: header treatment, card layout (single column? grid?), typography, the sky → pink accent placement (subtle border? icon backdrop? section underline?), empty-state look. Surface the Canva URLs in the PR description.
- **If the Canva MCP is NOT available:** fallback to text wireframes. Create `docs/phase25-wireframes.md` (one file, ≤ 200 lines) with three ASCII-or-markdown wireframe directions. Same coverage. Same selection criteria.
- The Cowork session (orchestrator) picks one before Block 2 begins. The Dispatch agent surfaces the options as a comment on the open PR (Phase 25's draft PR; create it early in this block) and waits for the orchestrator's pick before pushing implementation commits. **This is the one HITL gate in Phase 25.**
- Atomic commit on branch `phase25/v2-site-rebuild` (base = `phase24/export-pipeline`): the wireframes file (if used) or a `docs/phase25-design-decisions.md` capturing which Canva direction was selected and why.

### Block 2 — `website/v2/index.html` rewrite + `website/v2/app.js` + `website/v2/styles.css`

- Rewrite `website/v2/index.html` end-to-end. Three sections in order: **Application packages** (top — primary content per ADR-002 D4 "the page opens with the application-package list"), **Config templates** (middle), **About** (bottom). Header: brand mark (logo.svg + "Ultimate Job Assist" + small "v0.2.3" badge). Footer: same shape as v1 (`No tracking. No analytics. No SaaS.`).
- `<meta name="robots" content="noindex,nofollow">` preserved verbatim.
- System font stack preserved verbatim.
- Tailwind via CDN browser script preserved (R4).
- Inline `<style>` block for `.gradient-text` preserved.
- `website/v2/app.js` (new):
  - On `DOMContentLoaded`, parallel-fetch `./exports/index.json` and `./templates/index.json`.
  - Render each section's cards from the parsed array.
  - Empty-state on missing or empty data (R3).
  - Prettification helper for company / role display (R1).
  - Card layout per the locked design from Block 1.
  - Each card on the Application packages section: download link with `download` attribute pointing at the zip filename (`./exports/<filename>`), human-readable size (`<size_bytes>` formatted via `Intl.NumberFormat` or a small KB/MB switch), status badge (the six allowlist values from Phase 24 R2 — distinct color per status; sky for `submitted`, slate for `open`, pink-tinted for `interviewing`, green for `offer`, slate-dim for `closed`, slate-dim for `rejected`), application month displayed verbatim (`YYYY-MM` is fine; no Intl.DateTimeFormat).
  - No frameworks. No bundler. ES modules optional but not required (the file is small enough that a single `<script defer>` is fine).
  - Total `app.js` should land under ~250 lines including comments and the empty-state markup.
- `website/v2/styles.css` (new, optional): only if Tailwind utilities can't cover it. Initial guidance: try to do everything with Tailwind classes; if a custom utility is needed (e.g. a precise sky → pink gradient border), put it here, not inline. Keep the file under 100 lines.
- `website/v2/exports/index.json` (new) per R6: `{"schema_version": 1, "exports": []}` + trailing newline.
- `website/v2/templates/index.json` (new): `{"schema_version": 1, "templates": []}` + trailing newline. The schema for templates is symmetric to exports — Phase 25 doesn't yet ship any templates; the populated file lands when the orchestrator decides what bracketed-placeholder templates to publish (parked as a v0.2.4-ish question, see "Out of scope" below).
- Atomic commit per logical change (or one if you prefer; both are fine — atomic = "one logical change," not "one file per commit"). Suggested split: (a) `index.html` skeleton + assets, (b) `app.js` + `styles.css`, (c) the two empty index.json files.

### Block 3 — Site-renderer test

- `website/v2/tests/site-renderer.test.html` (new): a single self-contained HTML page that (a) loads `app.js`, (b) injects three fixture `index.json` shapes (empty / single-row / multi-row across two months), (c) calls the renderer, (d) asserts the DOM landed as expected. Use `<details>` blocks + plain-text assertions (no testing framework — the file is openable in any browser and reports pass/fail visually). Cover:
  - Empty array → empty-state block visible, card grid invisible.
  - Single row → one card with the right prettified company/role + size in human units + status badge + working download link href.
  - Multi-row across two months in random insertion order → cards appear in the same sort order Phase 24 wrote them (descending by month).
  - Missing-fetch → empty-state block visible, console warning logged.
- This test file is the renderer's analog to Phase 24's `test_export_application.py` — it's the spec under glass, not a CI gate. Open the file in a browser to verify; check it in.
- Atomic commit.

### Block 4 — End-to-end smoke + PR

- Smoke (manual, document in PR description): from a fully-checked-out workdir on `phase25/v2-site-rebuild`, run a fresh `export_application` from a real per-application folder (Netflix or Waymo from `references/examples/` if those still exist; if not, hand-craft a minimum-viable `decoded-jds/` + `resumes/` pair with placeholder content). Verify the produced `exports/index.json` row appears in the rendered card on `file://...website/v2/index.html`. Re-run; verify the card updates in place (status changes propagate, size_bytes refreshes).
- Verify `python scripts/sync_to_public_v2.py --dry-run` shows `website/v2/exports/index.json` and `website/v2/templates/index.json` on the copy-list (per R5, no allowlist change should be needed). Paste the relevant lines of dry-run output into the PR description.
- Open ONE PR titled `Phase 25: v2 site rebuild (target v0.2.3)` against `main` from `phase25/v2-site-rebuild`, where the base of the branch is `phase24/export-pipeline`. The PR description must call out the stacked nature: "This PR stacks on `phase24/export-pipeline` (PR #7). Reviewing the combined Phase 24 + Phase 25 work as one unit per the orchestrator's preference. Merging this PR will only land cleanly after PR #7 merges OR the orchestrator targets the merge at `phase24/export-pipeline` instead of `main` to flatten the stack."
- **Do not merge yourself.** **Do not tag yourself.** The Cowork session reviews + merges with `--no-ff` after deciding the merge order, then cuts `v0.2.3` against the merge commit.
- Atomic commit (the PR-prep commits land in Block 2-3; this block adds nothing new on disk — it's the PR-open + smoke + handoff).

---

## Working principles (verbatim from CLAUDE.md — non-negotiable)

- **Human-in-the-loop.** Block 1's design lock is the one explicit HITL gate. R1-R6 above resolve every other axis up-front so the Dispatch agent doesn't need to escalate. If a new ambiguity surfaces (the Canva MCP isn't available AND the wireframe approach isn't yielding a clear winner; the Phase 24 `index.json` shape committed on the branch differs from this brief's R1 description; the sync script's behavior surprises you), surface it on the PR and wait.
- **Atomic.** One logical change per commit. Block 2's three suggested commits are still one logical change each — index.html skeleton, JS+CSS renderer, the two empty index.json files. Reverting any single piece should be possible without surgery on unrelated changes.
- **Deterministic.** No timestamps in committed artifacts. Sort orders match what Phase 24's `_sort_index_exports` produces (descending month, ascending company); the renderer should NOT re-sort. The empty `index.json` files have a fixed payload + trailing newline; same bytes across re-runs.
- **Evidence-based.** Every code-shape decision should trace to either ADR-002 §D4, this brief's R1-R6, the Phase 24 source on `phase24/export-pipeline` (cite by path + line), or `website/index.html` (the v1 site's pattern). The schema fields you render must match Phase 24's `_update_exports_index` output verbatim.

If the brief and the orientation files disagree, the orientation files win.

---

## Branch + PR mechanics

- **Base branch: `phase24/export-pipeline` (NOT `main`).** This is load-bearing per the user's preference. Phase 25's commits stack on top.
- **Feature branch: `phase25/v2-site-rebuild`.** Multiple atomic commits on it (one per Block above plus the suggested Block 2 split), one PR.
- PR mechanics: same as Phase 23 / 24. The `gh` CLI is still broken on this machine; PR creation + merge use `git credential fill` → REST API. Pattern documented in Sessions 8-12 SESSION_LOG entries.
- Credential handling: same `.session-secrets/` pattern from CLAUDE.md "Credential handling pattern (Session 8 — load-bearing)". PAT lives in `.session-secrets/`, never in chat, stripped from origin URL after operations.
- If you cannot push the feature branch (network or auth issue), output `git format-patch phase24/export-pipeline..HEAD --stdout` at end of session.

---

## Success criteria

`v0.2.3` ships when ALL of the following hold:

1. `website/v2/index.html` is rebuilt end-to-end with three sections (Application packages / Config templates / About) per ADR-002 D4 + the Block 1 locked design. The "v0.2.0 is in the oven" placeholder is gone.
2. `website/v2/app.js` exists and renders cards from `./exports/index.json` and `./templates/index.json` per Block 2 spec, including R1 prettification, R2 metadata-not-render, R3 empty-state handling.
3. `website/v2/exports/index.json` exists with `{"schema_version": 1, "exports": []}` (R6).
4. `website/v2/templates/index.json` exists with `{"schema_version": 1, "templates": []}`.
5. `website/v2/tests/site-renderer.test.html` exists and visually passes when opened in a browser (Block 3).
6. The end-to-end smoke (Block 4) succeeds: a fresh `export_application` run produces an `index.json` row that the renderer displays correctly; a re-run updates the card in place.
7. `python scripts/sync_to_public_v2.py --dry-run` shows `website/v2/exports/index.json` + `website/v2/templates/index.json` propagating to dst (R5 verified).
8. `noindex,nofollow` + `robots.txt: Disallow /` preserved verbatim from the placeholder.
9. Mobile-friendly: cards stack on viewports ≤ 640 px; verified by resizing the browser during Block 4 smoke.
10. The Phase 24 work on `phase24/export-pipeline` is unchanged — Phase 25's commits add files under `website/v2/`, they do NOT modify `host/uja_mcp/`, `host/uja_host/`, `host/tests/`, or any docs other than possibly `docs/phase25-wireframes.md` / `docs/phase25-design-decisions.md`.
11. The deprecated tree (`host/uja_host/api/chat.py`, `api/conversations.py`, `host/frontend/`) is unchanged from Sessions 10-12.
12. PR is open + ready for review, stacked on `phase24/export-pipeline`. Tag is cut by the originating Cowork session after merge — annotated `v0.2.3`, message references ADR-002 D4 + this brief.

---

## End-of-session deliverables (in your final message back)

1. The PR URL.
2. Block-by-block summary of what landed, with commit SHAs and the base branch (`phase24/export-pipeline`).
3. The Canva MCP design URLs (if used) OR the path to `docs/phase25-wireframes.md` (if fallback used). Plus the orchestrator's selected direction.
4. The end-to-end smoke result: the `index.json` row produced, the screenshot or HTML excerpt of the rendered card, the re-run delta.
5. The `python scripts/sync_to_public_v2.py --dry-run` output excerpt confirming R5.
6. Any ambiguity you resolved on your own + the rationale (in case the Cowork session disagrees). The R1-R6 axes should not need this; flag any other axis.
7. A note flagging the next session's work + any architectural surprises that should inform Phase 26 planning (most likely: what shape templates take when the orchestrator decides to publish them, anything you discovered about per-application zip sizes that the renderer should handle differently at scale).

---

## Out of scope for this session

- Anything in Phase 24 (already on `phase24/export-pipeline`; do NOT re-touch `host/uja_mcp/tools/export.py` or its tests).
- Any work in `host/uja_mcp/` or `host/uja_host/` — Phase 25 is purely site-side.
- Populating `website/v2/templates/` with actual templates (memory.md, tracker.md, base resume DOCX) — the renderer must handle them, but choosing what to publish is a v0.2.4-ish orchestrator decision.
- The v0.4.0 workflow tracker artifact (Track 7).
- ADR-003 / v0.3.0 reframe (parked).
- Any Tauri work.
- Touching the deprecated tree.
- Touching v1 canonical or v1 deploy-source.
- Touching v2 deploy-source directly.
- Re-raising the custom-domain question from Phase 13. Per ADR-002 D4 implementation implications, it gets re-raised at v0.2.x landing, not in Phase 25 itself. If you want to land a one-line note in `CLAUDE.md` "Current Status & What's Next" flagging "custom domain is now relevant," fine — but no action.
- Adding analytics, telemetry, or any external script beyond Tailwind CDN. Per the v1 footer: "No tracking. No analytics. No SaaS."
- Live-smoke-testing the v0.2.1 build (`live_smoke_phase23.md`) — Milan's responsibility.
- Live-smoke-testing the v0.2.2 build (`live_smoke_phase24.md`) — Milan's responsibility, post-Phase-24-merge.

---

## Questions for orchestrator (flag for review before approving the brief)

These are points where this brief deviates from the user's input. Please confirm or correct before the Dispatch session launches.

1. **R4 contradicts the user's "Tailwind is NOT brought in for the v2 site (v1 didn't have it)" instruction.** The v1 production site `website/index.html` and the current v2 placeholder both use Tailwind via the `@tailwindcss/browser@4` CDN script. R4 keeps Tailwind. If the orchestrator wants the truly framework-free path, this needs to be explicit, plus a separate Phase 26-ish ticket to rip Tailwind out of the v1 site too (otherwise Phase 25 diverges from the established pattern for no architectural reason).
2. **R5 contradicts the user's "Phase 25 owns adding `website/v2/exports/` to the allowlist" instruction.** The existing `("website/v2", "website")` entry already recursively syncs everything under `website/v2/`. Adding a nested entry would be redundant. If the orchestrator has a reason to want explicit nested entries (e.g. for visibility in the dry-run output), fine, but it's not a correctness requirement.
3. **The user's brief input said "Phase 24's PR #7" — verified: PR #7 against `main` from `phase24/export-pipeline`.** The branch's HEAD is `5879f3f`. If Phase 24 gets force-pushed (rebased) before Session 13 launches, the Dispatch agent should re-base its branch on the new tip — flag this in the launch instructions.
4. **The Phase 24 implementation references "five commits" in the user's input but the branch on origin shows five commits** (`fc77c92` Block 1 → `5879f3f` Block 5). Consistent. No-op.
5. **Templates section is rendered but un-populated.** The brief commits to rendering templates from `templates/index.json` but defers populating it. Confirm that's acceptable for v0.2.3 — the alternative is to either ship a starter set in this session (scope creep) or hide the Config templates section entirely until v0.2.4 (deviates from ADR-002 D4 "three sections, each on its own anchor").
6. **The brief assumes `references/examples/` may have been pruned** (per `EXCLUDE_DST` in `sync_to_public_v2.py`). For Block 4's smoke, the agent may need to hand-craft a fixture `decoded-jds/` + `resumes/` pair. Is that acceptable, or does the orchestrator have a preferred test application?

---

*End of brief.*
