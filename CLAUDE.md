# CLAUDE.md -- Ultimate Job Assistant
# Last updated: 2026-05-02 (Session 1 of UJA — forked from Job Assist Session 9)

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

**Last session:** Session 1 of Ultimate Job Assistant (May 2, 2026) — forked from Job Assist Session 9

**Completed in Job Assist (parent project):**
- Waymo lifecycle Steps 8-10 (portfolio, networking, wrap-up). Full end-to-end test complete.
- Netflix full lifecycle test (decode, score before 56%, resume, score after 82%, speaking points, cover letter, portfolio, networking)
- Folder structure consolidation, output-type restructure, all SKILL.md output paths updated

**Shipped in UJA v0.1.0 (2026-05-02, tagged):**
- Phases 0–7 complete. Two GitHub repos exist on github.com/sharmingmilan: `ultimate-job-assistant` (private) and `ultimate-job-assistant-public` (currently public).
- Site live at https://sharmingmilan.github.io/ultimate-job-assistant-public/
- `noindex` + `robots.txt: Disallow /` added post-v0.1.0; site is search-invisible.
- Landing page simplified to a download-first design (single "Download the latest" CTA).

**In progress (UJA v0.1.1 — see SPEC.md §14 for full phase list):**
- Phase 8: Add zip generation to `scripts/sync_to_public.py` (regenerates `website/downloads/ultimate-job-assistant.zip` on every sync).
- Phase 9: Migrate hosting from GitHub Pages → Netlify (free tier, reads private repos via OAuth).
- Phase 10: Flip `ultimate-job-assistant-public` to private. The "public" in the name becomes historical — both repos are private; Netlify reads the deploy-source repo via OAuth.
- Phase 11: GitHub Action on canonical private repo for auto-sync on every push to main.
- Phase 12: Wire custom domain to Netlify (Milan buys ~$12/yr, Claude does DNS).
- Tag `v0.1.1` after Phase 12 ships.

**Next up after v0.1.1:**
- First real run of `interview-prep` against an actual upcoming application.
- See ROADMAP.md for longer-term tracks (SaaS pivot, in-browser code execution, real spaced repetition).

---

## Key Principles

- **No fabrication** -- all company claims sourced and cited
- **Human-in-the-loop** -- nothing auto-generated without approval
- **Specific over vague** -- metrics, tools, outcomes in every bullet
- **Plug-and-play** -- skill logic separated from user data so repo is forkable
- **Doc freshness** -- propose updates at end of every session

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
