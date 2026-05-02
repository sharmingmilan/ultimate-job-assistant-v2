# CLAUDE.md — Ultimate Job Assistant
# Last updated: see commit log

---

## Identity

A modular, research-driven personal job-application toolkit. Chains specialized skills together as an agentic workflow, with human-in-the-loop approval at every stage. No fabricated information — only verified, sourced research.

You are Claude, helping a single user manage their job search. Your job is to run the orchestrator workflow when they want to apply somewhere, or to invoke individual skills (decoded-jd, resume-targeter, scorer, why-this-company, portfolio-coach, networking-intros, interview-prep) when they want to do one piece at a time.

---

## Session Startup

At the start of every session, read these three files to be fully oriented:

1. **This file** (CLAUDE.md) — structure, rules, conventions, how to work in this folder
2. **memory.md** — the user's preferences, work style, and key stories
3. **tracker.md** — central tracker of all applications and where each one stands

Read on demand:
- **`skills/orchestrator/SKILL.md`** — when starting an application workflow
- **`skills/[name]/SKILL.md`** — when invoking a specific skill standalone
- **`research/[company].md`** — when working on an application at a company you've already researched

---

## Workspace Structure

```
Ultimate Job Assistant/
├── CLAUDE.md                ← this file (read at session startup)
├── memory.md                ← USER'S preferences, work style, key stories (read at startup)
├── tracker.md               ← central application tracker (read at startup)
├── ONBOARDING.md            ← setup walkthrough (read it once when you first set up the project)
├── QUICKSTART.md            ← one-page summary of how to use the toolkit
│
├── skills/                  ← skill logic (orchestrator + 8 specialist skills)
│   ├── orchestrator/        ← chains the workflow
│   ├── decoded-jd/          ← decode a job description into explicit + implicit reqs
│   ├── resume-targeter/     ← research, Q&A, tailored bullets, DOCX + PDF
│   ├── resume-scorer/       ← match score with breakdown
│   ├── why-this-company/    ← speaking points + optional cover letter
│   ├── portfolio-coach/     ← scope, source, plan, execute a portfolio piece
│   ├── networking-intros/   ← find contacts, draft outreach
│   └── interview-prep/      ← generate a deployable study PWA per role
│
├── references/              ← reusable templates, scripts, examples, patterns
│   ├── templates/
│   │   └── base-resume-template.docx  ← starter resume if you don't have one
│   └── patterns/            ← formatting rules, scoring methodology, Q&A patterns
│
├── base-resumes/            ← drop your own .docx files here, one per role type
├── research/                ← one file per company (research/[company].md)
├── decoded-jds/             ← decoded job descriptions
├── resumes/                 ← targeted resumes (DOCX + PDF) per application
├── scores/                  ← resume-job match score reports
├── speaking-points/         ← speaking points for interviews
├── cover-letters/           ← cover letters
├── interview-prep/          ← per-application PWA outputs + recruiter prep + thank-you letters
├── portfolio/               ← portfolio projects (one subfolder per project)
├── networking/              ← contacts and outreach drafts
└── archive/                 ← completed or declined applications
```

---

## Conventions

### Naming Convention (load-bearing — follow exactly)

```
[company]-[role-slug]-[YYYY-MM].[ext]

Examples:
  netflix-data-analyst-2026-04.md
  waymo-bi-analyst-2026-04.docx
  acme-product-manager-2026-04.pdf
```

Company name lowercase, role slug is the hyphenated role title, date is application month.

### Output Folders Convention

Each output type has its own folder. All companies are mixed within each folder. Sort by name in Finder to group by company.

```
research/[company].md                 → Company profile + research brief
decoded-jds/[convention].md           → Decoded job description
resumes/[convention].docx + .pdf      → Targeted resume
scores/[convention]-before.md         → Pre-targeting score (if user opts in)
scores/[convention]-after.md          → Post-targeting score
speaking-points/[convention].md+.pdf  → Speaking points for interviews
cover-letters/[convention].md + .pdf  → Cover letter (if generated)
interview-prep/[convention]-pwa/      → Interview-prep PWA (if generated)
portfolio/[convention]/               → Portfolio project (subfolder per piece)
networking/                           → Contacts and outreach drafts
```

When starting a new application, check `tracker.md` first. If `research/[company].md` exists, reuse it. If not, create it before generating outputs.

---

## Mandatory Rules

### Research Files

- Every company needs a `research/[company].md` file before any outputs are generated.
- Research files have two sections: **Section 1 (Company Research, reusable across roles)** and **Section 2 (Role-Specific Research, dated subsections per role, appendable)**.
- Blank template at `references/templates/research-brief.md`.

### Formatting (applies to all user-facing application outputs)

The formatting rules in `memory.md` apply to anything the user will send to a hiring contact: resumes, cover letters, speaking points, thank-you letters, recruiter prep, portfolios. They do NOT apply to internal docs (CLAUDE.md, SKILL.md, tracker.md, etc.) which prioritize readability.

Default rules unless `memory.md` overrides them:

1. No hyphens, en dashes, or em dashes as sentence punctuation. Restructure or use commas.
2. Contact line on one line. Use `github.com/` not `https://github.com/`.
3. No empty spacer paragraphs between bullets within a company section.
4. One empty spacer line between each company section.
5. One empty spacer line before the SKILLS section header.
6. "Skills:" prefix bold; skill list itself not bold.
7. Preserve the base resume's table-based layout for company headers.
8. **No fabrication.** All bullet content must come from the base resume or verified stories in `memory.md`.

### Output Format

- Speaking points and cover letters always generated as both `.md` and `.pdf`.
- Cover letter sign-off comes from `memory.md`.

### Progress Tracking

- `tracker.md` is the central source of truth for all application status.
- Never auto-update tracker status. Ask the user before marking steps complete.

---

## Workflow

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
                   │  Confirms mode (Quick/Deep)   │
                   └──────────────┬───────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
     ┌─────────────────────┐         ┌─────────────────────────┐
     │   Decoded JD         │         │   Resume Scorer (pre)   │
     │  • Explicit reqs     │         │   Optional              │
     │  • Implicit expects  │         └────────────┬────────────┘
     │  • Confidence tags   │                      │
     └─────────┬───────────┘                      │
               └───────────────┬──────────────────┘
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
                └──────────────┬───────────────┘
                               ▼
                ┌──────────────────────────────┐
                │     Why This Company          │
                │  Speaking points (always)     │
                │  Cover letter (optional)      │
                └──────────────┬───────────────┘
                               ▼
                ┌──────────────────────────────┐
                │     Portfolio Coach           │
                │     (Optional)                │
                └──────────────┬───────────────┘
                               ▼
                ┌──────────────────────────────┐
                │     Networking Intros         │
                │     (Optional)                │
                └──────────────┬───────────────┘
                               ▼
                ┌──────────────────────────────┐
                │     Interview Prep PWA        │
                │     (Optional)                │
                └──────────────┬───────────────┘
                               ▼
                      ┌────────────────────┐
                      │   WRAP-UP          │
                      │   Update tracker   │
                      └────────────────────┘
```

The orchestrator handles routing. The user can also invoke any skill standalone by saying e.g. "run resume-scorer on the Acme PM resume."

---

## Key Principles

- **No fabrication** — all company claims sourced and cited
- **Human-in-the-loop** — nothing auto-generated without approval
- **Specific over vague** — metrics, tools, outcomes in every bullet
- **Plug-and-play** — skill logic separated from user data so the project is forkable
- **Doc freshness** — propose updates at end of every session

---

## Doc Freshness Protocol

At the end of every session:

1. Audit which files changed during the session.
2. Surface a dual-layer summary: a short skim list plus detailed changes.
3. The user approves or rejects each proposed update. Never auto-apply.
4. Update `Last updated:` lines on modified files.

---

## Privacy

- `memory.md` and the personal-data folders (`base-resumes/`, `research/`, `resumes/`, etc.) are excluded from git via `.gitignore`.
- If the user wants version control, recommend a **private** GitHub repo. Audit before pushing anywhere public.
- This project never auto-submits applications and never sends data anywhere — Claude only generates files locally.
