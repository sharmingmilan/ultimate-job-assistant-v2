# Job Application Skill Suite — Design Document

## Overview

A modular, plug-and-play suite of skills that chains together as an agentic workflow to help job seekers build targeted, research-backed application materials. Designed to be forkable — skill logic is separated from user data so anyone can customize it to their own background.

---

## Architecture Principles

- **Modular**: Each skill is standalone and can run independently or as part of the orchestrated workflow
- **Human-in-the-loop**: Every stage requires user approval before proceeding. No auto-generated outputs without review.
- **No fabrication**: All company/role claims must come from verified, credible web research with source citations
- **Specific over vague**: Bullet points and outputs must include concrete details — numbers, tools, outcomes, scope
- **Plug-and-play**: Clean separation between skill logic and user data. Someone can fork the repo, clear out user data, and start fresh.
- **Adjustable**: Any skill's scope, workflow order, or behavior can be revised as needs evolve

---

## Research Brief Format

All research briefs follow a two-section structure and live at `research/[company].md`, shared across all roles at that company.

### Section 1: Company Research (reusable across roles)

Contains: Company Overview, Company Culture & Values (Core Cultural Signals + Watch Items), Interview Process & What They Look For (Process + What They Screen For), Sources. This section is written once per company and reused across all role applications at that company.

### Section 2: Role-Specific Research (dated subsections, appendable)

Contains dated subsections in the format `### [Role Title] (YYYY-MM)` with: Role & Team Context, Key Themes for Resume Targeting, and optionally Gaps & Honest Limitations. When applying to a second role at the same company, a new dated subsection is appended without overwriting previous role sections.

Blank template: `references/templates/research-brief.md`

---

## Skills

### Skill 1: Resume Targeter

**Purpose**: Research a company's culture, values, and interview process deeply, then conduct adaptive Q&A with the user to craft tailored resume bullet points and generate a final DOCX + PDF resume.

**Key Design Decisions**:
- Five-phase workflow: Gather Inputs → Deep Company Research → Adaptive Q&A → Bullet Generation & Change Review → Final Resume Generation
- Research covers three dimensions: culture & values, interview process, and role-specific context. All claims sourced and cited.
- Adaptive Q&A runs in rounds: Round 1 maps core experience, Round 2 probes values alignment, subsequent rounds fill gaps. Stops when every major requirement and value has a supporting story.
- Bullets are proposed in REPLACE/ADD/KEEP format. User approves each change before final generation.
- Final output preserves the user's original resume formatting and structure (table-based company headers, bullet styles, section layout).
- 8 mandatory formatting rules enforced on all outputs (no dashes as punctuation, contact line on one line, bullet spacing, section spacing, Skills formatting, layout preservation, no fabrication). Rules documented in memory.md and SKILL.md.
- When decoded-jd has already run, resume-targeter reads it as a foundation for Phase 2 research to avoid duplicate JD parsing.

### Skill 2: Decoded JD

**Purpose**: Analyze the explicit and implicit expectations of a job posting using deep company research.

**Key Design Decisions**:
- Output: "Decoded JD" document — explicit requirements side by side with implicit expectations derived from culture research
- Confidence tagging on all findings (strong evidence vs. informed inference)
- Mode toggle: Quick Mode (infer from context, confirm) vs. Deep Mode (full interrogation with gap-filling questions)
- Mode is inferred from context and confirmed with a quick check — no formal toggle menu
- When research is thin (e.g., small startups), skill is transparent about confidence levels AND asks user to fill gaps
- Standalone use case: night-before interview refresh, deciding whether to apply
- Called by orchestrator during resume-targeter workflow

### Skill 3: Networking & Warm Intros (Narrow Scope)

**Purpose**: Find relevant contacts at the target company and draft a personalized first outreach message.

**Key Design Decisions**:
- Narrow scope for v1: find contacts + draft first message only
- User is less experienced with outreach — skill should be coaching-oriented, not just template-generating
- **Future enhancements**: Full networking coaching arc — timing outreach relative to application, follow-up cadence, handling responses, different approaches for different connection levels (2nd-degree LinkedIn vs. cold message vs. re-engaging old contact)

### Skill 4: Resume-Job Match Scorer

**Purpose**: Score how well a resume matches a job description with a transparent, blended percentage breakdown.

**Key Design Decisions**:
- **Requires decoded-jd** — the implicit expectations and values alignment layer depend on a decoded JD. If it hasn't run, scorer stops and offers to run it first.
- Blended score: keyword coverage (30%) + qualification match (40%) + values alignment (30%) (from Decoded JD research)
- Transparent breakdown — like a report card showing exactly where you're strong and where gaps are
- Score is purely informational — user always makes the decision
- **Unified suggestions**: Scorer is the single place where all resume improvement suggestions live — including narrative insights flagged by why-this-company. This avoids multiple skills each proposing their own edits.
- **Opt-in flow**:
  - Skill explicitly asks at the start: "Want me to score your resume against this JD first?"
  - If YES → scores before AND after automatically (before/after comparison)
  - If NO → skips before score, asks again at the end: "Want me to score the final resume?"
- Post-score step: suggests specific corrections to the resume AND recommends supplementary materials (cover letter, portfolio, etc.) to close remaining gaps
- Creates natural handoffs to other skills in the workflow

### Skill 5: "Why This Company" Narrative

**Purpose**: Connect dots between the user's career arc and the company's mission. Produce speaking points and optionally a cover letter.

**Key Design Decisions**:
- Outputs:
  - Speaking points cheat sheet (always generated) — 5-7 bullet points, neutral professional tone, designed for quick glance before calls
  - Cover letter (optional — skill asks "Want me to draft a cover letter from these points?" every time)
- User doesn't want a script — wants a cheat sheet to glance at and then talk candidly
- Neutral, professional tone — user adapts to their own voice
- **Narrative insights handoff**: After generating narrative outputs, skill reviews them against the resume and flags framing-level insights (e.g., "the resume emphasizes operational reliability but the narrative is about innovation — these should align"). These are saved in the speaking points file and handed off to resume-scorer, which incorporates them into its unified suggestions. The skill does NOT suggest specific resume edits or loop back to resume-targeter directly.
- Runs after resume-targeter is finished and scored (Option B — modular)

### Skill 6: Portfolio Project Coach

**Purpose**: Recommend, scope, source, and walk the user through building a portfolio piece relevant to the target role.

**Key Design Decisions**:
- Skill recommends which project type fits the role best (GitHub repo, Tableau dashboard, written analysis, AI project)
- Step-by-step walkthrough with check-ins at each stage: "Want me to walk you through this, or can you take it from here?"
- Project structure:
  1. Project brief (what, why, what it demonstrates)
  2. Dataset selection with backup option
  3. Analysis plan
  4. Execution (broken into chunks)
  5. Packaging (README, dashboard layout, report structure)
  6. Review against what target company would care about
- **Data sourcing — Option C (hybrid)**:
  - Curated list of free data sources baked into skill (Makeover Monday, Kaggle, data.gov, etc.), organized by domain
  - Live web search for more specific/current datasets
  - User confirms live-search finds before they get added to curated list
  - Curated list grows and improves over time with human-verified additions
- **Real-world examples**: Skill surfaces existing portfolio projects (GitHub repos, Tableau Public pages, analyses, AI projects) as reference/inspiration
- **LinkedIn post**: Optional final step — "Want me to draft a LinkedIn post to showcase this project?"
  - Offers two framings: project-focused (evergreen) and job-search-transparent (attracts recruiters)
  - User picks which framing fits
- Not for every application — more of a "dream company" investment

### Skill 7: Orchestrator

**Purpose**: Chain all skills together into a guided application workflow, managing folder creation, skill handoffs, decision points, file routing, and progress tracking.

**Key Design Decisions**:
- Guided, not automatic. Drives the sequence but never runs a skill without user confirmation.
- Context-aware. Reads existing files to determine where a partially completed application left off.
- Graceful skipping. Any optional skill can be skipped without breaking the chain.
- Naming convention enforcement. Before any skill runs, the orchestrator sets context variables (`[company]`, `[role-slug]`, `[YYYY-MM]`) that derive all output filenames: `[company]-[role-slug]-[YYYY-MM].[ext]`. Verifies `research/[company].md` exists (or will be created during resume-targeter Phase 2).
- Single source of progress. The central `tracker.md` is the progress log, with one row per application and columns for each skill. Never auto-updated; orchestrator proposes updates for user approval.
- Default workflow order:
  1. Decoded JD (research phase)
  2. Resume-Targeter (core resume building with adaptive Q&A)
  3. Resume-Job Match Scorer (bookends the resume work — before/after if opted in)
  4. "Why This Company" Narrative (speaking points, optional cover letter, optional resume revision loop)
  5. Portfolio Project Coach (optional, for high-priority applications)
  6. Networking & Warm Intros (optional, loosely coupled)
  7. Interview Prep PWA (optional Step 9.5; new in UJA v0.1.0)
- Error handling: if a skill fails, announce the issue and offer retry, skip, or stop-and-resume-later.
- The orchestrator is a guide, not a gatekeeper. If the user wants to skip, reorder, or stop, respect that immediately.

### Skill 8: Interview Prep PWA (UJA v0.1.0)

**Purpose**: Convert the decoded JD plus company research into a deployable single-file Progressive Web App for one specific interview, using the worked-example → faded-scaffold → free-recall pedagogical loop modeled on the Netflix Interview Prep build.

**Key Design Decisions**:
- Six explicit phases (A through F) with checkpoint per phase (see `skills/interview-prep/SKILL.md`).
- Content separated from rendering at the `content.json` layer. The PWA template is generic and reusable; per-application runs only generate new content. This keeps the SaaS pivot path open (a future server can swap content from a database without rewriting the React).
- Hard rule: no fabricated interview questions. Every entry in the "Real Qs" tab cites a credible source (Glassdoor, Blind, Levels.fyi, official tech blog). Synthetic worked examples are allowed but must use vocabulary and patterns sourced from the company's real materials. Full source-attribution rules in `skills/interview-prep/references/source-attribution-rules.md`.
- Generic across formats. The editor component is parameterized by language: SQL, Python, plaintext (for system-design / behavioral / case-study rounds).
- Output is drag-and-drop deployable. Each run produces `interview-prep/[convention]-pwa/` containing a single `index.html` (~250-400 KB), a manifest, a service worker, the PWA shell icons, and a user-facing README. The user drags the folder onto Netlify Drop for a free public URL.
- Zero monthly cost. No backend, no auth, no database. Progress persists to `localStorage` per browser. iOS Safari clears localStorage after about 7 days inactive — documented as a known limitation rather than fixed.
- Pedagogical citations render in the PWA footer for transparency: Renkl, Sweller, Roediger & Karpicke, Rohrer, Cepeda, Paivio, Mayer, Chi. Full reference list in `skills/interview-prep/references/pedagogy.md`.
- Reference build: the original Netflix Interview Prep project lives at `skills/interview-prep/references/netflix-example/` for design provenance.
- Wired into the orchestrator as optional Step 9.5 (between Networking and Wrap-up); also runnable standalone.
- See `SPEC.md` §5–§6 for the higher-level rationale and acceptance criteria.

---

## Build Order

1. Resume-targeter — `skills/resume-targeter/SKILL.md` — Tested 4x (Netflix, Lumin, Disney, Waymo)
2. Decoded JD — `skills/decoded-jd/SKILL.md` — Tested 1x (Waymo lifecycle)
3. Resume-Job Match Scorer — `skills/resume-scorer/SKILL.md` — Tested 1x (Waymo before/after)
4. "Why This Company" Narrative — `skills/why-this-company/SKILL.md` — Tested 1x (Waymo speaking points + cover letter)
5. Portfolio Project Coach — `skills/portfolio-coach/SKILL.md` — Tested 1x (Waymo lifecycle)
6. Orchestrator — `skills/orchestrator/SKILL.md` — Tested 1x (Waymo Steps 1-10 complete)
7. Networking & Warm Intros — `skills/networking-intros/SKILL.md` — Tested 1x (Waymo lifecycle)
8. Interview Prep PWA — `skills/interview-prep/SKILL.md` — NEW in UJA v0.1.0 (Phase 5 regression test pending)

---

## File Locations

- All skill SKILL.md files: `Job Assist/skills/[skill-name]/SKILL.md`
- Portfolio coach curated datasets: `Job Assist/skills/portfolio-coach/references/curated-datasets.json`
- Resume-targeter evals: `Job Assist/skills/resume-targeter/evals/`
- This design doc: `Job Assist/DESIGN_DOC.md`

---

## Doc Freshness Protocol

All markdown files stay current through an end-of-session update process. Updates are always proposed, never auto-applied.

### Triggers
1. **Development sessions** (editing skills, orchestrator, architecture) → propose updates to skill docs, CLAUDE.md, design doc, tracker.md
2. **Workflow runs** (applying to a job) → propose updates to CLAUDE.md, tracker.md, curated-datasets.json, networking files

### Update Format
Dual-layer: a quick **summary** you can skim + **detailed changes** with exact file/line edits underneath if you want to verify.

### Rules
- Proposed, never auto-applied. User approves or rejects.
- Happens at end of session, not mid-workflow.
- Only files that actually changed. No touching current files.
- Never deletes content — only adds, modifies, or restructures.
- Each updated file gets a refreshed `Last updated:` line.

---

## Project Location

Target directory: `/Users/Milan/Documents/Claude/Job Assist/`

Follows output-type folder organization with convention-based routing. See `CLAUDE.md` for full folder structure, naming convention, and workflow diagram.

---

## Future Enhancements (Noted)

- **Job Hunt Dashboard** — serves two purposes: (1) **status tracker** with user-logged inputs per application (applied, interviewing, offer, rejected) and which optional materials were submitted (cover letter, portfolio, etc.), and (2) **navigation hub** with direct links to all application materials across output-type folders (resumes/, cover-letters/, speaking-points/, decoded-jds/, portfolio/, scores/) so the user never digs through folders. Dashboard surfaces trends and patterns to help focus effort. Note: `tracker.md` already provides basic status tracking; the dashboard would add visualization and linking on top. Input format, visualization, and specific metrics TBD.
- Full networking coaching arc (timing, follow-up, handling responses)
- Resume library management — skill learns your different resume versions by role type
- Shareable/synced curated dataset list across users
- Plug-and-play GitHub repo with clear setup instructions
- Skill description optimization for triggering accuracy
- **Golden reference template** — a visually verified "perfect" resume PDF to compare future generations against, catching visual regressions (spacing drift, font weight, line height) that formatting rules alone may miss
- **Multi-persona forkability** — generalize the toolkit so anyone can clone the repo and use it regardless of experience level or industry. Key work: (1) make `memory.md` a guided template with onboarding questions that build the user's profile from scratch, (2) adapt Q&A prompts in resume-targeter and why-this-company to calibrate to experience level (fresh grad with projects/coursework vs. 20-year veteran with executive stories), (3) adjust resume-scorer framing so expected "Gap" ratings for early-career users are encouraging rather than discouraging, (4) add role-type examples beyond data analytics (CSM, engineering, product, marketing, etc.) to portfolio-coach project recommendations. Target personas: recent college graduates, career changers, and professionals across industries and experience levels (0–99+ years).
- **Full product (app/website)** — package Job Assist as a standalone product accessible beyond the CLI/skill workflow. Two potential paths: (1) **web app** with user accounts, onboarding flow, file storage, and a guided UI that walks users through each skill step (hosted, shareable, no local setup required), or (2) **native/mobile app** published to App Store and/or Google Play for on-the-go application management. Either path requires: user authentication, cloud storage for resumes and application materials, a frontend that replaces the conversational Q&A with structured forms or chat UI, payment/subscription model (if monetized), and an API layer wrapping the skill logic. Scoping session needed to decide between web-first vs. native, free vs. freemium, and which skills to prioritize for the initial launch.

---

*Last updated: April 10, 2026*
*Status: All 7 skills drafted and tested. Orchestrator lifecycle tested through Steps 1-10 (Waymo, complete). Resume-targeter tested 4x (Netflix, Lumin, Disney, Waymo). Folder structure migrated to output-type organization (Phase 2 complete). Next: package as .skill file.*
