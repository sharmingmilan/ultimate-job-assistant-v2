# ROADMAP.md — Ultimate Job Assistant

**Last updated:** 2026-05-02 (Session 4 — v0.2.0 promoted to committed; new decisions in log)
**Status:** Living document. The full v0.1.0 build plan lives in SPEC.md. This file captures *post-v0.1.0* work.

---

## How this file works

Each section below describes a possible future direction with rough scope, cost, and prerequisites. Items here are NOT committed work. They become committed when:

1. Milan approves an item for active build, AND
2. A SPEC update or follow-up SPEC document is written (every committed item earns its own spec)

Items live here so the design seams in v0.1.0 stay aware of where we might go later.

---

## ~~Track 0 — Self-hosted local web app~~ — promoted to v0.2.0

This track is now the committed v0.2.0 build (SPEC.md §14 / ADR-001). Captured here briefly so the roadmap stays the entry point for "what's coming next."

### Shape

A self-hosted local web app the user runs on their own computer, brings their own Anthropic API key to, and uses through a browser tab. Path A (Cowork mode in Claude Desktop) and Path B (web app) become two surfaces over the same `skills/[name]/SKILL.md` files. Same on-disk folder structure either way.

### Architecture (locked)

| Concern | Decision |
|---|---|
| Skill execution | Skills-as-Tools — host registers a tool catalog with Claude API; agent loop stays in Claude |
| Backend | Python 3.11+ + FastAPI |
| Frontend | React + Vite + Tailwind + shadcn/ui (using the `anthropic-skills:web-artifacts-builder` patterns) |
| Distribution | Curated-zip extension with `start-uja.sh` + `start-uja.bat` |
| Persistence | SQLite at `<project-root>/.uja/state.db`, schema-versioned |
| File access | Hard sandbox to one project-root folder picked at first launch |
| API key | Encrypted at rest via OS keychain (Python `keyring`); never logged; outbound only to `api.anthropic.com` |
| Network | `127.0.0.1` only by default; documented `--bind` override |
| Branch protection | Local pre-push hook (Pro is required for server-side; we don't pay) |

Full rationale, rejected alternatives, and the eight-tool catalog live in `docs/ADR-001-v0.2.0-architecture.md`.

### Phasing

Phases 14–22 in SPEC.md §14. Phase 14 (this ADR + branch setup) shipped 2026-05-02 / Session 4. Phase 15 (backend scaffold) is next.

### Cost / mo

$0 to operator. Users pay their own Anthropic bill.

### Why this and not Track 1 (SaaS)

Track 1 (SaaS multi-user) remains a possible future direction but requires auth, payments, hosting, GDPR/CCPA, and a real ops story. Track 0 is the much smaller step that gets the toolkit out of "you have to use Claude Desktop's Cowork mode" without taking on operator responsibilities. If Track 0 sees real usage, Track 1 becomes more attractive; if it doesn't, Track 1 was correctly deferred.

---

## Track 1 — SaaS pivot

Convert the personal toolkit into a multi-user product where strangers can sign up, run the workflow on their own JDs, and download their own deliverables.

### Why this might happen

Milan said: *"I want to build this out so someone random can use it for their job applying needs."*

### What changes from v0.1.0

| Concern | v0.1.0 (today) | SaaS |
|---|---|---|
| Auth | none | Clerk free tier (10K MAU free) or Supabase Auth |
| Database | filesystem + git | Supabase (Postgres) free tier (500 MB, 50K MAU) |
| Skill execution | Claude in chat (Cowork) | Anthropic API server-side, wrapped as serverless functions |
| Hosting | Netlify Drop, free | Vercel Pro $20/mo or Cloudflare Pages free + Workers |
| Payments | none | Stripe (test mode free; ~3% on real txns) |
| Privacy / compliance | n/a (single user) | GDPR, CCPA, data deletion, ToS, privacy policy |
| File storage | filesystem | Supabase Storage or R2 (~$0/mo at low volume) |
| Per-user PWA | folder on disk | hosted subdomain or download link |

### Architecture seams already in place

- Content separated from rendering at `content.json` (SaaS can swap from a DB)
- Skill spec is YAML frontmatter + markdown — easy to ship as an API contract
- No hardcoded Milan-specific paths in skill code (only in personal-data folders, which are git-ignored)

### Cost ladder

| Stage | Users | Stack | Cost / mo |
|---|---|---|---|
| Hobby | 1–10 | Vercel free + Supabase free + Clerk free | ~$0 (excluding Anthropic API) |
| Light | 10–500 | Vercel Pro + Supabase Free + Clerk free | ~$20 |
| Growth | 500–5K | Vercel Pro + Supabase Pro + Clerk Pro | ~$70 |
| Scale | 5K+ | Custom; depends on usage | $200+ |

Anthropic API costs are usage-based. At ~$0.05–0.50 per workflow run depending on model choice and how aggressively the skill leans on web research.

### Open design questions (do not need answers yet)

- Bring-your-own-API-key vs. operator-provided?
- Do users own their data file-by-file, or only via export?
- Real-time collaboration on a resume targeting session, or single-user only?
- Resume-targeter's "human-in-the-loop" model: how does that translate to async web UI?

### Prerequisites

1. v0.1.0 ships and gets a real successful run
2. Decision: flip repo to public (currently private)
3. A separate SPEC document (`SPEC-saas.md`) before any code

---

## Track 2 — Browser-driven skills (without backend)

Lighter version of the SaaS pivot: package each skill as a static page that runs Claude *via the user's own API key*, kept entirely in the browser. No server, no auth, no database, no payments.

### Why this might happen

Lower bar than full SaaS. Anyone with an Anthropic API key gets the toolkit; Milan never has to operate a service.

### Cost / mo

$0 to operator. Users pay their own Anthropic bill.

### Tradeoffs

- ✅ No operator infrastructure
- ✅ User data never leaves their browser
- ❌ User must sign up for Anthropic API (friction)
- ❌ Web research from a browser is rate-limited and CORS-restricted
- ❌ File handling is awkward (downloads, no persistent project state)

---

## Track 3 — Code execution for self-grading

Add a real SQL playground inside the PWA so retrieval problems can be self-checked.

### Approach options

1. **DuckDB-Wasm** — runs SQL fully in the browser, no backend needed. Bundle adds ~3 MB; works for analytical SQL but not Postgres/Trino dialect features that DuckDB lacks
2. **Server-side executor** — pushes the project into "needs a backend" territory; only worth it if SaaS pivot happens first
3. **Worker that proxies to Snowflake/Trino sandboxes** — most realistic dialect parity but $$$ and complex

### Recommendation

Start with DuckDB-Wasm. Document dialect divergences from Trino. Server-side only if SaaS happens.

---

## Track 4 — Spaced repetition (real)

Replace the v0.1.0 flag-and-cooldown with a proper SM-2 / Anki-style scheduler.

### Why later

The flag-and-cooldown is fine for a 7-day prep horizon. SM-2 only matters when content volume exceeds what someone can churn through in a week and the user has a multi-week study horizon (e.g., a junior candidate prepping for their first analyst role).

### Implementation

- Two new fields per problem: `next_review_at`, `ease_factor`
- localStorage today; database when SaaS happens
- Standard SM-2 update on every "Conquered" attempt: ease ± based on self-rating
- Anki-style 4-button rating (Again, Hard, Good, Easy)

---

## Track 5 — Cross-application analytics

Today, each application's `interview-prep` PWA is isolated. There's no view that says "Milan tends to struggle with window functions across companies."

### What this would unlock

- Resume-targeter could surface: "you've struggled with X concept in 3 of your last 5 prep sites — call it out as a growth area on your resume"
- Portfolio-coach could pick: "your last 4 study sites had a deduplication topic; you've never done a portfolio piece on dedup — recommend it"
- Speaking-points could rehearse: "in your last 3 interviews, the case-study round used a metric-drop framing; here's a refresher"

### Implementation

A small `analytics.json` at the project root; every PWA writes summary stats on completion (topics attempted, retrieval pass rate, time-on-task). Skills read it. No identifying info, all on disk.

---

## ~~Track 6 — Auto-deploy (CD on tag)~~ — promoted to v0.1.1

This track is now part of the committed v0.1.1 build (SPEC §14). The form is slightly different from the original framing: rather than auto-deploying on tagged release, the v0.1.1 plan auto-deploys on **every push to main** of the canonical private repo, via a GitHub Action that:

1. Runs `scripts/sync_to_public.py` with strict PII scan
2. Pushes the sanitized result to the deploy-source repo
3. Netlify (now the host) auto-rebuilds when the deploy-source repo changes

Edit-to-live latency target: ~30 seconds.

---

## Track 7 — Workflow UI rethink (v0.4.0) — committed Session 8

The chat-style UI shipped in Phase 17 is the wrong metaphor for job-application workflows. Discovered live in Session 8 testing: agent loops mid-conversation get visually overwhelming, the HITL approve cards are decoupled from the workflow state they're modifying, and there's no "where am I in the process" surface. Chat works for one-off questions, not for orchestrated multi-step work.

### What v0.4.0 looks like

A structured workflow tracker — Sims-style. Each job application is one persistent "session" with a visible stage map: Intake → Research → Decode → Resume → Score → Speaking Points → Cover Letter → Portfolio → Networking → Interview Prep. The user clicks into a stage, sees its inputs/outputs/status, takes a discrete action (approve, edit, regenerate, skip). Chat becomes a sidecar — "talk to the agent about this stage" — but never the primary surface.

### Inspiration

- Sims-style game UI (per Milan in Session 8): visible character/persona state, branching decisions, undo, clear progress
- Linear's project view: structured stages with status badges
- Notion's database/board view: per-row state with rich detail panes
- Pipedream / Zapier workflow editors: visible step graph

### Open design questions (next session)

1. **Canva MCP exploration** — pull design references for Sims-style game UIs and structured workflow trackers. Sketch 2-3 visual directions.
2. **State model** — how does an "application" persist? Probably extends `tracker.md` with structured per-stage state instead of free-text.
3. **Agent integration** — does the agent drive the stages, or does the user pick a stage and the agent assists? Probably the latter (user-driven), with the agent being callable per-stage.
4. **Cowork vs local-app** — ✅ resolved by ADR-002 D1 (Session 9): the workflow tracker runs as a Cowork artifact (interactive HTML) that calls back into the v0.2.x MCP server through `window.cowork.callMcpTool(name, args)`. No local UI server needed. The MCP server (host/uja_mcp/) owns the tool surface; the artifact owns the rendering.

### Why this is in roadmap, not v0.2.0

v0.2.0 ships (Session 9) as a maintenance release of the Phase 15-17.5 work; v0.2.x lands the Pure Cowork + thin MCP runtime per ADR-002. The chat UI is preserved as a deprecated reference (per ADR-002 D3). v0.4.0 is the right target for the workflow-tracker redesign — it sits on top of the v0.2.x MCP server (which owns the tool surface) and uses Cowork's artifact pipeline for rendering. Clean slate, but on a foundation that's already specified.

---

## Track 8 — Site as exportable application-package delivery hub (v0.2.x site rebuild) — committed Session 8

Reframes the v2 Netlify site from "marketing landing for the local web app download" to "delivery hub for completed **exportable** application packages + config templates." Driven by Milan's Session 8 statements: "I just want the website to be a place to take whole packaged application zips for and configs" + "exportable*" (his subsequent correction — "exportable" rather than "packaged" is the load-bearing word, because these zips exist to be downloaded, shared, sent to recruiters, archived, etc.) + "the application files I need to apply for a job should end up being built there."

### What it looks like

- **Per-application exportable zip downloads.** One zip per company-role: decoded JD, targeted resume (DOCX + PDF), score reports, speaking points (MD + PDF), cover letter (MD + PDF), portfolio README, networking outreach drafts. URL-only access (search-invisible per existing v1 pattern). Designed to be sent intact to recruiters, attached to applications, archived for cross-application reference, etc.
- **Config templates section.** The bracketed-placeholder versions of memory.md, tracker.md, base resume, etc. — what a forker downloads to bootstrap their own UJA workspace.
- **Index page.** Lists all available application packages with company / role / date / status badges. No marketing copy.
- **No download CTA for the local web app.** That direction is being reconsidered (Pivot C).

### Resolved by ADR-002 D4 (Session 9)

- **Where does the zip get built?** ✅ Cowork emits it as a workflow step via the new `export_application(company_role)` MCP tool. The MCP server walks per-output-type folders, validates the minimum-viable set, writes a deterministic zip to `website/v2/exports/`, and updates `index.json`. Existing `auto-sync-to-public.yml` mirrors to deploy-source; Netlify rebuilds.
- **Static or generated?** ✅ Static. `index.html` + JS that fetches `exports/index.json` and `templates/index.json` and renders cards.
- **Zip structure?** ✅ `<company>-<role-slug>-<YYYY-MM>.zip` containing `manifest.json` (machine-readable) + `README.md` (human-readable) + `decoded-jd/` + `resume/` (DOCX + PDF) + `scores/` + `speaking-points/` + `cover-letter/` + `portfolio/` + `networking/`. Deterministic bytes: sorted ordering, fixed compression level, zeroed timestamps.
- **Visual style** — Canva MCP exploration still required (spike, ahead of v0.2.3 build). Match v0.4.0's structured-workflow aesthetic. No marketing copy. No gradient buttons. No emoji. System font stack. Sky → pink gradient as accent only.

### Why this is in roadmap, not v0.2.0 ship

ADR-002 D4 (Session 9) targets the v2 site rebuild at v0.2.3 — after the MCP server scaffold (v0.2.1) and the export pipeline (v0.2.2) are in place, since the site depends on both. Specified in SPEC §14 as Phase 25.

---

## Track 9 — v0.3.0 reframe (parked pending ADR-003) — moved here from SPEC §14 in Session 9

ADR-001 §14 originally committed v0.3.0 to a Tauri double-click app wrapping the local-host. With ADR-002 D1 chosen (Pure Cowork + thin MCP, Session 9), Cowork is itself the desktop app — there is no "web app" left to wrap. The v0.3.0 plan is parked. Sat in SPEC §14 as a "PARKED" section briefly; moved here because SPEC §14 carries committed phases and ROADMAP is the right home for parked/future work.

### Plausible reframings (to be resolved by ADR-003 after v0.2.x lands)

- **v0.3.0 = polished MCP-server installer.** One-click `pip install` + Cowork MCP-config registration; code signing for the launcher binary on macOS (~$99/yr Apple Dev) and Windows (~$200/yr code-signing cert). Could ship unsigned with right-click→Open caveat on first release. Lowest-friction path for non-developer forkers.
- **v0.3.0 = headless export-only mode.** A standalone CLI that bundles per-application zips without going through Cowork. Resurrects the OS-keychain API-key path from "demoted" to "supported behind a flag" (per ADR-002 D3). Useful for CI-style application-bundling pipelines, scheduled exports, or users who want the export pipeline without the rest of Cowork's surface.
- **v0.3.0 = skipped.** Jump straight to v0.4.0 (workflow tracker). Defensible if v0.2.x's launcher is already polished enough that "v0.3.0 polish" doesn't earn a tag, and if no headless export demand surfaces.

### When ADR-003 lands

Likely after Phase 23-25 (v0.2.1 / v0.2.2 / v0.2.3) ships. ADR-003 needs the same treatment ADR-002 got: gut-preference questions to Milan first, recommendation pre-loaded, then a structured Decisions document. The "Do not start any Tauri work" guidance from ADR-002 stays in force until ADR-003 resolves the reframing.

### Why this is in ROADMAP, not SPEC

SPEC §14 carries committed phases — work where the deliverable, the target tag, and the acceptance criteria are all specified. Parked work (multiple plausible shapes, no committed direction) belongs in ROADMAP. Following the same convention as Track 7 (v0.4.0 workflow UI rethink) and Track 8 (v0.2.x site rebuild), which were committed to roadmap rather than SPEC at their decision-log moment.

---

## Anti-roadmap

Things explicitly NOT planned, even with infinite time:

- ❌ A native mobile app — PWA install on iOS/Android is good enough
- ❌ A built-in chat with Claude inside the PWA — the toolkit's value is in the structured workflow, not yet another chat box
- ❌ Resume parsing OCR for paper/scanned PDFs — out of scope; users provide text-based resumes
- ❌ LinkedIn API integration — terms-of-service hostile; not worth it
- ❌ "Auto-apply" features that submit applications — bad outcomes for users; we coach the application, the user submits

---

## Decision log

| Date | Decision | Rationale |
|---|---|---|
| 2026-05-02 | v0.1.0 stays personal/local | Faster to ship; SaaS pivot kept open via content/rendering separation |
| 2026-05-02 | Repo private at start | Path to public after first real successful run, with explicit Milan approval |
| 2026-05-02 | Single shared neutral icon for all PWAs | Simpler than per-app generation; brand consistency across applications |
| 2026-05-02 (revised) | **Two-tier repo strategy: private repo never public; public artifact is ONBOARDING.md** | Earlier plan was to flip private → public after first run. Revised after PII was discovered in the v0.1.0 baseline commit. Private repo can hold real Milan data permanently; public reach happens via a sanitized onboarding doc (and optionally a future public companion repo). See SPEC §13. |
| 2026-05-02 | Do NOT amend commit `49bc5be` | The original commit retains the unredacted resume fixture. Per the new repo strategy, this is fine — the repo is private and stays private. Working-tree redacted version remains for use as the active eval fixture. |
| 2026-05-02 | **Public companion repo confirmed (option b)** | Selected over single-doc and branch-based publish. New repo `ultimate-job-assistant-public` will hold sanitized skill code + templates + ONBOARDING + website source. Sync via allowlisted script with PII scanner; never automatic. See SPEC §13.1. |
| 2026-05-02 | **Public website: shape C, GitHub Pages, part of v0.1.0** | Landing page + multi-page docs site. Astro is the default stack (decision flips during Phase 7 design if MkDocs Material fits better). Live demo PWA (option D) deferred to v0.1.1. See SPEC §13.2 and Phase 7 in §14. |
| 2026-05-02 (Phase 7 design) | **Stack flipped from Astro to plain static HTML + Tailwind CDN** | Mirrors PWA-template philosophy. ~1 hr build vs 3+ for Astro. GitHub Pages serves directly with `upload-pages-artifact` + `deploy-pages`. |
| 2026-05-02 (post-v0.1.0 same day) | **noindex + robots.txt added** | Site stays live and public-repo-hosted but is invisible to search engines. Personal-toolkit note added to README. URL becomes the credential. |
| 2026-05-02 (post-v0.1.0 evening) | **Landing page simplified to download-first** | One primary CTA: "Download the latest". HEAD-fetch JS displays zip size + date. Documentation pages still exist but understated. |
| 2026-05-02 (final architecture revision) | **Both repos go private, hosting moves to Netlify, zip distribution** | Even with `noindex`, a public GitHub repo is still searchable on GitHub itself. Moving hosting from GitHub Pages to Netlify (free tier, reads private repos via OAuth) lets both repos go private while keeping the site live. The website exposes `/downloads/ultimate-job-assistant.zip` for anyone with the URL — that becomes the public artifact. Auto-sync via GitHub Action on the canonical private repo. Custom domain (~$12/yr) confirmed for v0.1.1. See SPEC §13 (current state) and §14 v0.1.1 phases 8-12. |
| 2026-05-02 (Session 4) | **v0.2.0 = self-hosted local web app (Track 0 promoted)** | Adds a second way to run UJA: a Python+FastAPI backend + React+Vite+Tailwind+shadcn/ui frontend the user launches locally with `start-uja.sh` / `start-uja.bat`. Skills stay as `SKILL.md` (Skills-as-Tools); agent loop stays in Claude. Bring-your-own-API-key. Cost stays $0 to operator. Full architecture + alternatives in `docs/ADR-001-v0.2.0-architecture.md`. Phases 14–22 in SPEC.md §14. |
| 2026-05-02 (Session 4) | **ROADMAP.md is canonical-only (drop from sync allowlist)** | Removed from `scripts/sync_to_public.py` ALLOWLIST and added to EXCLUDE_DST so any historical copy gets pruned from the deploy-source repo. Rationale: ROADMAP carries SaaS speculation and repo-strategy notes that have no business sitting in the deploy-source repo even though that repo is private. Asymmetry over the rest of the allowlist is deliberate. SPEC.md §13.10 captures the rule. |
| 2026-05-02 (Session 4) | **Local pre-push hook replaces server-side branch protection** | GitHub branch protection / rulesets are Pro-gated on free private repos (verified via API: HTTP 403). `references/git-hooks/pre-push` refuses direct pushes to `main`. `scripts/install-hooks.sh` is the idempotent installer. SPEC.md §13.11 captures the rule. |

| 2026-05-03 (Session 8) | **Pivot A: chat-style UI is wrong metaphor for job-app workflows; v0.4.0 = Sims-style workflow tracker** | Live testing showed agent-loop mid-stream is visually overwhelming, HITL cards decoupled from workflow state, no "where am I" surface. Track 7 added; Canva MCP for design exploration. |
| 2026-05-03 (Session 8) | **Pivot B: v2 site reframes to exportable-application-package delivery hub** | Marketing landing was wrong fit for inner-circle audience. Per-application exportable zip downloads (sendable to recruiters, archivable, shareable) + config templates only. URL-only access (existing search-invisible pattern). Track 8 added. "Exportable" is load-bearing — these zips exist to leave the site, not just sit on it. |
| 2026-05-03 (Session 8) | **Pivot C: Anthropic-API-key + local-web-app architecture being reconsidered** | Workflow likely stays in Cowork (users have Claude desktop); local infrastructure exists for tooling not agent loop. Phase 17.5 HITL endpoints + sandbox + file API survive; chat-tab + agent-loop-in-host being deprecated. Resolution awaiting ADR-002 next session. |
| 2026-05-03 (Session 8) | **v0.2.0 phase plan (Phases 18-21 + tag) paused pending ADR-002** | Pivots A/B/C above mean Phases 18-21 (distribution polish, comprehensive tests, docs refresh, merge gate) need to be redesigned, not just executed. Phase 17.5 (this session) is the last shipped work under the original v0.2.0 plan. |
| 2026-05-03 (Session 9) | **ADR-002 lands: Pure Cowork + thin MCP architecture chosen** | Resolves Pivot C. Local FastAPI process becomes a JSON-RPC-over-stdio MCP server (no HTTP frontend, no per-user Anthropic API key, no port). Cowork drives the agent loop. v0.4.0 workflow tracker becomes a Cowork artifact that calls back into the MCP server. Sandbox / db / file_tools / skill_tools / skill_registry / HITL endpoints / 36-test suite all survive and re-shape into MCP tool functions. See `docs/ADR-002-architecture-rethink.md`. |
| 2026-05-03 (Session 9) | **v0.2.0 ships as maintenance release; Phases 18-21 retired** | Per ADR-002 D2. Tag `v0.2.0` against current `main` to capture the Phase 15-17.5 work as a reachable artifact; release notes flag chat-style UX as deprecated. v0.2.x picks up the new architecture (Phases 23-25 in SPEC §14). |
| 2026-05-03 (Session 9) | **Chat-tab frontend kept as deprecated reference** | Per ADR-002 D3 + Q3 clarification. `host/frontend/` stays on main with a README marking it deprecated and explaining its preserved purpose (HITL UX patterns demo). No active maintenance. v0.4.0 workflow tracker rebuilds the same patterns in a different visual frame. |
| 2026-05-03 (Session 9) | **v0.3.0 (Tauri) parked; ADR-003 will reframe** | Per ADR-002 "Phasing impact." Cowork is itself the desktop app; wrapping a non-existent web app in Tauri is moot. Plausible reframings (polished MCP installer, headless export mode, or skip) deferred to ADR-003 after v0.2.x lands. Do not start Tauri work meanwhile. |
| 2026-05-03 (Session 9) | **v2 site zip pipeline: Cowork emits via `export_application` MCP tool** | Per ADR-002 D4 + Q4 answer. When the v0.4.0 workflow tracker hits an export stage, Cowork calls `export_application(company_role)`; the MCP server walks per-output-type folders, validates minimum-viable set, writes deterministic zip to `website/v2/exports/`, updates `index.json`. Existing `auto-sync-to-public.yml` mirrors to deploy-source; Netlify rebuilds. Zip layout: `manifest.json` + `README.md` + per-output-type subfolders. Deterministic bytes (sorted, fixed compression, zeroed timestamps). |
| 2026-05-03 (Session 9, post-wrap) | **v0.3.0 PARKED block moved from SPEC §14 to ROADMAP Track 9** | SPEC §14 carries committed phases; ROADMAP is the right home for parked/future work. SPEC now has a one-line pointer to Track 9. Mirrors how Tracks 7 + 8 (v0.4.0 + v0.2.x site) live in ROADMAP rather than SPEC at their decision-log moment. |

Append future decisions here as they're made.
