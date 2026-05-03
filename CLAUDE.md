# CLAUDE.md -- Ultimate Job Assistant
# Last updated: 2026-05-03 (Session 9 — ADR-002 lands + v0.2.0 tagged as maintenance release)

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

**Last session:** Session 9 of Ultimate Job Assistant (May 3, 2026) — ADR-002 (v0.2.0+ architecture rethink) landed; v0.2.0 tagged against `main` as a maintenance release per D2.

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

**Next up (in priority order):**

Phases 22.5 and 23 are split across Sessions 10 and 11 to stage the Dispatch-session pattern (Session 10 = small cheap test; Session 11 = the larger shipping-target work). Briefs for both live on disk at `docs/session-10-brief.md` and `docs/session-11-brief.md`. Launch a Dispatch session for either via `bash scripts/dispatch-session.sh <N>` (emits a `claude://` deep link with the orchestrator-style prompt prefilled).

1. **Phase 22.5 — Deprecation marking (Session 10, ~30-45 min).** Per ADR-002 D3. Add `host/frontend/README.md` flagging it as deprecated reference. Docstring headers on `host/uja_host/main.py`, `api/chat.py`, `api/conversations.py`. Demote `keystore.py` + `api/auth.py`. Cheap test of the Dispatch-session pattern before Phase 23 commits to a longer session. No version bump. See `docs/session-10-brief.md`.

2. **Phase 23 — MCP server scaffold (Session 11, target v0.2.1, ~3-4 hr).** Stand up `host/uja_mcp/server.py` (JSON-RPC over stdio per the `mcp-builder` skill's Python guidance). Register file + skill + HITL + `read_workspace_metadata` tools. Pin `mcp` in `host/requirements.txt`. Re-point the Phase 15/16/17.5 tests at MCP tool functions. New `host/tests/test_mcp_server.py`. New `start-uja-mcp.sh` / `start-uja-mcp.bat` launcher + `references/cowork-mcp-config-snippet.json`. Tag `v0.2.1` end of session. See `docs/session-11-brief.md`.

3. **Phase 24 — Export pipeline (target v0.2.2).** Implement `export_application(company_role)` MCP tool per ADR-002 D4. Deterministic zip bytes (sorted ordering, fixed compression, zeroed timestamps). Tests for manifest schema + determinism + sandbox-bounded writes.

4. **Phase 25 — v2 site rebuild (target v0.2.3).** Per ADR-002 D4. Static `index.html` + JS that fetches `exports/index.json` and `templates/index.json` and renders cards. Three sections: Application packages / Config templates / About. Canva MCP visual exploration first. `scripts/sync_to_public_v2.py` allowlist updated. Re-raise custom-domain question.

5. **v0.4.0 workflow UI Canva MCP design spike (parallel to Phase 23).** Sims-style game UI references, sketch the structured workflow tracker, prototype one application's stage view. The tracker is a Cowork artifact (per ADR-002 D1) that calls back into the v0.2.x MCP server through `window.cowork.callMcpTool`.

**v0.3.0 — PARKED.** Cowork is itself the desktop app; wrapping a non-existent web app in Tauri is moot. Plausible reframings (polished MCP installer, headless export mode, or skip) deferred to ADR-003 after v0.2.x lands. Do not start any Tauri work.

**What's preserved from earlier sessions and survives ADR-002:** the FastAPI backend skeleton, sandbox helper, file API, persistence layer (SQLite schema v2), OS-keychain key store (demoted but kept), `propose_changes`/`ask_user` primitives, the HITL approve/reject/answer endpoints, the Skills-as-Tools registry, the test suite (36 passing tests), the test fixtures pattern (TestClient + monkeypatched config + tmp_path-rooted SQLite). These are infrastructure the next architecture sits on top of.

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
