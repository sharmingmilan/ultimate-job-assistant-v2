# CLAUDE.md -- Ultimate Job Assistant
# Last updated: 2026-05-04 (Session 14 — ADR-003 synthesis + freshness pass + Session 14 wrap; v0.2.1)

---

## Identity

A modular, research-driven personal job-application toolkit. Chains specialized skills together as an agentic workflow, with human-in-the-loop approval at every stage. No fabricated information -- only verified, sourced research.

Forked from the `Job Assist` project on 2026-05-02. Adds one major capability over the parent: the `interview-prep` skill, which produces a deployable single-file Progressive Web App (PWA) for any technical interview based on the same evidence-based pedagogy used in the Netflix Interview Prep build.

---

## Session Startup

Read three files to be fully oriented:
1. **This file** (CLAUDE.md) -- structure, rules, conventions, current status
2. **SPEC.md** -- canonical build plan, scope, decisions, acceptance criteria (read this BEFORE editing anything structural)
3. **memory.md** -- Milan's preferences, work style, key stories for resume targeting

Read on demand:
- **tracker.md** -- when working on a specific application or resuming where we left off
- **DESIGN_DOC.md** -- when you need detailed skill specs, design decisions, or future enhancement context
- **ROADMAP.md** -- when discussing future enhancements, SaaS pivot, or post-v0.1.0 work
- **SESSION_LOG.md** -- when you need history of past sessions and why decisions were made

---

## Workspace Structure

```
Ultimate Job Assistant/
├── CLAUDE.md                ← you are here (structure, rules, conventions, status)
├── SPEC.md                  ← canonical build plan (read before any structural change)
├── ROADMAP.md               ← future enhancements (SaaS pivot, multi-user, etc.)
├── README.md                ← public-facing entry doc
├── memory.md                ← Milan's preferences, work style, key stories
├── tracker.md               ← central application tracker (all roles, all statuses)
├── DESIGN_DOC.md            ← detailed skill specs, design decisions, future enhancements
├── SESSION_LOG.md           ← append-only session history
├── .github/workflows/ci.yml ← CI: SKILL frontmatter, JSON schema, smoke test
│
├── skills/                  ← skill logic (no user data -- pushable to GitHub)
│   ├── resume-targeter/
│   ├── decoded-jd/
│   ├── resume-scorer/
│   ├── why-this-company/
│   ├── portfolio-coach/
│   ├── networking-intros/
│   ├── orchestrator/
│   └── interview-prep/      ← NEW (v0.1.0)
├── references/              ← reusable templates, scripts, examples, patterns
│   ├── templates/
│   ├── scripts/
│   ├── examples/
│   └── patterns/
│
├── base-resumes/            ← base resume library (3-5 by role type)
├── research/                ← one file per company (profile + research brief, merged)
├── decoded-jds/             ← decoded job descriptions
├── resumes/                 ← targeted resumes (DOCX + PDF)
├── scores/                  ← resume-job match score reports
├── speaking-points/         ← "why this company" speaking points
├── cover-letters/           ← cover letters
├── interview-prep/          ← recruiter prep, thank-you letters, misc interview materials
├── portfolio/               ← portfolio projects (one subfolder per project)
├── networking/              ← contacts and outreach drafts
├── archive/                 ← completed or declined applications
└── .gitignore
```

---

## Conventions

### Naming Convention (load-bearing, must follow exactly)
```
[company]-[role-slug]-[YYYY-MM].[ext]

Examples:
  netflix-data-analyst-2026-04.md
  waymo-bi-analyst-2026-04.docx
  disney-lead-data-analyst-2026-04.pdf
  waymo-bi-analyst-2026-04-before.md   (scores get -before/-after suffix)
```

Company name lowercase, role slug is the hyphenated role title, date is application month.

### Output Folders Convention
Each output type has its own folder. All companies mixed within each folder. Sort by name in Finder to group by company.
```
research/[company].md                → Company profile + research brief (one file per company, reused across roles)
decoded-jds/[convention].md          → Decoded job description
resumes/[convention].docx + .pdf     → Targeted resume
scores/[convention]-before.md        → Score reports (-before and -after)
speaking-points/[convention].md+.pdf → Speaking points for interviews
cover-letters/[convention].md + .pdf → Cover letters
interview-prep/[convention]-*.md     → Recruiter prep, thank-you letters, misc
portfolio/[convention]/              → Portfolio projects (subfolder per project)
networking/                          → Contacts and outreach drafts
```

When starting a new application, check tracker.md first. If `research/[company].md` exists, reuse it. If not, create it before generating outputs.

### Skills Convention
```
skills/[name]/                       → SKILL.md has the full spec. Read before running.
                                       Some skills have subdirectories (evals/, references/).
```

### References Convention
```
references/templates/                → Blank templates for new files
references/scripts/                  → PDF generation scripts (adapt for new output types)
references/examples/                 → Waymo lifecycle outputs as quality benchmarks
references/patterns/                 → Methodology docs (formatting, scoring, Q&A, DOCX editing)
```

---

## Mandatory Rules

### Research Files
- Every company needs a `research/[company].md` file before any outputs are generated
- Research files have two sections: Section 1 (Company Research, reusable across roles) and Section 2 (Role-Specific Research, dated subsections per role, appendable)
- Blank template at `references/templates/research-brief.md`

### Formatting
No dashes as punctuation, contact line on one line, two-page max, no fabrication. Full rule set in memory.md (source of truth) and `skills/resume-targeter/SKILL.md`. Applies to ALL outputs, not just resumes.

### Output Format
Speaking points and cover letters always generated as both .md and .pdf. Cover letters end with sign-off from memory.md ("Sincerely, Milan").

### Progress Tracking
- **tracker.md** is the central source of truth for all application status
- Never auto-update tracker status. Ask Milan before marking steps complete.

### Naming Enforcement
All output files must follow the naming convention: `[company]-[role-slug]-[YYYY-MM].[ext]`. The orchestrator sets these variables at the start of each application and all skills derive filenames from them.

---

## Repeat Company Research Protocol

When applying to a new role at a company that already has a `research/[company].md` file:

1. Read existing `research/[company].md` (Section 1) as foundation
2. Search for new developments, leadership changes, strategy shifts. Add to Section 1 with dated annotation.
3. Append new dated subsection to Section 2 of research file
4. Add new row to tracker.md
5. Adaptive Q&A focuses on the delta vs. previous role, not re-covering explored ground

---

## Workflow Diagram

```
                        ┌─────────────────────┐
                        │   User provides:     │
                        │   • Job description  │
                        │   • Base resume      │
                        └─────────┬───────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │     ORCHESTRATOR starts       │
                   │  Infers mode: Quick or Deep   │
                   │  Confirms with user           │
                   └──────────────┬───────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
     ┌─────────────────────┐         ┌─────────────────────────┐
     │   Decoded JD         │         │   Resume Scorer         │
     │  • Explicit reqs     │         │   (pre-score, optional) │
     │  • Implicit expects  │         │                         │
     │  • Confidence tags   │         │  YES → score + breakdown│
     └─────────┬───────────┘         │  NO  → skip             │
               │                      └────────────┬────────────┘
               └───────────────┬───────────────────┘
                               ▼
                ┌──────────────────────────────┐
                │     Resume Targeter           │
                │  Research → Q&A → Bullets →   │
                │  Change Review → DOCX + PDF   │
                └──────────────┬───────────────┘
                               ▼
                ┌──────────────────────────────┐
                │     Resume Scorer (post)      │
                │  Auto if pre-score was yes    │
                │  Otherwise ask                │
                │  Shows before/after delta     │
                └──────────────┬───────────────┘
                               ▼
                ┌──────────────────────────────┐
                │     Why This Company          │
                │  Speaking points (always)     │
                │  Cover letter (optional)      │
                │  Narrative insights → scorer  │
                └──────────────┬───────────────┘
                               ▼
     ┌─────────────────────────────────────────┐
     │     Portfolio Coach (optional)            │
     │  Scope → Data → Plan → Execute → Package │
     │  Optional LinkedIn post                   │
     └─────────────────┬───────────────────────┘
                       ▼
     ┌─────────────────────────────────────────┐
     │     Networking Intros (optional)         │
     │  Find contacts → Draft outreach          │
     └─────────────────┬───────────────────────┘
                       ▼
              ┌────────────────────┐
              │   WRAP-UP          │
              │   Update tracker   │
              │   Doc freshness    │
              └────────────────────┘
```

---

## Build Order & Status

| #  | Skill              | Status                                    |
|----|--------------------|-------------------------------------------|
| 1  | resume-targeter    | Tested 4x (Netflix, Lumin, Disney, Waymo) |
| 2  | decoded-jd         | Tested 1x (Waymo lifecycle)               |
| 3  | resume-scorer      | Tested 2x (Waymo, Netflix before/after)   |
| 4  | why-this-company   | Tested 2x (Waymo, Netflix speaking + cover)|
| 5  | portfolio-coach    | Tested 2x (Waymo A/B test, Netflix spend)  |
| 6  | orchestrator       | Tested 2x (Waymo Steps 1-10, Netflix full) |
| 7  | networking-intros  | Tested 2x (Waymo, Netflix)                 |
| 8  | interview-prep     | NEW v0.1.0 — see SPEC.md, regression target = Netflix Interview Prep |

---

## Current Status & What's Next

**Last session:** Session 14 of Ultimate Job Assistant (May 4, 2026) — ADR-003 visual-identity synthesis. Three PRs landed in Session 14: PR #9 (Phase 24.5 landscape doc) merged at `62dc805` after a reflog-recovery sequence; PR #10 (CLAUDE.md freshness pass + active-repo note + Cowork session workflow caveat + .gitignore hygiene) merged at `c068251`; PR #11 (ADR-003 itself, branch `adr-003/visual-identity` at `8e15ac2`) **opened and left unmerged** — Milan merges as the kickoff of Session 15 / Phase 25. Eight visual identity decisions locked (D1-D8) via interactive synthesis from the Phase 24.5 landscape evidence; daily-check-in surface is the load-bearing aspiration that cascades across most decisions.

**Completed in Job Assist (parent project):**
- Waymo lifecycle Steps 8-10 (portfolio, networking, wrap-up). Full end-to-end test complete.
- Netflix full lifecycle test (decode, score before 56%, resume, score after 82%, speaking points, cover letter, portfolio, networking)
- Folder structure consolidation, output-type restructure, all SKILL.md output paths updated

**Shipped in UJA v0.1.0 (2026-05-02, tagged):**
- Phases 0–7. Both repos on github.com/sharmingmilan: `ultimate-job-assistant` (canonical, private) and `ultimate-job-assistant-public` (deploy-source, also private as of Session 3).
- Live site at https://ultimatejobassist.netlify.app — Netlify free tier, reads the deploy-source repo via OAuth.
- `noindex` + `robots.txt: Disallow /` keep the site search-invisible.

**Shipped in UJA v0.1.1 (Session 3 — UNTAGGED, awaiting Phase 13):**
- Phase 8 zip generation, Phase 9 initial sync, Phase 10 hosting → Netlify, Phase 11 deploy-source private, Phase 12 auto-sync GitHub Action.
- Phase 13 (custom domain) deferred — gates the v0.1.1 tag.

**Shipped in UJA v0.2.0 (Sessions 4-9, tagged 2026-05-03 against `main` commit `cb66496`):**
- Phase 14: ADR-001 — architecture decisions (Skills-as-Tools, FastAPI, React/Vite/Tailwind/shadcn, sandbox, SQLite, OS keychain, distribution model).
- Phase 15 (Session 5): backend scaffold — `host/uja_host/` (sandbox, config, db, keystore, tools/, api/, main.py).
- Phase 16 (Session 6): skill registry — real `run_skill` / `propose_changes` / `ask_user`; SQLite schema v2; 20 unit tests.
- Phase 17 (Session 7): React frontend — Chat / Materials / Settings tabs + Onboarding + brand sky→pink gradient.
- Phase 17.5 (Session 8): HITL endpoints + frontend wiring — `POST /api/changes/{id}/approve|reject` + `POST /api/questions/{id}/answer` + chat resume mode + state-machine UI. Plus chat conversation-event race fix. 36 passing tests.
- **Phases 18-21 RETIRED** per ADR-002 D2 — chat-style architecture deprecated; v0.2.x picks up the new direction.
- **Phase 22 (Session 9)**: tag `v0.2.0` cut. Release message flags chat-style UX as deprecated and points at ADR-002.

**Architecture decision: ADR-002 (Session 9, 2026-05-03) — Pure Cowork + thin MCP**

See `docs/ADR-002-architecture-rethink.md`. Four decisions:

- **D1** — Pure Cowork + thin MCP server replaces agent-loop-in-host. Local FastAPI process becomes a JSON-RPC-over-stdio MCP server (no HTTP frontend, no per-user Anthropic API key, no port). Cowork drives the agent loop.
- **D2** — Tag `v0.2.0` against current `main` as a maintenance release. v0.2.x picks up the new direction.
- **D3** — Repository layout: sandbox / db / config / file_tools / skill_tools / skill_registry / HITL endpoints / 36-test suite all SURVIVE and re-shape into MCP tool functions. `keystore` + `api/auth.py` are DEMOTED. `chat.py` + `conversations.py` + `host/frontend/` are DEPRECATED-AS-REFERENCE. New `host/uja_mcp/` package added in v0.2.1.
- **D4** — v2 site reframes per Pivot B: static delivery hub for per-application zips + config templates. Deterministic zip layout (`manifest.json` + `README.md` + per-output-type subfolders). Cowork emits via `export_application` MCP tool; existing auto-sync mirrors to deploy-source; Netlify rebuilds.

Supersedes ADR-001 §D1, D2, D3, D6, D8, D10. Preserves §D4, D5, D7, D9.

**Shipped in UJA Phase 22.5 (Session 10, 2026-05-03, no version bump):**
- Per ADR-002 D3. Five deprecation stickers + one soften commit, merged at `6849f2a`. `host/frontend/README.md` (new), deprecated docstrings on `host/uja_host/main.py` / `api/chat.py` / `api/conversations.py`, demoted docstrings on `keystore.py` / `api/auth.py`. No behavior change. Tests: 36 passed, 3 skipped (unchanged). First Dispatch session for the project.

**Shipped in UJA v0.2.1 (Session 11, 2026-05-03, tagged on merge commit `e634252`, tag SHA `307e56a`):**
- Per ADR-002 D1. Phase 23 MCP server scaffold. Six atomic commits in PR #3 (`96b752d` → `c6d653b`):
  - `host/uja_mcp/` package: `server.py` (255 lines, FastMCP-based, JSON-RPC over stdio) + `tools/files.py` + `tools/skills.py` + `tools/hitl.py`. Twelve tools registered: `read_file`, `write_file`, `edit_file`, `list_files`, `read_workspace_metadata`, `list_skills`, `read_skill`, `propose_changes`, `approve_changes`, `reject_changes`, `ask_user`, `answer_question`. (`export_application` deferred to Phase 24 with comments in `tools/__init__.py` + `server.py`.)
  - `mcp>=1.27,<2.0` pinned in `host/requirements.txt`.
  - Phase 15 / 16 / 17.5 tests re-pointed from FastAPI `TestClient` at MCP tool functions; same fixture pattern. New `host/tests/test_mcp_server.py` covers `tools/list`, `tools/call`, `is_error=true` contract.
  - `start-uja-mcp.sh` (macOS/Linux) + `start-uja-mcp.bat` (Windows) launchers — informational, emit ready-to-paste Cowork MCP-config snippet with paths prefilled. Cowork owns the server's lifecycle.
  - `references/cowork-mcp-config-snippet.json` — canonical template.
  - `host/tests/live_smoke_phase23.md` — six-check user-run smoke test for the live Cowork registration.
- **Tests: 50 passed, 3 skipped** (was 36 / 3 pre-Phase-23).
- The deprecated tree (`api/chat.py`, `api/conversations.py`, `host/frontend/`) is unchanged from Session 10 per ADR-002 D3.
- Three judgment calls flagged in the Session 11 SESSION_LOG entry: (1) two deprecated chat-route tests dropped during the re-target; (2) `api/changes.py` + `api/questions.py` business logic re-implemented in `uja_mcp/tools/hitl.py` rather than refactored into shared pure functions (D3 says don't refactor the deprecated tree); (3) MCP server warns instead of fail-fast on missing project root, surfacing `ToolError` per call so the agent can drive setup interactively.
- Second Dispatch session for the project. Pattern continued to hold at ~3-4 hr / six-commit scope.

**Shipped in UJA Phase 24.5 (Session 13, 2026-05-03, no version bump — landscape research doc only):**
- Per the Phase 22.5 precedent (insert phase, no version bump). Three atomic commits on `phase24_5/research`: Block 1 (lock app list, `2607283`), Block 2 prep (provenance + skipped, `6fb10b8`), Blocks 2-4 (per-app deep dives + cross-app synthesis + recommendations, `a37db36`).
- Output: `docs/phase24_5-app-space-research.md` — 7,678-word competitive landscape covering 15 reference apps (12 in-bucket + 3 cross-domain outliers) across application trackers, AI resume tools, personal-job-dashboard templates, indie-maker hubs, and outliers (Are.na / Pinboard / Hello.cv). Each app gets a consistent rubric (visual takeaway, layout, palette, status conventions, density, standout, anti-pattern) plus user-review subsections on Huntr / Teal / Rezi.
- Cross-app analysis: layout-shape frequency tables, color-convention counts, status-nomenclature variance, density tiers, copy-voice cluster analysis (6 voice clusters surfaced; v2 maps closest to "plain-without-clubby"), privacy-messaging conventions, and a comparison of v2's ADR-002 §D4 guardrails against the landscape (positions v2 visually closer to indie-hubs cluster than to SaaS trackers).
- Eight framed-as-questions for ADR-003 (`## Recommendations for ADR-003 synthesis`): Q1 kanban-vs-flat-tag, Q2 dark-vs-light, Q3 status-pill saturation, Q4 single-vs-multi-view, Q5 privacy-as-hero-vs-footer, Q6 voice cluster, Q7 AI-foregrounding, Q8 onboarding shape. Each presents both sides with landscape evidence; none pre-decide.
- Provenance artifacts: `docs/phase24_5-screenshots/` with 15 `<app-slug>-source.md` files capturing where each visual reference came from (binaries weren't bridged to the sandbox; doc references URLs + provenance metadata rather than embedded images), plus `docs/phase24_5-research-scratchpad.md` documenting Block 1's app-selection process.
- PR #9 merged in Session 14 Block 1 at `62dc805` after a recovery sequence — first merge attempt was interrupted by a `git pull` auth prompt; cleanup pushed `--delete` before verifying merge state, which auto-closed the PR. Recovery: re-pushed branch from reflog (`a37db36`), re-opened PR via PATCH, merged via PUT. Pattern documented in Session 14 entry as the "always check API status before cleanup" lesson.

**Next up (in priority order):**

Session 15 picks up via the paste-ready prompt at `docs/session-15-cowork-prompt.md` (committed in Session 14, PR #11). The prompt orients a fresh Cowork session on "review and merge ADR-003 → re-edit session-14-brief.md → start Phase 25." Dispatch pattern abandoned per Session 13 — all sessions are interactive Cowork.

1. **Session 15 kickoff — merge PR #11 (ADR-003) and re-edit `docs/session-14-brief.md`.** PR #11 is open against `main` from branch `adr-003/visual-identity`. The deferred Phase 25 brief at `docs/session-14-brief.md` (on branch `docs/session-14-brief-draft` at `914d9e4`) predates ADR-003 and references "Canva MCP visual exploration first" as Phase 25 Block 1 — superseded. Block 1 should become "ADR-003 implementation pass: light-variant palette, theme toggle, About page, copy review." Open as a separate PR off main; merge before Phase 25 implementation starts.

2. **Phase 24 — Export pipeline (PR #7, branch `phase24/export-pipeline` at `5879f3f`, OPEN against `main`).** Five commits, 87 tests passing per Session 12 brief. **Phase 25 stacks on this branch, not on main.** Phase 24 + Phase 25 ship as combined `v0.2.3` (skipping `v0.2.2`). Decision per the Session 13 → 14 handoff doc.

3. **Phase 25 — v2 site rebuild (target `v0.2.3`).** Per ADR-002 §D4 + ADR-003 D1-D8. Static `index.html` + JS that fetches `exports/index.json` and `templates/index.json` and renders cards. Three sections: Application packages / Config templates / About. Inherits ADR-003 locked design (no Canva MCP exploration needed). Branch from `phase24/export-pipeline` (Phase 24 + Phase 25 ship combined as `v0.2.3`).

4. **Live smoke-test the v0.2.1 build.** Run `host/tests/live_smoke_phase23.md` against a real Cowork session — register the MCP server via the snippet from `start-uja-mcp.sh`, walk the six checks. The genuine acceptance gate; the test suite proves the tool-function contract, only a live Cowork session proves the JSON-RPC stdio framing. Can run in parallel with Phase 25.

5. **v0.4.0 workflow UI design spike (deferred).** Sims-style structured workflow tracker as a Cowork artifact per ADR-002 §D1. Parked for a future ADR after v0.2.3 lands per the Session 13 → 14 handoff doc.

**v0.3.0 — PARKED.** Cowork is itself the desktop app; wrapping a non-existent web app in Tauri is moot. Plausible reframings (polished MCP installer, headless export mode, or skip) deferred to a future ADR after v0.2.x lands. Do not start any Tauri work.

**What's preserved from earlier sessions and survives ADR-002:** the FastAPI backend skeleton (deprecated, kept as reference), sandbox helper, file API, persistence layer (SQLite schema v2), OS-keychain key store (demoted but kept), `propose_changes`/`ask_user` primitives, the HITL approve/reject/answer logic (re-implemented in `uja_mcp/tools/hitl.py` per D3, FastAPI copy intentionally untouched), the Skills-as-Tools registry, and the test suite (50 passing tests as of v0.2.1, up from 36 pre-Phase-23). The MCP layer in `host/uja_mcp/` is a thin facade over this surviving infrastructure.

---

## Key Principles

- **No fabrication** -- all company claims sourced and cited
- **Human-in-the-loop** -- nothing auto-generated without approval
- **Specific over vague** -- metrics, tools, outcomes in every bullet
- **Plug-and-play** -- skill logic separated from user data so repo is forkable
- **Doc freshness** -- propose updates at end of every session

---

## Working Principles (Session 8 codification)

These four principles govern HOW work happens in any session, not WHAT the project does. Asked for explicitly by Milan in Session 8.

- **Human-in-the-loop (HITL)** -- ask clarifying questions before non-trivial work; never assume scope; surface decisions for approval before acting. The HITL endpoints shipped in Phase 17.5 are the system-level expression of this principle.
- **Atomic** -- one logical change per commit, one branch per block-piece, `--no-ff` merge to main. Reverting any single piece should be possible without surgery on unrelated changes. Sessions 6, 7, and 8 follow this pattern (look at `git log` for the commit-by-commit shape).
- **Deterministic** -- same inputs produce same outputs. No flaky tests. No timestamps in committed artifacts. Pinned dependency versions in `host/requirements.txt` and `host/frontend/package.json`. Tests use fixed fixtures, not wall-clock-dependent state.
- **Evidence-based** -- every claim backed by a file path, a line number, a search result, or a web source. No fabrication. When debugging, "I think X is the cause" is replaced with "lines 67-77 of ChatTab.tsx show X, the backend log at timestamp Y confirms Z, therefore the cause is W."

### Dispatch session pattern (Session 9 codification)

Headless / hands-off sessions run via Claude Code Dispatch. The pattern keeps the orchestrator-style autonomy of "you are the planner, executor, evaluator, and quality gate" while working around Dispatch's isolation from the originating Cowork session's context.

**Two-layer prompt:**

1. **The brief lives on disk.** `docs/session-N-brief.md` is the substantive content — orientation file list, deliverable, blocks, working principles re-affirmed, success criteria, end-of-session deliverables, out-of-scope list. Version-controlled, reviewable in PRs, accessible to any surface (Dispatch / Code / desktop / web) because the Dispatch worktree includes it.
2. **The launcher prompt is thin.** `scripts/dispatch-session.sh <N>` emits a `claude://` URL with a compact orchestrator-style prompt prefilled. The prompt points at the brief and tells the agent to execute it autonomously. Reusable for any session — the per-session work lives in the brief.

**Why brief-on-disk + thin-prompt-from-script:**

- Dispatch sessions are fully isolated from parent Cowork context (verified via the open GitHub issue documenting this). They have full repo file access via Git worktrees but no inherited memory.
- Encoding the entire session brief into the URL itself is brittle (URL length limits, no version control, no PR review).
- Brief-on-disk + thin-prompt = the brief carries substance; the URL stays small; the brief survives across sessions and surfaces.

**Mechanics:**

- `bash scripts/dispatch-session.sh 10` reads `docs/session-10-brief.md`, builds the orchestrator-style prompt, URL-encodes it, prints the `claude://` URL, and (on macOS) copies it to the clipboard. Add `--open` to launch it directly.
- Click the URL → Claude Desktop opens with the prompt prefilled. Review it (per the link-safety rules), hit send. Dispatch routes to a Code session if the work is dev-shaped.
- The Dispatch session reads its orientation files (CLAUDE.md, SPEC.md §14, the latest ADR, recent SESSION_LOG entries, then the brief) and executes.

**Branch + merge discipline differs from interactive sessions:**

- Dispatch session works on a feature branch and opens a PR. It does NOT push to `main` or tag releases — those belong to the originating Cowork session per the human-in-the-loop principle.
- The Cowork session reviews the PR, merges with `--no-ff` (preserving the merge-commit pattern from Sessions 6-9), and cuts any tags.

**When to dispatch vs run interactively:**

- **Dispatch:** small atomic phases (Phase 22.5 / docs cleanup), heads-down implementation work with a clear deliverable + acceptance gate (Phase 23 / 24 / 25), parallelizable work (Phase 24 + 25 could run as two Dispatch sessions in parallel).
- **Interactive Cowork:** anything that needs cross-doc reasoning, ADR drafting, decisions Milan wants to be in the room for, debugging that requires surfacing partial state mid-stream.

The Dispatch pattern was codified in Session 9 after ADR-002 landed; first use was Session 10 (Phase 22.5).

### Credential handling pattern (Session 8 — load-bearing)

Any credential (PAT, API key, OAuth token) MUST be delivered safely. Two failure modes observed in Session 8:

1. **Pasting into chat.** The transcript persists permanently. Both a GitHub PAT and an Anthropic API key were leaked this way before the pattern was established. Always rotate any credential that lands in chat.
2. **`cat`-then-`pbcopy` mid-Terminal-session.** Terminal scrollback retains the displayed value; selecting nearby output for an unrelated paste exposes the secret again.

Standard pattern going forward:

```bash
# User writes the credential to a file in the workspace folder
mkdir -p "<workspace>/.session-secrets"
echo "PASTE_TOKEN_HERE" > "<workspace>/.session-secrets/cred-name.txt"
chmod 600 "<workspace>/.session-secrets/cred-name.txt"

# .gitignore must include .session-secrets/

# Claude reads it via Read tool (file content goes only to model context, not visible in chat output)
# OR consumes it in bash with stderr-redacted commands:
TOKEN=$(cat "<workspace>/.session-secrets/cred-name.txt" | tr -d '[:space:]')
git clone "https://x-access-token:${TOKEN}@github.com/owner/repo.git" target 2>&1 \
    | sed -E 's|x-access-token:[^@]+@|x-access-token:<REDACTED>@|g'
unset TOKEN

# Folder gets cleaned up at end of session
```

For local-app onboarding screens (UJA's API key field, etc.):

```bash
# Put on clipboard silently — never display in Terminal
cat "<path>/key.txt" | tr -d '\n' | pbcopy
```

#### Cowork session workflow (Session 14, 2026-05-04 — load-bearing)

Git operations in a Cowork session split across two surfaces:

- **Claude side** prepares the commands (one bash block per branch: commit + push + PR + merge + cleanup) and runs read-only git ops (`git status`, `git diff`, `git log`) in sandbox bash.
- **You** run the prepared block in your local terminal.

Why the split: the Cowork sandbox cannot write to `.git/` (FS-layer restriction — the sandbox uid owns the directory but writes are still rejected; reads and `git log` / `git diff` / `git status` work fine). Your terminal has full access. We commit / push / PR / merge from your terminal exactly as in any normal repo, just with the block prepared by Claude.

Repository visibility (public vs private) does not change the pattern — the PAT still controls write access regardless, so it stays in your terminal and is stderr-redacted with `sed` when echoed.

Sessions 11 (Phase 23, Dispatch) and 14 (Phase 24.5 merge + this freshness pass, Cowork) demonstrate the two halves. The Dispatch session runs git itself; the Cowork session hands off a prepared block.

**If a `.git/index.lock` stale file blocks a commit**, run `rm .git/index.lock` from your terminal first — the sandbox can't clean these up.

---

## Doc Freshness Protocol

### Two Triggers

**Development sessions** (editing skills, architecture): May need updates to CLAUDE.md, SKILL.md files, DESIGN_DOC.md, tracker.md.

**Workflow runs** (applying to a job): May need updates to CLAUDE.md, tracker.md, research files, curated-datasets.json, networking files.

### Update Format

Dual-layer: quick **summary** to skim + **detailed changes** underneath if you want to verify.

### Thorough Consistency Audit (mandatory at end of every session)

Before proposing updates, perform a full audit:

1. **Formatting rules compliance**: Grep all .md files in output folders for em dashes, en dashes, and other violations. Fix all.
2. **Folder structure compliance**: Verify every company has `research/[company].md`. Verify tracker.md has a row for every active application.
3. **Research brief format**: Verify two-section structure (Company Research + Role-Specific with dated subsections).
4. **Cross-file consistency**: Verify status claims in CLAUDE.md, DESIGN_DOC.md, tracker.md all agree with reality.
5. **Naming convention compliance**: Verify all output files follow `[company]-[role-slug]-[YYYY-MM].[ext]`.
6. **Date freshness**: Verify `Last updated:` lines are current on modified files.

Use grep/glob to scan programmatically. Document issues and fix before proposing the session update.

### Rules

- Updates are **proposed, never auto-applied**. User approves or rejects.
- Happens at **end of session**, not mid-workflow.
- Only files that actually changed get proposed.
- Never deletes content -- adds, modifies, or restructures.
- Each updated file gets a refreshed `Last updated:` line.

---

## GitHub Separation

Active repo: `sharmingmilan/ultimate-job-assistant-v2` (private, branched from `ultimate-job-assistant` in Session 4 / v0.2.0).

```
# What gets pushed (plug-and-play for others)
skills/                  ← all skill logic, generic
references/              ← templates, scripts, examples, patterns
CLAUDE.md                ← structure template (with placeholder routing)
DESIGN_DOC.md            ← skill specs and design decisions

# What stays local (personal data -- currently private repo, strip before making public)
base-resumes/            ← base resumes
research/                ← company research files
decoded-jds/             ← decoded JDs
resumes/                 ← targeted resumes
scores/                  ← score reports
speaking-points/         ← speaking points
cover-letters/           ← cover letters
interview-prep/          ← recruiter prep, thank-you letters
portfolio/               ← portfolio projects
networking/              ← contacts and outreach
archive/                 ← completed apps
memory.md                ← personal stories and preferences
tracker.md               ← application statuses
SESSION_LOG.md           ← session history
```
