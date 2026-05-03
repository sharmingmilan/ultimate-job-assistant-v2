# CLAUDE.md -- Ultimate Job Assistant
# Last updated: 2026-05-03 (Session 8 — Phase 17.5 ships + chat race fix + strategic pivots locked)

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

**Last session:** Session 8 of Ultimate Job Assistant (May 3, 2026) — Phase 17.5 (close-the-HITL-loop) shipped, chat conversation-event race condition fixed, three strategic pivots locked that reshape v0.2.0+ scope.

**Completed in Job Assist (parent project):**
- Waymo lifecycle Steps 8-10 (portfolio, networking, wrap-up). Full end-to-end test complete.
- Netflix full lifecycle test (decode, score before 56%, resume, score after 82%, speaking points, cover letter, portfolio, networking)
- Folder structure consolidation, output-type restructure, all SKILL.md output paths updated

**Shipped in UJA v0.1.0 (2026-05-02, tagged):**
- Phases 0–7 complete. Both repos on github.com/sharmingmilan: `ultimate-job-assistant` (canonical, private) and `ultimate-job-assistant-public` (deploy-source, also private as of Session 3).
- Live site at https://ultimatejobassist.netlify.app — Netlify free tier, reads the deploy-source repo via OAuth.
- `noindex` + `robots.txt: Disallow /` keep the site search-invisible.
- Landing page is download-first: single "Download the latest" CTA + HEAD-fetch JS for size/date.

**Shipped in UJA v0.1.1 (Session 3, 2026-05-02 — UNTAGGED, awaiting Phase 13):**
- Phase 8: zip generation in `scripts/sync_to_public.py` — `build_zip()` curates `website/downloads/ultimate-job-assistant.zip` on every sync (drops maintainer-only paths, injects `references/zip-bundle/` user templates, verifies `ZIP_REQUIRED_MEMBERS`).
- Phase 9: initial sync after zip-build — both repos pushed.
- Phase 10: hosting migrated GitHub Pages → Netlify.
- Phase 11: deploy-source repo flipped to private (Netlify OAuth retains access).
- Phase 12: auto-sync GitHub Action `auto-sync-to-public.yml` shipped end-to-end. Triggers on every push to canonical `main`. Uses fine-grained PAT (`PUBLIC_REPO_TOKEN`, Contents: Read+write, scoped only to deploy-source). Round-trip latency push → live zip ≈ 30 s. ONBOARDING.md Step 7 documents the setup for forkers.

**Deferred (gates the v0.1.1 tag):**
- Phase 13: custom domain. Awaiting Milan to purchase (`ujassist.app` or `ultimatejobassistant.com`, ~$12/yr). When it lands, walk through Netlify "Add custom domain" + DNS records, then tag `v0.1.1`.

**In flight (UJA v0.2.0 — Session 6, on v2 canonical's `main`):**
Self-hosted local web app where the user runs UJA in a browser against their own Anthropic API key. Architecture decisions locked in Session 4 (see `docs/ADR-001-v0.2.0-architecture.md` and SPEC.md §14):
- **Skill execution:** Skills-as-Tools. SKILL.md files stay as the source of truth. Host registers a fixed tool catalog with the Anthropic API; the agent loop stays inside Claude. Cowork mode and web-app mode become two surfaces over the same skills.
- **Backend:** Python + FastAPI (reuses existing `scripts/` unchanged).
- **Frontend:** React + Vite + Tailwind + shadcn/ui (using the `anthropic-skills:web-artifacts-builder` patterns).
- **Distribution:** curated-zip extension with `start-uja.sh` + `start-uja.bat`. Prereq: Python 3.11+.
- **Persistence:** SQLite at the project root, schema-versioned, append-only.
- **Sandbox:** backend reads/writes only the project-root folder picked at first launch. API key encrypted at rest via OS keychain (`keyring`). Server binds 127.0.0.1 only.
- **Branch protection:** GitHub branch protection / rulesets are Pro-gated on free private repos. Replaced by a local pre-push hook (`references/git-hooks/pre-push`) that refuses direct pushes to `main`. Run `bash scripts/install-hooks.sh` after cloning canonical to install it. Hook detects v1 vs v2 canonical so the warning text matches the canonical you're pushing to.

**Shipped in UJA Session 5 (2026-05-02 evening, on `dev/v0.2.0`):**
- Phase 15 backend scaffold landed: `host/uja_host/` (sandbox, config, db, keystore, tools/, api/, main.py), `start-uja.sh`, `start-uja.bat`, pytest acceptance test, live_smoke.sh. 1,814 lines. Commit `1259f59`.
- v2 repo separation prep landed: `V2_SETUP.md` (188-line handoff doc), `scripts/sync_to_public_v2.py`, `website/v2/index.html` + `robots.txt` + `netlify.toml`.
- v2 repos created and live: canonical `sharmingmilan/ultimate-job-assistant-v2`, deploy-source `sharmingmilan/ultimate-job-assistant-v2-public`, both private, site at https://ultimatejobassist-v2.netlify.app.

**Shipped in UJA Session 6 (2026-05-02 same-day continuation, on v2 canonical's `main`):**
- Phase 16 — skill registry. Replaced `host/uja_host/tools/skill_stubs.py` with three real implementations in `skill_tools.py`: `run_skill` (catalog + load mode following Skills-as-Tools per ADR D1), `propose_changes` (persisted pending change-sets, sandbox-bounded, no-op on disk until approved), `ask_user` (persisted pending questions). New `skill_registry.py` discovery module walks `skills/*/SKILL.md` and parses YAML frontmatter. SQLite schema v2 migration adds `pending_changes` + `pending_questions` tables with repository helpers. Tool catalog stays at 8 entries; `run_skill.name` moved from required to optional so catalog mode works. `api/chat.py` SYSTEM_PROMPT rewritten to teach the model the new primitives.
- Phase 16 — tests. 20 unit tests in `host/tests/test_phase16_skill_registry.py` cover discovery, the three tools, sandbox boundaries, and dispatcher error surfacing. 3 live integration smoke skeletons in `tests/integration/test_phase16_smoke.py` gated on `UJA_RUN_LIVE_TESTS=1`. Existing Phase 15 acceptance test still passes (21 passed, 3 skipped).
- Cleanup — pre-push hook now detects v1 vs v2 canonical for accurate warning text. V2_SETUP.md Step 2 has a footgun callout for the GitHub fine-grained PAT "All repositories" radio defaulting on edit.
- Commits on v2 canonical `main`: `91d51c2` (hook), `5670c15` (V2_SETUP), `e84f1db` (skill_tools), `a2c8502` (tests), `2c0fd74` (`--no-ff` merge of `phase16/skill-registry`).

**Shipped in UJA Session 7 (2026-05-02 same-day continuation, on v2 canonical's `main`):**
- Phase 17 — React + Vite + Tailwind + shadcn/ui frontend in `host/frontend/`. Vite 8 + React 19 + TS 6, scaffolded with the `anthropic-skills:web-artifacts-builder` pattern, then trimmed to only the eight shadcn primitives the app actually uses (button, card, input, label, alert, scroll-area, textarea, separator). Brand sky→pink gradient from the v2 logo (`3cc7d46`) wired as `bg-brand-gradient` + `text-brand-sky/pink`. System font stack (no Inter — avoids the AI-slop tell).
- Three primary tabs all built to the ADR §D10 polish bar (empty / loading / error states on every surface; `cmd+1`/`cmd+2`/`cmd+3` jumps tabs; `cmd+enter` sends; `esc` cancels in-flight chat; WCAG AA focus rings; aria-* on every interactive):
  - Chat: conversation sidebar against `/api/conversations`, composer that streams `/api/chat` as SSE, renders text + tool_use + tool_result blocks. `propose_changes` and `ask_user` tool_use blocks render dedicated diff / question cards (approve/reject + answer wiring deferred to Phase 17.5; the change-set + question primitives already persist server-side from Phase 16).
  - Materials: lazy file tree against the new `/api/files/tree`. Right-pane previewer routes by extension — md (marked + DOMPurify), docx (mammoth via deferred import), pdf (native iframe; PDF.js upgrade is a 17.5 polish task), text-ish, image. Per ADR §D4 all rendering is client-side.
  - Settings: project root (PUT /api/config/project-root), API key (write-only, never reads back from server, surfaces memory-fallback warning), theme picker, conversation list with delete (DELETE /api/conversations/{id}), about card (host version, schema version, root path).
- Two-step Onboarding flow that takes over the main pane when `/api/health` reports `project_root_configured: false`. Maps to existing config + auth endpoints; bad keys rejected via `test_connection: true` before they hit the keychain.
- Backend additions (Phase 17 piece 1 of 3, commit `eb064f4`): new `host/uja_host/api/files.py` (GET /tree, /text, /raw — sandbox-bounded, 1 MB text cap, 25 MB raw cap), `delete_conversation()` helper + DELETE endpoint (cascades through pending_changes / pending_questions via existing FKs), `main.py` mounts `host/frontend/dist/` at `/` via StaticFiles in production.
- Acceptance gate cleared:
  - `npm run build` green: ~118 KB gzipped initial bundle (CSS + react + radix + app + preview-md). mammoth (~119 KB gz) correctly deferred — only loads when a `.docx` file is opened.
  - `tsc -b` green (with `ignoreDeprecations: 6.0` for TS 6's deprecated `baseUrl` warning — needed for shadcn @/ aliasing).
  - `pytest`: 21 passed / 3 skipped (unchanged from Session 6).
  - TestClient smoke: `GET /` serves the SPA shell, `/api/health` returns 200, `/api/files/tree` 409s without project root and lists tree with one configured. Sandbox enforcement still rejects `..` traversal.
- Atomic commits on three feature branches (`phase17/files-api`, `phase17/frontend-scaffold`, `phase17/frontend-tabs`), `--no-ff` merged to v2 canonical `main` per the Session 6 pattern. Final `main` HEAD: `c821f2d`.

**v2 repo + site separation (decided 2026-05-02 / Session 5):**
- v0.1.x stays at `sharmingmilan/ultimate-job-assistant` (canonical) + `sharmingmilan/ultimate-job-assistant-public` (deploy-source) → `https://ultimatejobassist.netlify.app`. Untouched.
- v0.2.0 lives at `sharmingmilan/ultimate-job-assistant-v2` (canonical, private) + `sharmingmilan/ultimate-job-assistant-v2-public` (deploy-source, private) → `https://ultimatejobassist-v2.netlify.app`.
- Long-term shape (one site or two) is parked. Decide post-Phase 17 when the React frontend exists.

**Shipped in UJA Session 8 (2026-05-03):**

- **Chat conversation-event race fix** (commit `95b1ef5`, merge `d4ae9c0`): load-history `useEffect` was wiping in-flight asstRow on every `conversation` SSE event, silently dropping all subsequent text/tool_use/tool_result. Fix tracks the streaming conversation via a ref, useEffect skips fetch when the in-flight stream owns the active conversation. 8 lines added to `ChatTab.tsx`.

- **Phase 17.5 — HITL endpoints + frontend wiring + tests** (3 commits + merge `8a68e85`): `POST /api/changes/{id}/approve|reject` (sandbox-bounded disk writes + idempotency), `POST /api/questions/{id}/answer` (records + synthesizes user message into conversation), `chat.py` resume-mode (empty body when conversation_id set), frontend wires real Approve/Reject/Send-answer with state machine (pending → submitting → applied/rejected/answered/error) and auto-resume after each action. 15 unit tests, full suite 36/36 green.

- **Two reusable patterns**: `.session-secrets/` for safely-delivered credentials (write to file, never paste in chat); test-workspace pattern (`cp -R ~/code/uja-v2 ~/code/uja-test-workspace`) for sandboxed agent writes.

**Strategic pivots locked this session — Block B/C/D and v0.2.0 ship plan paused (see SESSION_LOG.md Session 8 for detail):**

- **Pivot A** — Chat-style UI is the wrong metaphor for job-application workflows. v0.4.0 will be a Sims-style structured workflow tracker (per-application stages, discrete decisions, visible state, branching, undo). Canva MCP for design exploration. Chat becomes a sidecar.
- **Pivot B** — v2 Netlify site reframes from "marketing landing for the local web app" to "delivery hub for **exportable** application packages + config templates." One zip per company-role containing decoded JD, targeted resume, cover letter, score, speaking points. Designed to be downloaded, sent to recruiters, archived, or shared. Static, search-invisible, URL-only access.
- **Pivot C** — Anthropic-API-key + local-web-app architecture being reconsidered. Workflow likely stays in Cowork; local infrastructure exists for tooling (file ops, sandbox, persistence) not for running the agent loop. Reusable: backend, sandbox, file API, HITL endpoints, OS keychain. Deprecating: chat tab as primary surface, agent-loop-in-host pattern.

**Next up (in priority order, all deferred from this session):**

1. **ADR-002 — v0.2.0+ architecture rethink** based on Pivots A/B/C. Decide what ships under the v0.2.0 tag (probably just the bug fixes + HITL endpoints as a maintenance release), what becomes v0.2.x / v0.3.0 / v0.4.0. Update SPEC §14 phase plan.
2. **v2 site rebuild per Pivot B** — **exportable** application package + config delivery hub. Static. No marketing. Canva MCP for visual style. ~1-2 day rebuild from scratch.
3. **v0.4.0 workflow UI design exploration** — Sims-style game UI references via Canva MCP, sketch the structured workflow tracker, prototype one application's stage view, gather feedback.
4. **v0.3.0 Tauri double-click app** stays planned for after v0.2.0 ships (whatever v0.2.0 ends up meaning post-rethink). Per-OS distribution: .dmg / .msi / .AppImage. Bundles Python interpreter so users install nothing.

**What's preserved from earlier sessions and survives all pivots:** the FastAPI backend, sandbox helper, file API, persistence layer, OS-keychain key store, propose_changes/ask_user primitives, the HITL approve/reject/answer endpoints from this session, the test suite (36 passing tests). These are infrastructure the next architecture sits on top of.

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
