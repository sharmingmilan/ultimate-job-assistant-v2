# SPEC.md — Ultimate Job Assistant

**Status:** APPROVED — execution in progress (Phase 0 → 6)
**Author:** Claude (Cowork mode) + Milan
**Last updated:** 2026-05-02

This spec is the single source of truth. It documents what we're building, why, what is deliberately out of scope, and how we execute with checkpoints. Read this first; all other docs derive from it.

---

## 1. Goal

Build **Ultimate Job Assistant** — a polished personal job-application toolkit derived from `Job Assist`, enhanced with a new generic **`interview-prep`** skill that produces a deployable single-file PWA per application, modeled on the proven Netflix Interview Prep build.

Single user (Milan). Polished, version-controlled, CI/CD-checked. No backend, no auth, no database. Future SaaS pivot path documented separately in `ROADMAP.md` so the option stays open.

---

## 2. What this project is and is not

### Is

- A copy of the existing `Job Assist` workflow (orchestrator + 7 skills) preserved intact
- Plus one new skill: `interview-prep` that generates a Netflix-style study PWA for any role at any company
- Wired into the orchestrator as optional **Step 9.5** between Networking and Wrap-up
- Tracked in git with a CI workflow that validates artifacts on every change
- Documented for resuming across sessions (CLAUDE.md, SESSION_LOG.md, ROADMAP.md)

### Is NOT (in this build)

- Multi-user SaaS — see `ROADMAP.md` for the pivot path
- A backend, database, auth system, or payment integration
- A hosted-by-default product — generated PWAs are zip-droppable to Netlify or Vercel; hosting is the user's choice
- A web UI for the other Job Assist skills — those continue to run through Claude in chat
- A full code-execution environment for SQL — the editor is for thinking and self-check, not running queries (matches Netflix project's deliberate scoping)

---

## 3. User and context assumptions

- **Primary user:** Milan, applying to multiple roles per month
- **Devices:** iPhone (primary study device) + laptop (authoring device)
- **Time horizon per application:** ~1 week of prep
- **Inputs available:** decoded JD, company research file, score reports, base resume — all live in the existing Job Assist folder structure
- **Trust constraint:** No fabricated information. Every reported real-world interview question must cite a source (Glassdoor, Blind, Levels.fyi, etc.). Worked examples may use synthetic data, but only domain vocabulary and patterns extracted from research files.

---

## 4. Architecture

### 4.1 Project layout

```
~/Documents/Documents - Milan's MacBook Pro (Personal)/Claude/
└── Ultimate Job Assistant/
    ├── CLAUDE.md                              ← updated routing + status
    ├── SPEC.md                                ← this file (canonical)
    ├── ROADMAP.md                             ← future enhancements (SaaS path)
    ├── DESIGN_DOC.md                          ← carried over, updated
    ├── SESSION_LOG.md                         ← carried over, appended
    ├── memory.md                              ← carried over (user preferences)
    ├── tracker.md                             ← carried over, schema extended
    ├── README.md                              ← public-facing entry doc
    ├── .gitignore                             ← carried over, expanded
    ├── .github/
    │   └── workflows/
    │       └── ci.yml                         ← lint + Playwright smoke
    │
    ├── skills/                                ← carried over
    │   ├── orchestrator/                      ← updated (Step 9.5 added)
    │   ├── decoded-jd/
    │   ├── resume-targeter/
    │   ├── resume-scorer/
    │   ├── why-this-company/
    │   ├── portfolio-coach/
    │   ├── networking-intros/
    │   └── interview-prep/                    ← NEW
    │       ├── SKILL.md
    │       ├── template/
    │       │   ├── index.html.template
    │       │   ├── app.jsx.template
    │       │   ├── manifest.json
    │       │   ├── sw.js
    │       │   ├── icon-192.png               ← single neutral app icon
    │       │   └── icon-512.png
    │       ├── content-schema.json
    │       ├── references/
    │       │   ├── netflix-example/
    │       │   ├── pedagogy.md
    │       │   └── source-attribution-rules.md
    │       └── evals/
    │           └── netflix-regression.md
    │
    ├── references/                            ← carried over
    ├── base-resumes/                          ← carried over
    ├── research/                              ← carried over
    ├── decoded-jds/                           ← carried over
    ├── resumes/, scores/, speaking-points/, cover-letters/  ← carried over
    ├── interview-prep/                        ← carried over + new subfolder pattern
    │   ├── (existing PDFs preserved)
    │   └── [company]-[role]-[YYYY-MM]-pwa/    ← per-application PWA outputs
    ├── portfolio/, networking/, archive/      ← carried over
    └── applications/                          ← carried over
```

### 4.2 Output naming convention (extended)

Job Assist's `[company]-[role-slug]-[YYYY-MM].[ext]` is preserved. New addition for the PWA output folder:

```
interview-prep/[company]-[role-slug]-[YYYY-MM]-pwa/
├── index.html                                 ← deployable single file (~250-350 KB)
├── app.jsx                                    ← unminified source for reference
├── content.json                               ← topic data (separable for re-use)
├── manifest.json
├── sw.js
├── icon-192.png, icon-512.png
└── README.md                                  ← user-facing deployment notes
```

A user drags this folder onto Netlify Drop and gets a public URL in ~30 seconds. Cost: $0.

### 4.3 Content separation

Netflix project hard-coded content into `app.jsx`. The new template separates concerns:

```
content.json    ← all problems, topics, walkthroughs, real-questions tab data
app.jsx         ← rendering logic only (reads content.json at build time)
```

Future SaaS can swap content.json from a CMS or DB without rewriting React. Evals are easier: snapshot, diff, regenerate the JSON.

---

## 5. The `interview-prep` skill — full specification

### 5.1 Skill identity

```yaml
name: interview-prep
description: Research-driven interview prep skill that builds a deployable
  single-file study PWA tailored to a specific role. Pulls from decoded-jds/,
  research/, scores/, and web sources (Glassdoor/Blind/Levels.fyi). Produces
  a 3-phase study site (worked-example -> faded-scaffold -> free-recall) plus
  a "Real Qs" tab with sourced reported interview questions. Use when the
  user wants to prepare for a specific company's technical or case-study
  interview rounds.
```

### 5.2 Workflow — six phases (A through F)

**Phase A — Inputs.** Read `decoded-jds/[convention].md`, `research/[company].md`, `scores/[convention]-after.md`, `memory.md`. If any are missing, prompt user (or skip if optional).

**Phase B — Format inference.** From decoded JD + research, identify interview format:
- Technical screen type (SQL, coding, system-design, take-home, behavioral, case study)
- Expected duration and platform (CoderPad, HackerRank, Zoom whiteboard, etc.)
- Topic areas surfaced in JD
- Domain vocabulary the interviewer will use

Output: `interview-prep/[convention]-format.md`.

**Phase C — Topic synthesis.** Generate topic list ranked by expected interview frequency. Cite source per topic. Use 7–12 topics for technical screens, 4–6 for behavioral/case rounds.

Output: appended to `[convention]-format.md`.

**Phase D — Content authoring.** For every topic, generate:
- 3 worked examples (easy, medium, hard) with full solution + 6–10-bullet walkthrough
- 3 faded scaffolds (same problems, blanks at error-prone tokens)
- 3 retrieval problems (new prompts, no scaffold, with `selfExplain` seed + `explanation`)

Synthetic data is allowed; fake interview questions are not. The "Real Qs" tab is sourced-only.

Output: `interview-prep/[convention]-content.json`.

**Phase E — Real questions tab.** Search the web for reported interview questions at this company. Required attribution per item:
```json
{
  "id": "...",
  "category": "SQL | Python | System Design | ...",
  "title": "...",
  "prompt": "...",
  "concepts": ["..."],
  "difficulty": "easy | medium | hard",
  "source": "Glassdoor (2025-08, anonymous senior DA)",
  "source_url": "https://...",
  "solution": "...",
  "hint": "...",
  "note": "..."
}
```

If a search returns nothing credible, the tab is omitted with a note in the README. Never invent questions.

**Phase F — Build + ship.** Inject content.json into the template, produce `index.html`, run smoke test (Playwright headless), output deployable folder, write user-facing README, log to `tracker.md`.

### 5.3 Content authoring rules

- Every prompt states the mechanical ask AND the business motivation
- Every walk bullet explains a *choice*, not just code
- Faded blanks target error-prone tokens (join type, null operator, window choice, threshold)
- Retrieval problems must be solvable without the worked example visible
- All synthetic data is internally consistent across panels
- All claims about a company's actual interview format must cite a source

### 5.4 Pedagogy (carried over with citations)

| Principle | Source | Where it appears |
|---|---|---|
| Worked examples | Sweller & Cooper (1985); Renkl (2014) | "Came" phase |
| Fading | Atkinson et al. (2003) | "Saw" phase |
| Retrieval | Roediger & Karpicke (2006) | "Conquered" phase |
| Interleaving | Rohrer (2012) | Interleave mode |
| Spacing | Cepeda et al. (2006) | Flag-and-cooldown review |
| Dual coding | Paivio (1971); Mayer (2009) | Schema panels |
| Elaboration | Chi et al. (1994) | Self-explain prompts |

Citations render in the PWA footer.

### 5.5 Generic across formats

| Round type | Topic example | Worked-example mode | Editor type |
|---|---|---|---|
| SQL technical | "Window functions" | SQL solution + walkthrough | SQL editor with syntax highlight |
| Python/Pandas | "groupby + merge" | Python solution + walkthrough | Python editor (same architecture) |
| System design | "Design a feed ranker" | Reference architecture + tradeoff bullets | Plaintext notes editor |
| Behavioral | "Conflict with PM" | STAR-formatted answer + analysis | Plaintext notes editor |
| Case study | "Diagnose a metric drop" | Framework walk + computed answer | Plaintext notes editor |

Editor parameterized by `{ mode: 'sql' | 'python' | 'plaintext' }`.

---

## 6. PWA template — technical spec

### 6.1 Stack

- React 18, Tailwind, Babel-standalone — all via jsDelivr CDN
- Service worker for offline caching
- `localStorage` for progress persistence
- No build step on the host machine

Rationale: non-engineer user, ~1 week prep horizon, must survive a CDN failure (file can be opened locally as a fallback).

### 6.2 Editor component

- Transparent `<textarea>` over a syntax-colored `<pre>`
- Tab = 2 spaces; Shift+Tab unindents
- Auto-indent preserves prior-line whitespace
- Persistence key: `ujassist_q_{appId}_{topicId}_{difficulty}`
- Tokenizer per language (SQL, Python, plaintext = no highlight)

### 6.3 Bundle constraints

- Single `index.html` ≤ 400 KB (Netflix shipped 344 KB)
- All third-party JS via CDN, never inlined
- Service worker caches CDN deps after first load → fully offline

### 6.4 Acceptance criteria

A built PWA passes when:

1. All topics render Came/Saw/Conquered phases with the correct number of problems
2. Editor accepts input, persists to localStorage, applies syntax highlighting
3. Headless Playwright run reports zero `pageerror` events
4. Bundle is brace-balanced (programmatic check) and ≤ 400 KB
5. Manifest is valid; service worker registers without error
6. Real-Qs tab either renders sourced items or shows the explicit "no sourced questions found" state
7. PWA installs to iOS home screen and loads offline after first load (manual)

---

## 7. Workflow integration — orchestrator Step 9.5

```
Step 1:    Setup & Folder Creation         [Required]
Step 2:    Decoded JD                       [Required]
Step 3:    Resume Score (before)            [Optional]
Step 4:    Resume Targeter                  [Required]
Step 5:    Resume Score (after)             [Auto if Step 3]
Step 6:    Why This Company                 [Required]
Step 7:    Cover Letter                     [Optional]
Step 8:    Portfolio Project                [Optional]
Step 9:    Networking & Warm Intros         [Optional]
Step 9.5:  Interview Prep PWA               [Optional — NEW]
Step 10:   Wrap-up & Doc Freshness          [Required]
```

Standalone invocation also supported.

---

## 8. Git + CI/CD

### 8.1 Repo

- `git init` at the project root
- **Visibility: private** for v0.1.0. Path to public after first real successful run, but Claude must explicitly ask before flipping visibility
- `.gitignore` excludes: `.DS_Store`, personal data folders (`base-resumes/`, `research/`, `resumes/`, `scores/`, `speaking-points/`, `cover-letters/`, `interview-prep/*-pwa/`, `applications/`, `archive/`), `.env*`
- Skill code, templates, generic references are tracked

### 8.2 GitHub Actions CI

`.github/workflows/ci.yml` runs on push and PR:

1. Checkout
2. Validate `skills/*/SKILL.md` frontmatter
3. JSON-lint `skills/interview-prep/content-schema.json`
4. Render template with sample content into temp `index.html`
5. Run Playwright headless smoke test
6. Brace-balance check on rendered JSX
7. Markdown lint (formatting rules)

### 8.3 CD

Manual for v0.1.0. Skill outputs deployable folder; user uses Netlify Drop or `netlify deploy --prod --dir=...`.

Future: tagged-release auto-deploy in ROADMAP.md.

---

## 9. Self-audit checkpoint protocol

After every phase, Claude runs a structured self-check:

```
Checkpoint [Phase X]
✅ <criterion 1>
✅ <criterion 2>
⚠️  <criterion 3 — note + recommended action>
❌ <criterion 4 — what to do>

Diff from prior state:
+ <new file>
~ <modified file>
- <removed file>
```

**Cadence (per Milan's decision):** Proceed automatically when self-audit is fully green. Stop and surface for approval on any ⚠️ or ❌.

For complex phases, Claude may delegate verification to a sub-agent for an independent read.

---

## 10. Project-level acceptance criteria

The project is "v0.1.0 ready" when:

1. `~/Claude/Ultimate Job Assistant/` exists with the layout in §4.1
2. All existing Job Assist skills work unchanged
3. The new `interview-prep` skill produces a valid PWA against the Netflix decoded JD as a regression test
4. Regression PWA matches Netflix structural fidelity (11 topics × 3 phases × 3 difficulties + Real Qs tab)
5. Private git repo initialized; CI green; baseline tag `v0.1.0` placed at the end of Phase 7
6. README.md explains the project to a stranger; CLAUDE.md explains it to future Claude; ONBOARDING.md walks a new public user through setup
7. ROADMAP.md captures the SaaS pivot path
8. `tracker.md` schema extended with an `interview_prep_pwa` column
9. **Public companion repo** (`ultimate-job-assistant-public`) exists, contains only sanitized files (PII scanner clean), and includes the website source
10. **Public website** is live on GitHub Pages: landing page + multi-page ONBOARDING docs, builds on every push, no broken links

---

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Web research returns thin / unverifiable interview reports for niche roles | Honest "no sourced questions found" tab. Documented in skill spec. |
| PWA bundle exceeds 400 KB as content scales | content.json externalized; verified at CI |
| Regression test diverges from Netflix output | Snapshot structure, not bytes |
| iOS Safari clears localStorage after 7 days inactive | Documented in PWA's user-facing README |
| User wants to share PWAs with others | Each PWA is already standalone; SaaS multi-user is in ROADMAP |
| Future SaaS pivot blocked by hardcoded assumptions | Content separated at content.json layer; documented seams |

---

## 12. Future enhancements (preview — full version in ROADMAP.md)

- SaaS pivot (Clerk auth + Supabase DB + serverless wrap of skills + Stripe billing)
- Browser-driven Job Assist skills
- Server-side or DuckDB-Wasm code execution
- SM-2 / Anki-fidelity SRS
- Cross-application analytics

---

## 13. Decisions (confirmed by Milan, 2026-05-02; revised same day)

1. **Repo strategy — two-tier, FINAL form (2026-05-02 evening revision):**
   - **Private canonical repo** (`ultimate-job-assistant`) holds the canonical project including any artifacts that contain personal data (e.g., the unredacted resume fixture preserved in baseline commit `49bc5be`). Never made public.
   - **Sanitized deploy-source repo** (`ultimate-job-assistant-public`) is **also private**. Despite the name, this repo is no longer publicly browsable on GitHub. It exists solely as a sanitized mirror that a hosting provider (Netlify) reads via OAuth to serve the website. The "public" in its name is historical — it carries the public-facing/sanitized state, not public visibility.
   - **Public-facing surface** is the website only. The website exposes `/downloads/ultimate-job-assistant.zip` for anyone with the site URL — no GitHub account required to download. The zip is the canonical public artifact.
   - **Why the change.** Earlier (morning of 2026-05-02) the plan was: keep the deploy-source repo public so GitHub Pages on the free tier could serve the site. Milan revised this in the evening: even with `noindex` and `robots.txt`, a public GitHub repo is still searchable on GitHub itself. Moving hosting to Netlify lets both repos go private while keeping the site live. Cost stays $0/mo (Netlify free tier reads private GitHub repos with OAuth).
2. **Hosting:** **Netlify** (free tier), reading the private deploy-source repo via GitHub OAuth. Replaces GitHub Pages. URL goes from `sharmingmilan.github.io/...` to `*.netlify.app` (or to a custom domain when purchased).
3. **Custom domain:** **buy one, ~$12/yr.** Likely candidates: `ujassist.app` or `ultimatejobassistant.com` via Cloudflare or Namecheap. Milan buys the domain; Claude wires the DNS to Netlify.
4. **Distribution model:** **zip download from the website.** `scripts/sync_to_public.py` regenerates `website/downloads/ultimate-job-assistant.zip` on every sync. The simplified landing page (`website/index.html`) has one primary CTA — "Download the latest" — and a HEAD-fetch JS snippet that displays the zip's size and last-modified date.
5. **Sync trigger:** **GitHub Action on the private canonical repo.** Triggers on every push to `main`, runs `sync_to_public.py` with the STRICT PII scanner gate, and pushes to the deploy-source repo. Requires a Personal Access Token stored as repo secret `PUBLIC_REPO_TOKEN` (scope: `repo`). Milan creates the PAT manually.
6. **Iconography:** one **generic neutral icon for the Ultimate Job Assistant app**. Reused for every PWA generated; not regenerated per application.
7. **Existing `interview-prep/` PDFs:** keep in place; no migration. New `[convention]-pwa/` subfolders coexist.
8. **Approval cadence:** proceed automatically when self-audit is fully green. Stop and surface on any ⚠️ or ❌. Repeated-but-already-approved warnings (e.g., expected SOFT PII hits in private repos) count as informational, not blocking.
9. **Public-facing base-resume template:** the project ships a `references/templates/base-resume-template.docx` with the same section structure as Milan's real resume (PROFESSIONAL SUMMARY, PROFESSIONAL EXPERIENCE, SKILLS, EDUCATION) but every value replaced with `[BRACKETED]` placeholder text. Generated by `scripts/generate_template_resume.py`. Anyone who downloads the project zip gets a starter resume to fill in. The template syncs to the public companion repo via the existing allowlist (`references/templates/`) and rides through the website's zip download in v0.1.1.

### 13.A Superseded decisions (history)

The following items represent prior thinking that has been replaced; they are kept here so the historical context is recoverable.

| Date | Earlier decision | Replaced by |
|---|---|---|
| 2026-05-02 morning | "Flip private → public after first successful run" | The two-tier strategy in §13.1 (private + sanitized companion). |
| 2026-05-02 morning | "Public companion repo can be public on GitHub; site lives on GitHub Pages with `noindex`" | §13.1: both repos private; site moves to Netlify. |
| 2026-05-02 afternoon | "Stack for the website is plain static HTML + Tailwind CDN, served via GitHub Pages" | Stack stays the same (still plain HTML + Tailwind CDN). Hosting moves to Netlify. |
| 2026-05-02 afternoon | "Custom domain skipped for v0.1.0" | §13.3: custom domain confirmed as part of the v0.1.1 path. |

### 13.1 Public artifact strategy (decided 2026-05-02)

**Decision:** Option **(b) Public companion repo** — chosen over single-doc and branch-based options.

A separate GitHub repo, `ultimate-job-assistant-public`, holds:

- All skill code from `skills/*/` (generic, no PII)
- Generic templates from `references/templates/`, `references/scripts/`, `references/patterns/`
- `ONBOARDING.md` (sanitized version, copied or symlinked from private repo)
- A `.github/workflows/pages.yml` that builds the website on push
- The website source (landing page + docs)
- A `memory.md.template` (blanks where personal info goes)
- A blank skeleton of every personal-data folder (`.gitkeep` only) so cloners get the right structure

**Sync model:** the private repo is the working copy. A small script (`scripts/sync-to-public.sh`) copies an allowlist of files into a sibling clone of the public repo, runs a PII scanner over the diff, and stops if any sensitive string is found. The user reviews the diff and pushes manually. No automatic sync, ever — that's how PII leaks happen.

**Why not (a) single doc:** strangers can't actually use the toolkit from a single doc. They need the skill code.
**Why not (c) branch-based:** one wrong `git push` from the wrong branch leaks everything. Two separate repos make that mistake structurally impossible.

### 13.2 Public website (decided 2026-05-02)

**Shape:** **C — landing page + docs site.** Polished product-style landing page (hero, features, screenshots, "Get started" CTA) plus the ONBOARDING walkthrough rendered as a multi-page docs site.

**Hosting:** GitHub Pages, built and deployed on push to the companion repo via GitHub Actions. Default URL: `https://<username>.github.io/ultimate-job-assistant-public/`. No custom domain in v0.1.0.

**Timing:** part of **v0.1.0** as **Phase 7**, after the regression test (Phase 5) and ROADMAP/audit (Phase 6) but before the v0.1.0 tag.

**Stack:** during Phase 7 design (2026-05-02), flipped from Astro to **plain static HTML + Tailwind CDN** for these reasons:

| Option | Decision rationale |
|---|---|
| **Plain static HTML + Tailwind CDN** ✅ chosen | Mirrors the interview-prep PWA stack. Zero build step. Same "no npm install" philosophy. GitHub Pages serves directly with `actions/upload-pages-artifact` and `actions/deploy-pages`, no Node setup needed. ~1 hour to build vs 3+ for Astro. |
| Astro | Was the original default. Has nicer DX once set up but introduces a Node build pipeline that conflicts with the project's stated no-build philosophy. |
| MkDocs Material | Strong docs theme, but Python build, less landing-page-friendly. |

The decision was explicitly anticipated in the original spec ("decision can flip during Phase 7 design") and is recorded here.

**Live demo PWA on the website:** explicitly **deferred to v0.1.1**. The v0.1.0 website links to the GitHub repo and explains how to run the toolkit; it does not yet host an interactive demo. Adding the demo PWA was option D in the scope question and was deferred to keep v0.1.0 finishable.

---

## 14. Execution plan

### v0.1.0 (shipped — committed and tagged 2026-05-02)

| Phase | Subject | Deliverable | Status |
|---|---|---|---|
| 0 | Bootstrap project | New project folder, copied content, git init, root docs | ✅ commit `49bc5be` |
| 1 | Author SKILL.md | `skills/interview-prep/SKILL.md` (full pedagogy + workflow A–F) | ✅ commit `eb0d7ac` |
| 2 | Build PWA template | `template/`, `content-schema.json`, smoke test green | ✅ commit `eb0d7ac` |
| 3 | Wire orchestrator | Updated `orchestrator/SKILL.md`, `CLAUDE.md`, `tracker.md` | ✅ commit `eb0d7ac` |
| 4 | Git + CI/CD | `.github/workflows/ci.yml`, baseline commit, README.md | ✅ commit `eb0d7ac` |
| 5 | Regression test | Run skill against Netflix JD; structural diff | ✅ commit `d67c9d0` |
| 6 | ROADMAP + audit | `ROADMAP.md`, consistency audit | ✅ commit `d67c9d0` |
| 7 | Companion repo + website | `ultimate-job-assistant-public` repo, sync script, static landing+docs, GitHub Pages deploy | ✅ commit `3682c8a`, tagged `v0.1.0` |
| 7.5 | noindex + robots.txt + landing simplification | site stays live, search-invisible | ✅ commit `f02d9d4` (private), `bd975b2` (public) |

### v0.1.1 (next — fresh-session work)

| Phase | Subject | Deliverable | Acceptance |
|---|---|---|---|
| 8 | Add zip generation to `sync_to_public.py` | `website/downloads/ultimate-job-assistant.zip` is regenerated on every sync; `.gitkeep` keeps the dir | Sample sync produces a fresh zip; landing page HEAD-fetch displays size + date |
| 9 | Migrate hosting to Netlify | Netlify connected to deploy-source repo via OAuth; site live at `*.netlify.app`; GitHub Pages disabled | Netlify URL responds 200; download works |
| 10 | Make deploy-source repo private | `ultimate-job-assistant-public` flipped to `private: true` via API | Netlify still serves (OAuth stays valid) |
| 11 | Auto-sync GitHub Action | `.github/workflows/auto-sync-to-public.yml` on the canonical private repo, gated on STRICT PII scan | Push to canonical → public is auto-updated within ~30 s |
| 12 | Custom domain | Milan buys; Claude wires DNS to Netlify | HTTPS provisioned, custom URL responds 200 |
| (tag) | Tag `v0.1.1` | Tag after phase 12 ships | All §10 acceptance criteria, plus zip-distribution criteria pass |

---

*End of SPEC.md.*
