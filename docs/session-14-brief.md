# Phase 25 brief — v2 site rebuild (target v0.2.3)

**Target:** rebuild `website/v2/` as a static three-section delivery hub — Application packages, Config templates, About — driven by `exports/index.json` and `templates/index.json` produced by Phase 24's `export_application` tool. Replace the "v0.2.0 is in the oven" placeholder. Tag `v0.2.3` end of session, **on top of the merged Phase 24 + Phase 25 stack**.

**Estimated time:** 3-4 hours. Four-block shape: ADR-003 implementation pass first (palette + theme toggle + About + copy review), then `index.html` + `app.js` rewrite, then a self-contained renderer test, then end-to-end smoke + PR. Smaller code surface than Phase 24 (no MCP, no Python — pure HTML/CSS/JS) but more design density.

**Surface:** interactive Cowork session. Per the Session 13 → 14 handoff and the abandonment of the Dispatch pattern, all Phase 25 work runs in a single (or stacked) Cowork session with Milan in the room.

**Prerequisite — non-trivial:** Phase 24 (PR #7, branch `phase24/export-pipeline`, 5 commits, 87 tests passing) is **open against `main` but NOT merged**. Phase 25 stacks on top of it. The Phase 25 implementation worktree must branch from **`phase24/export-pipeline`**, not from `main`. Commits land on a new branch like `phase25/v2-site-rebuild` whose base is `phase24/export-pipeline`. The Phase 24 + Phase 25 work then reviews + merges as one combined unit, not as two independent PRs. The session brief itself (this doc) is pure docs and lives on a feature branch off `main` — separate concern.

---

## You are the Phase 25 implementation session

You and Milan execute Phase 25 together. Drive the work to a tagged `v0.2.3` release stacked on top of Phase 24, surfacing decisions for review and waiting for approval at named gates (HITL principle).

If something genuinely blocks you (an ambiguity the orientation files don't resolve, an `index.json` shape that differs from what this brief assumes, a Phase 24 detail that has shifted on the branch since this brief was written), surface it and ask. Do not improvise around the ADR; do improvise around incidental issues.

**If the brief and the orientation files disagree, the orientation files win.** This brief is a derived plan, not a re-statement of the ADRs. ADR-002 §D4 + ADR-003 D1-D8 + SPEC §14 Phase 25 row + the on-branch shape of `host/uja_mcp/tools/export.py` on `phase24/export-pipeline` are the source of truth.

---

## Orientation — read in this order before any code

1. **`CLAUDE.md`** — project structure, working principles (HITL / Atomic / Deterministic / Evidence-based), Cowork session workflow pattern, doc freshness protocol.
2. **`SPEC.md` §14** — committed phase plan. You are implementing **Phase 25**.
3. **`docs/ADR-002-architecture-rethink.md` §D4** — load-bearing. The "What the site serves" subsection enumerates the three sections; "How the site indexes itself" pins the static `index.html` + small JS pattern; "Visual style" pins the guardrails (no hero with marketing claim, no gradient buttons, no emoji, no AI branding, system font stack, sky → pink gradient as accent only, `noindex` + `robots.txt: Disallow /`).
4. **`docs/ADR-003-visual-identity.md`** — load-bearing. The eight decisions D1-D8 are locked design inputs for Phase 25: D1 flat list with status filter chips; D2 slate-950 dark default + light variant via `prefers-color-scheme` + explicit toggle; D3 mid-saturation translucent status pills; D4 single flat card list (daily-check-in cascade); D5 implicit privacy on homepage + About page carries context; D6 plain-without-clubby voice cluster; D7 no AI branding (confirms ADR-002 §D4); D8 cards immediately above the fold + thin top-bar only. Read end-to-end. The Decisions section + Cross-decision interactions are non-negotiable. Appendix A (concrete proposals) and Appendix B (voice examples) are starting points, not specifications.
5. **`docs/session-12-brief.md`** — Phase 24 predecessor. Sections to internalize: "Resolved decisions" (R1 / R2 / R3 — the export schema reflects all three) and the manifest / index.json schemas in Block 2 + Block 4.
6. **The `phase24/export-pipeline` branch contents** — read these without checking out. The shape of what Phase 25 renders is committed at `origin/phase24/export-pipeline`:
   - `git show origin/phase24/export-pipeline:host/uja_mcp/tools/export.py` — read end-to-end. Critical sections: `_build_manifest` (in-zip manifest schema v1, no `generated_at`), `_update_exports_index` (the row schema Phase 25 renders), `_sort_index_exports` (sort order: `application_month` desc, then `company` asc — the renderer should NOT re-sort, just preserve), `_render_readme` (in-zip README; not relevant to the site renderer but useful for tone/voice reference).
   - `git show origin/phase24/export-pipeline:host/tests/test_export_application.py` — the row-shape contract under test (use the assertions in `test_index_json_*` as the schema spec).
7. **The actual `exports/index.json` row shape (committed in Phase 24)** — copied here for ground-truth reference, since Phase 25 renders this verbatim:
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
8. **`website/v2/index.html`** — the current placeholder ("v0.2.0 is in the oven"). Phase 25 replaces it end-to-end.
9. **`website/v2/`** directory shape — current contents: `index.html`, `netlify.toml`, `robots.txt`, `assets/` (logo.svg, favicon.svg, favicon-32.png, apple-touch-icon.png). After Phase 25: also `exports/index.json` (initial empty array — created at runtime by the export tool, but the directory must exist; commit a placeholder `index.json` so the renderer doesn't 404 on first deploy), `templates/index.json` + `templates/<files>` (committed by Phase 25; see Block 3), and an About page or section per ADR-003 D5.
10. **`website/index.html`** (the v1 site, for stylistic reference) — confirms the existing brand pattern: Tailwind via the `@tailwindcss/browser@4` CDN script, `gradient-text` class for the sky → pink accent, system font stack, `noindex`. Phase 25 inherits this pattern (see "Resolved decision: framework choice" below).
11. **`scripts/sync_to_public_v2.py`** — the allowlist. Current entry `("website/v2", "website")` rewrites src `website/v2/` → dst `website/`. So everything Phase 25 puts under `website/v2/` lands at the deploy-source root after sync. Phase 25 must verify the `("website/v2", "website")` rewrite still covers `exports/` and `templates/` recursively — `shutil.copytree` recurses by default, so no allowlist change is needed. (See "Resolved decision: allowlist update" below.)
12. **`references/cowork-mcp-config-snippet.json`** — confirms Phase 25 doesn't touch MCP. The renderer is pure static; the export tool (which Cowork invokes through the MCP server) is the only producer of `exports/index.json`.

---

## Resolved decisions

These were ambiguities surfaced from the Phase 24 ship + the Session 13 brief input. Resolved up-front so the Phase 25 implementation doesn't need to escalate.

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

### Block 1 — ADR-003 implementation pass

**Goal:** translate ADR-003 D1-D8 into the concrete CSS variables, component sketches, About page copy, and voice-review checklist that Block 2's HTML/JS rewrite consumes. No design re-litigation. ADR-003 is locked.

**Outputs:**

- **Light-variant palette pass.** ADR-003 D2 commits Phase 25 to a complete light-variant palette alongside the canonical dark (slate-950 background, slate-300 body text, sky → pink accent). Specify every color used by the site as a CSS variable with both a dark-mode value and a light-mode value. Document the mapping in `docs/phase25-palette.md` (one file, ≤ 100 lines): list each variable, its dark value, its light value, the reason. WCAG AA contrast verified for body text and status pill text in both themes; document the contrast ratios alongside each value.
- **Theme toggle component sketch.** ADR-003 D2 specifies sun / moon icon button in the top-bar with `aria-label="Switch theme"`, `localStorage` key `uja-v2-theme` (`dark` | `light` | absent → `prefers-color-scheme`), keyboard activation. Sketch the inline SVG (sun + moon paths) and the ~30-50 line JS module that reads + writes the localStorage key. Land in the same commit as the palette pass OR in a sibling commit; either way before Block 2 starts.
- **Status filter chip + pill component sketches.** ADR-003 D1 + D3 specify the chip set (`All` / `Open` / `Submitted` / `Interviewing` / `Offer` / `Closed` / `Rejected`) and the mid-saturation pill style. Status → `{bg-color, text-color}` mapping per Appendix A.2 (`Open = sky-400`, `Submitted = blue-400`, `Interviewing = amber-400`, `Offer = emerald-400`, `Closed = slate-400`, `Rejected = rose-400` — exact hues are Phase 25 implementation choices; the locked rule is mid-saturation translucent backgrounds + bright text). Sketch the markup + the multi-select state machine (chip click filters; clicking same chip unselects; clicking `All` resets).
- **About page draft.** ADR-003 D5 makes the About page load-bearing — the only place context + privacy posture lives. Use Appendix A.4 as the starting draft; rewrite as needed. Keep to one short page or a single anchor section on `index.html` (Phase 25 picks per usability). Voice = plain-without-clubby per D6 + Appendix B.
- **Copy review checklist.** ADR-003 D6 codifies the voice. Run the checklist on every visible string in the rewritten HTML: (a) 8th-grade Flesch-Kincaid OR a literal label like `Submitted` that has no simpler form, (b) no aspirational verbs (dream, transform, unleash), (c) no insider terms (utilize, leverage, ecosystem), (d) no scare words (game-changer, revolutionary, AI-powered). Copy review runs as the last sub-step in Block 1 OR as a pre-merge step in the Phase 25 PR review — both work; the goal is "no aspirational copy ever lands."

**HITL gate:** present the palette table + the About page draft + the copy review pass for review with Milan before Block 2 starts. This is the one named HITL gate inside Phase 25 (R1-R6 below resolve every other axis up-front so the implementation doesn't escalate at every step).

**Atomic commits on branch `phase25/v2-site-rebuild` (base = `phase24/export-pipeline`):** suggested split: (a) `docs/phase25-palette.md` + the CSS variables in `website/v2/styles.css` (or the inline `<style>` block in `index.html`), (b) the About page draft + copy review notes appended to `docs/phase25-palette.md` or as a sibling `docs/phase25-copy-review.md`. Both before any Block 2 commit lands.

### Block 2 — `website/v2/index.html` rewrite + `website/v2/app.js` + `website/v2/styles.css`

- Rewrite `website/v2/index.html` end-to-end. Layout per ADR-003 D8: thin top-bar (~48-64px) with site name + About link + theme toggle. Below it the status filter chip row (~40px, D1). Below the chips the card list. Cards immediately above the fold at typical desktop viewport (1440x900) — no hero, no marketing banner, no intro paragraph. Three sections in the page: **Application packages** (top, primary content per D4 + D8), **Config templates** (middle), **About** (bottom anchor OR separate `about.html` per Block 1's choice).
- Header: brand mark (logo.svg + "Ultimate Job Assist" + small `v0.2.3` badge in the gradient accent). Footer: same shape as v1 (`No tracking. No analytics. No SaaS.`).
- `<meta name="robots" content="noindex,nofollow">` preserved verbatim.
- System font stack preserved verbatim.
- Tailwind via CDN browser script preserved (R4).
- Inline `<style>` block (or sibling `styles.css`) for `.gradient-text` and the CSS variables defined in Block 1.
- `prefers-color-scheme` + `localStorage` theme bootstrap script in `<head>` (NOT deferred) so the page paints in the right theme on first frame, avoiding a flash.
- `website/v2/app.js` (new):
  - On `DOMContentLoaded`, parallel-fetch `./exports/index.json` and `./templates/index.json`.
  - Render each section's cards from the parsed array. Single flat card list per ADR-003 D4 — no view switcher, no kanban, no calendar.
  - Status filter chips: multi-select state machine; chip click filters the card list (DOM update only, no fetch); count badge per chip; `All` resets.
  - Empty-state on missing or empty data (R3) — voice per ADR-003 Appendix B.
  - Prettification helper for company / role display (R1).
  - Card layout per ADR-003 Appendix A.3: company logo placeholder (colored circle with company initial), company name, role, application_month (e.g. `April 2026`), status pill (mid-saturation, D3), size, download link.
  - Each card on the Application packages section: download link with `download` attribute pointing at the zip filename (`./exports/<filename>`), human-readable size (`<size_bytes>` formatted via `Intl.NumberFormat` or a small KB/MB switch), status badge per the D3 mapping, application month displayed verbatim or prettified to `MMMM YYYY`.
  - No frameworks. No bundler. ES modules optional but not required (the file is small enough that a single `<script defer>` is fine).
  - Total `app.js` should land under ~300 lines including comments + the empty-state markup + the chip/filter state machine.
- `website/v2/styles.css` (new, optional): only if Tailwind utilities can't cover it. Initial guidance: try to do everything with Tailwind classes; if a custom utility is needed (the precise sky → pink gradient border, the mid-saturation pill style, the CSS variables for theming), put it here, not inline. Keep the file under 150 lines.
- `website/v2/exports/index.json` (new) per R6: `{"schema_version": 1, "exports": []}` + trailing newline.
- `website/v2/templates/index.json` (new): `{"schema_version": 1, "templates": []}` + trailing newline. The schema for templates is symmetric to exports — Phase 25 doesn't yet ship any templates; the populated file lands when the orchestrator decides what bracketed-placeholder templates to publish (parked as a v0.2.4-ish question, see "Out of scope" below).
- Atomic commit per logical change (or one if you prefer; both are fine — atomic = "one logical change," not "one file per commit"). Suggested split: (a) `index.html` skeleton + theme bootstrap + assets, (b) `app.js` + `styles.css` (renderer + chips + filter state machine), (c) the two empty index.json files.

### Block 3 — Site-renderer test

- `website/v2/tests/site-renderer.test.html` (new): a single self-contained HTML page that (a) loads `app.js`, (b) injects three fixture `index.json` shapes (empty / single-row / multi-row across two months), (c) calls the renderer, (d) asserts the DOM landed as expected. Use `<details>` blocks + plain-text assertions (no testing framework — the file is openable in any browser and reports pass/fail visually). Cover:
  - Empty array → empty-state block visible, card grid invisible.
  - Single row → one card with the right prettified company/role + size in human units + status badge + working download link href.
  - Multi-row across two months → cards in `application_month desc, company asc` order (preserved from `_sort_index_exports`).
  - Filter chip `Submitted` (single-select) → only `submitted` rows visible.
  - Filter chip multi-select (`Submitted` + `Interviewing`) → both subsets visible.
  - Theme toggle: clicking sun / moon swaps the `data-theme` attribute on `<html>` AND persists to `localStorage` under `uja-v2-theme`.
  - WCAG AA spot check: assert that the body-text-on-background contrast in both themes meets 4.5:1 (computed via a small `getComputedStyle` + relative-luminance helper — not a separate dependency).
- Atomic commit on the same branch.

### Block 4 — End-to-end smoke + PR

- Run the export tool against the Q6 lock fixture (`waymo-bi-analyst-2026-04`, see `docs/notes-q6-test-app-lock.md`):

  ```
  export_application(
    company_role="waymo-bi-analyst-2026-04",
    project_root="/Users/Milan/Documents/Documents - Milan's MacBook Pro (Personal)/Claude/Ultimate Job Assistant",
    status="interviewing"
  )
  ```

  Verify the produced `index.json` row appears in the rendered card on `file://...website/v2/index.html`. Re-run with `status="offer"`; verify the card updates in place. Smoke runs in a Cowork chat walkthrough — the assertions are visual + screenshot, not bash.
- Open the combined Phase 24 + Phase 25 PR (or stack — coordinator's choice) against `main`. Tag `v0.2.3` after merge.

## Working principles (verbatim from CLAUDE.md — non-negotiable)

- **Human-in-the-loop.** Block 1's ADR-003 implementation pass (palette + About + copy review) is the one explicit HITL gate. R1-R6 below resolve every other axis up-front so the implementation doesn't need to escalate. If a new ambiguity surfaces (an ADR-003 detail is ambiguous in practice; the Phase 24 `index.json` shape committed on the branch differs from this brief's R1 description; the sync script's behavior surprises you), surface it and wait.
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
10. The Phase 24 work on `phase24/export-pipeline` is unchanged — Phase 25's commits add files under `website/v2/`, they do NOT modify `host/uja_mcp/`, `host/uja_host/`, `host/tests/`, or any docs other than possibly `docs/phase25-palette.md` / `docs/phase25-copy-review.md`.
11. The deprecated tree (`host/uja_host/api/chat.py`, `api/conversations.py`, `host/frontend/`) is unchanged from Sessions 10-12.
12. PR is open + ready for review, stacked on `phase24/export-pipeline`. Tag is cut by the originating Cowork session after merge — annotated `v0.2.3`, message references ADR-002 D4 + this brief.

---

## End-of-session deliverables (in your final message back)

1. The PR URL.
2. Block-by-block summary of what landed, with commit SHAs and the base branch (`phase24/export-pipeline`).
3. `docs/phase25-palette.md` (Block 1) plus any sibling docs from the ADR-003 implementation pass (palette / About draft / copy review notes).
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

These are points where this brief deviates from the user's input. Confirm or correct before Phase 25 implementation begins.

1. **R4 contradicts the user's "Tailwind is NOT brought in for the v2 site (v1 didn't have it)" instruction.** The v1 production site `website/index.html` and the current v2 placeholder both use Tailwind via the `@tailwindcss/browser@4` CDN script. R4 keeps Tailwind. If the orchestrator wants the truly framework-free path, this needs to be explicit, plus a separate Phase 26-ish ticket to rip Tailwind out of the v1 site too (otherwise Phase 25 diverges from the established pattern for no architectural reason).
2. **R5 contradicts the user's "Phase 25 owns adding `website/v2/exports/` to the allowlist" instruction.** The existing `("website/v2", "website")` entry already recursively syncs everything under `website/v2/`. Adding a nested entry would be redundant. If the orchestrator has a reason to want explicit nested entries (e.g. for visibility in the dry-run output), fine, but it's not a correctness requirement.
3. **The user's brief input said "Phase 24's PR #7" — verified: PR #7 against `main` from `phase24/export-pipeline`.** The branch's HEAD is `5879f3f` as of Session 14. If Phase 24 gets force-pushed (rebased) before Phase 25 implementation begins, re-base the Phase 25 branch on the new tip.
4. **The Phase 24 implementation references "five commits" in the user's input but the branch on origin shows five commits** (`fc77c92` Block 1 → `5879f3f` Block 5). Consistent. No-op.
5. **Templates section is rendered but un-populated.** The brief commits to rendering templates from `templates/index.json` but defers populating it. Confirm that's acceptable for v0.2.3 — the alternative is to either ship a starter set in this session (scope creep) or hide the Config templates section entirely until v0.2.4 (deviates from ADR-002 D4 "three sections, each on its own anchor").
6. **The brief assumes `references/examples/` may have been pruned** (per `EXCLUDE_DST` in `sync_to_public_v2.py`). For Block 4's smoke, the agent may need to hand-craft a fixture `decoded-jds/` + `resumes/` pair. Is that acceptable, or does the orchestrator have a preferred test application?

---

*End of brief.*
