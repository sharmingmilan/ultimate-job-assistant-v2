# SESSION_LOG.md -- Job Assist
# Last updated: 2026-05-02 (added UJA Session 3 entry)

---

## How to Use This File

At the start of a new session, read this file first. It tells you where we left off, what's been decided, and what to do next. Then read CLAUDE.md for routing and DESIGN_DOC.md for skill specs if you need the full picture.

---

## Session 1: April 7, 2026

### What Happened

1. **Identified the project idea** from a Netflix Data Analyst job posting (Production Finance O&I, $150K-$230K). Milan wanted a skill that deeply researches a company, asks targeted Q&A questions, and builds a tailored resume.

2. **Expanded scope to a full skill suite** -- not just a resume-targeter, but a modular pipeline of 6 skills + an orchestrator. Discussed each skill in depth, identified flaws, clarified scope. All design decisions are in DESIGN_DOC.md.

3. **Defined 6 skills:**
   - **Decoded JD** -- analyzes explicit + implicit expectations from job postings. Confidence tagging. Quick/Deep mode inferred from context.
   - **Resume Targeter** -- core skill. Research, adaptive Q&A, tailored bullets, proposed changes, final DOCX + PDF.
   - **Resume-Job Match Scorer** -- blended percentage score with transparent breakdown. Opt-in at start; if yes, auto-scores at end for before/after. If no at start, asks again at end.
   - **Why This Company Narrative** -- connects career arc to company mission. Outputs speaking points (always) + cover letter (if opted in). Can fork back to revise resume if insights surface improvements.
   - **Portfolio Project Coach** -- recommends project type, walks through step-by-step with check-ins, sources datasets (curated list + live search, confirmed finds added to curated list), optionally drafts LinkedIn post (two framings: project-focused or job-search-transparent).
   - **Networking & Warm Intros** -- narrow v1: find contacts + draft first message. Future: full coaching arc.
   - **Orchestrator** -- chains skills in order, respects user choices at every decision point.

4. **Built folder structure** following Milan's three-layer architecture (CLAUDE.md, CONTEXT.md per workspace, Skills/scripts/references). Company-level folders with role subfolders inside applications/.

5. **Baked in a Doc Freshness Protocol** -- at end of every session (development or workflow run), propose markdown updates as dual-layer: quick summary + detailed changes. User approves or rejects. Never auto-applied.

6. **Drafted and tested the resume-targeter skill (test case 1: Netflix):**
   - Researched Netflix culture, values, interview process (Freedom & Responsibility, Dream Team, Keeper Test, core values: Judgment, Selflessness, Courage, Communication, Curiosity, Integrity, Inclusion)
   - Ran 2 rounds of adaptive Q&A with Milan. Key stories surfaced:
     - Nike studio scheduling optimizer (SQL joining 6+ datasets, Tableau output, daily standups)
     - Apple data integrity pushback (Spend FY/QTR mapping failure, drove upstream correction instead of hardcoding)
     - Apple weekly ETL ownership (4-7 hrs/week, 12-person team dependency, AI automations to compress time)
     - Apple self-directed AI initiative (org GitHub, standardized docs, semantic layer, biweekly training)
   - Generated tailored bullets, got feedback, revised (concise for resume, leave stories for interview)
   - Proposed changes in REPLACE/ADD/KEEP format
   - Generated final DOCX + PDF preserving original formatting
   - All outputs saved to applications/netflix/data-analyst-2026-04/

7. **Created evals.json with 3 test cases:**
   - Test 1: Netflix Data Analyst (completed -- live end-to-end)
   - Test 2: Lumin Digital Product Data Analyst (pending -- tests thin research)
   - Test 3: Disney Lead Data Analyst (pending -- tests recognizing prior experience)

8. **Future enhancements noted:**
   - Job Hunt Dashboard (status tracker + navigation hub with links to all materials, trend analysis)
   - Full networking coaching arc
   - Resume library management
   - Shareable curated dataset list
   - GitHub repo with setup instructions

### Milan's Preferences (important for all future sessions)

- **Resume style**: Concise bullets with metrics -- leave stories for the interview. "I glance at notes and talk candidly."
- **Tone**: Neutral, professional. Milan adapts to his own voice.
- **Mode selection**: Infer from context, confirm with a quick check. No formal toggle menus.
- **Multiple base resumes**: Has different versions for different role types (data analyst, data engineer, etc.)
- **Batch applies** but customizes per application.
- **LinkedIn posts**: Offer both framings (project-focused and job-search-transparent), let Milan pick.
- **Updates**: Always proposed, never auto-applied. Dual-layer format (summary + details).
- **Plug-and-play design principle**: Separate skill logic from user data so repo is forkable.

---

## Session 2: April 7, 2026

### What Happened

1. **Ran test case 2: Lumin Digital (Product Data Analyst, remote, $125K-$145K)**
   - Researched Lumin Digital: Series B fintech startup, ~300 employees, 100% remote, cloud-native digital banking platform for credit unions/banks
   - Research was appropriately thin given startup status: brief includes confidence tags ([HIGH]/[MED]/[LOW]) and explicit gaps section
   - Key culture signals: trust/boldness/transparency, servant leadership, 99% employee satisfaction, 4.6/5 Glassdoor
   - Interview process: 4 rounds (~3 weeks): recruiter, hiring manager + tech screen, peer panel, cross-team leads panel. Difficulty: 2.8/5
   - Ran 2 rounds of Q&A. New stories surfaced:
     - Wells Fargo self-service funnel: call center logs + SLA data in Redshift, mapped customer drop-off points, reduced help desk calls 20%, increased self-service completion 12%
     - Pinterest desk sensor cross-validation: reconciled occupancy vs. badge data, identified event-driven capacity spikes, built workplace dashboard
     - Apple KPI definition: defined procurement reporting parameters (all PRs vs. finalized/pending)
     - Disney regression + bundling: backfilled 2 years vendor data, regression showed IP bundling outperforms individual, shifted marketing strategy
     - Google Analytics: light use for web dev business (2020), honest/don't oversell
   - Milan confirmed resume philosophy: concise bullets with metrics, stories saved for interview. No callouts of bad company practices.
   - Generated tailored DOCX and research brief to applications/lumin-digital/product-data-analyst-2026-04/

2. **Test case 3 (Disney) not run** -- deferred to next session

---

## Session 3: April 7, 2026

### What Happened

1. **Identified fabricated content in base resume** -- "Freelance Data & Analytics Consultant | April 2025 - September 2025" was fabricated in a prior session and baked into the base resume, then carried into the Netflix output. Removed from both data-analyst-base.docx and the Netflix targeted resume (DOCX + PDF).

2. **New base resume uploaded** -- Milan_Sharma_Resume_2026.docx replaced the old base. Uses a table-based layout (company | date, title | location) with ListParagraph bullet style. No fabricated content.

3. **Regenerated Netflix and Lumin Digital resumes from new base:**
   - Reused existing research briefs and Q&A stories from memory.md (no fresh research or Q&A needed)

4. **Established resume formatting rules (8 rules):**
   - No dashes as punctuation
   - Contact line on one line (shorten URLs)
   - No rogue spacer paragraphs between bullets
   - One spacer line between company sections
   - One spacer line before SKILLS section
   - "Skills:" bold, skill list not bold
   - Preserve base resume table-based layout
   - No fabrication

5. **Saved formatting rules to memory.md, resume-targeter SKILL.md, and ARCHITECTURE.md**

### Key Correction: Nike Story Detail
- The Nike studio scheduling optimizer output is called the **Bay Watch Dashboard** in Tableau (name not used in bullet per Milan's preference, but documented here for reference)

---

## Session 4: April 8, 2026

### What Happened

1. **Completed test case 3: Disney Lead Data Analyst (Job ID 10146987)**
   - Team: Disney Entertainment & ESPN Product & Technology, New York, NY, $148K-$199K
   - Researched Disney culture, interview process (4 rounds, ~74 days, case study presentation)
   - Ran 3 rounds of Q&A (core experience, return-to-Disney narrative, bullet targeting)
   - All 8 formatting rules verified and passing

2. **Drafted all remaining skills** -- decoded-jd, resume-scorer, why-this-company, portfolio-coach, orchestrator, networking-intros. All 7 skills now have SKILL.md files.

3. **Added repeat-company research protocol to ARCHITECTURE.md**

---

## Session 5: April 8, 2026

### What Happened

1. **Ran full orchestrator lifecycle test: Waymo BI Analyst (Product Data Science, $125K-$157K)**
   - Completed Steps 1-7 of orchestrator pipeline:
     - Step 1: Decoded JD (Deep mode, 10 must-haves, 5 nice-to-haves, 7 implicit expectations)
     - Step 2: Research brief (company overview, culture, interview process, role context)
     - Step 3: Pre-score: 74% (Keyword 82%, Qualification 78%, Values 60%)
     - Step 4: Resume Targeter (9 bullet replacements + summary rewrite, 2 rounds Q&A)
     - Step 5: Post-score: 88% (+14 delta, Keyword 89%, Qualification 90%, Values 84%)
     - Step 6: Speaking points (7 points, .md + .pdf) + Why Waymo narrative
     - Step 7: Cover letter (.md + .pdf) with "Sincerely, Milan" signature
   - Steps 8-10 not started (portfolio, networking, wrap-up)

2. **New stories added to memory.md:**
   - Apple + Wells Fargo knowledge sharing and best practices (office hours, biweekly deep-dives)
   - Apple data integrity pushback expanded (non-technical team pressure, SME framing, pros/cons approach)
   - Apple KPI governance expanded (Confluence pages, Box folders data dictionary)
   - Disney digital asset expanded (proactive gap identification, COVID-era criticality, dimensional/relational modeling, Python-heavy)

3. **Doc consistency fixes:**
   - DESIGN_DOC.md: Added Resume Targeter as Skill 1, Orchestrator as Skill 7, renumbered all skills
   - ARCHITECTURE.md: Replaced all skill numbers with skill names in workflow diagram and folder structure (build order != workflow order, names avoid confusion)
   - CLAUDE.md: Routing table updated with both CONTEXT levels and research-brief references

4. **Formatting enforcement expanded:**
   - Fixed contact line GitHub URL (https://github.com/sharmingmilan to github.com/sharmingmilan)
   - Added mandatory verification step to resume-targeter SKILL.md Phase 5 (contact line, page count, dashes)
   - Added no-dashes rule to why-this-company SKILL.md
   - All speaking points and cover letter text rewritten to remove em dashes
   - Cover letter signature preference saved to memory.md ("Sincerely, Milan")

5. **Mandatory folder structure established:**
   - Company-level CONTEXT.md required for all companies (created for Disney, Lumin Digital, MrBeast; Netflix and Waymo already had them)
   - Role-level CONTEXT.md tracks workflow progress per application
   - Research brief lives at company level with two-section structure:
     - Section 1: Company Research (reusable across roles)
     - Section 2: Role-Specific Research (dated subsections per role, appendable)
   - Research briefs copied to company level for Disney, Lumin Digital, Netflix, Waymo
   - Rules documented in ARCHITECTURE.md, DESIGN_DOC.md, CLAUDE.md

6. **Why-this-company skill updated:**
   - Now generates both .md and .pdf for speaking points and cover letters
   - Signature block reads from memory.md
   - Formatting rules section added (no dashes, no fabrication)

7. **Created references/ folder:**
   - templates/: company-context.md, role-context.md, research-brief.md (blank templates)
   - scripts/: generate-speaking-points-pdf.py, generate-cover-letter-pdf.py (reportlab)
   - examples/: Full Waymo lifecycle outputs as quality benchmarks
   - patterns/: formatting-rules.md, docx-xml-editing.md, scoring-methodology.md, adaptive-qa.md
   - README.md with usage guide
   - Added to ARCHITECTURE.md folder structure and CLAUDE.md routing table

### Key Design Decisions Made This Session

- Skill numbers removed from ARCHITECTURE.md (build order != workflow order, use names instead)
- Research brief two-section structure (company reusable + role-specific appendable)
- All outputs (speaking points, cover letters) must be generated as both .md and .pdf
- Cover letter signature block is a persistent preference in memory.md
- references/ folder is the canonical location for reusable assets
- Formatting rules apply to ALL outputs, not just resumes

---

## Session 6: April 8, 2026 (continuation)

### What Happened

1. **Completed end-of-session consistency audit from Session 5:**
   - Fixed em dashes in score-before.md and score-after.md (Waymo)
   - Fixed em dashes in MrBeast decoded-jd.md and CONTEXT.md
   - Fixed em dashes in Disney role-level CONTEXT.md
   - Fixed em dashes in all three role-level research brief copies (Waymo, Disney, Lumin)
   - Fixed em dashes in ARCHITECTURE.md (replaced with --)
   - All applications/ .md files now zero em dash occurrences

2. **Created missing Lumin Digital role-level CONTEXT.md** at applications/lumin-digital/product-data-analyst-2026-04/CONTEXT.md

3. **Restructured all three remaining research briefs to two-section format:**
   - Netflix: restructured from flat format to Section 1 (Company Research) + Section 2 (Role-Specific: Data Analyst, Production Finance O&I)
   - Disney: restructured from flat format to Section 1 (Company Research) + Section 2 (Role-Specific: Lead Data Analyst, Disney Entertainment & ESPN Product & Technology)
   - Lumin Digital: restructured from flat format to Section 1 (Company Research) + Section 2 (Role-Specific: Product Data Analyst)

4. **Created MrBeast research-brief.md stub** at company level with placeholder sections

5. **Added Research Brief Format spec to DESIGN_DOC.md** as a new section between Architecture Principles and Skills

6. **Updated DESIGN_DOC.md build order** to reflect actual test counts (resume-targeter 4x, decoded-jd 1x, etc.)

7. **Updated Doc Freshness Protocol in ARCHITECTURE.md** with mandatory "Thorough Consistency Audit" section defining:
   - Formatting rules compliance (em dash grep)
   - Folder structure compliance (company + role CONTEXT.md, research-brief.md)
   - Research brief format verification
   - Cross-file consistency checks
   - CONTEXT.md accuracy verification
   - Date freshness checks

8. **Final verification pass:**
   - All 5 companies have company-level CONTEXT.md and research-brief.md: confirmed
   - All 5 role folders have role-level CONTEXT.md: confirmed
   - All 4 company-level research briefs in two-section format: confirmed (MrBeast is stub)
   - Zero em dashes in applications/ .md files: confirmed
   - DESIGN_DOC.md, ARCHITECTURE.md, CLAUDE.md status claims consistent

---

## Session 7: April 10, 2026

### What Happened

1. **Completed Waymo lifecycle Steps 8-10:**
   - Portfolio: Safety Feature Experiment A/B test (Python script + synthetic data). +8.2pp treatment effect overall, new riders +12.2pp vs returning +6.7pp, p=2e-17. Files: generate_data.py, experiment_analysis.py, figures/, README.md saved to applications/waymo/bi-analyst-2026-04/portfolio/
   - Networking: LinkedIn outreach draft for Harsh Shah (Product Data Science team) saved to networking/outreach-harsh-shah-waymo.md
   - Waymo lifecycle is now complete end-to-end (Steps 1-10)

2. **Netflix -- recruiter screen follow-up (Anna Guan):**
   - Milan had a recruiter call with Anna Guan for the Data Analyst, Production Finance O&I role
   - Drafted thank you letter addressing culture/values stumble (had notes in front of him, not internalized)
   - Values covered with verified work stories: candor + courage (Apple data integrity pushback), selflessness + curiosity (Apple AI initiative + GitHub org), judgment (adhoc + long-term path, Tableau stakeholder redirection)
   - Role context added: O&I team, 200 stakeholders, 25 teams, Global Affairs signs off on metrics, hiring manager is Bruno
   - Saved as "Thank You, Anna.md" and "Thank You, Anna.pdf" in applications/netflix/data-analyst-2026-04/
   - Note: build_notebook.py and experiment-analysis.ipynb (earlier notebook attempt) still in Waymo portfolio folder -- delete from Finder before pushing to GitHub

3. **Preference added to memory.md:**
   - No automatic CONTEXT.md progress checkbox updates
   - Ask Milan when he wants to archive files within a position's subfolder

---

## Session 8: April 10, 2026

### What Happened

1. **Pushed to GitHub** -- Initial commit (5cca876) to private repo `sharmingmilan/job-assist`. Full project snapshot: 90 files, 18,391 lines.

2. **Phase 1 folder restructure (root doc consolidation):**
   - Merged ARCHITECTURE.md into CLAUDE.md. All unique content absorbed: workflow diagram, folder structure rules, repeat-company protocol, doc freshness protocol with audit checklist, GitHub separation. ARCHITECTURE.md deleted.
   - Moved "What's Next" and "Current Status" from SESSION_LOG.md into CLAUDE.md. SESSION_LOG.md is now append-only history.
   - Replaced routing table (13 rows) with 3 convention rules. No maintenance needed when folders change.
   - Created tracker.md as central application tracker. One table with all 5 applications, status, which skills ran, decisions log. Replaces per-role CONTEXT.md for status tracking (role CONTEXT.md files still exist for now).

3. **Full audit and gap analysis completed before restructuring:**
   - Mapped every file read/write path across all 7 SKILL.md files
   - Identified 6 cross-skill read dependencies that would need updating in Phase 2
   - Documented that Milan wants output-type folder organization (resumes/, cover-letters/, decoded-jds/, etc.) instead of per-company/per-role
   - Identified tracker.md as replacement for per-role CONTEXT.md progress logs
   - Phase 2 (output-type folders) and Phase 3 (skill path updates) planned but not started

### Key Decisions

- DESIGN_DOC.md stays separate (serves humans, GitHub, and Claude)
- SESSION_LOG.md stays as append-only history (not read at session start)
- Convention-based routing over explicit routing table
- Central tracker over per-role progress logs
- Incremental restructure: Phase 1 (root docs) → Phase 2 (output folders) → Phase 3 (skill updates)
- Output-type folder structure confirmed as target for Phase 2

---

## What's Next

Moved to CLAUDE.md "Current Status & What's Next" section. SESSION_LOG.md is now append-only history.

---

## Session: 2026-05-02 (UJA Session 1) — Fork to Ultimate Job Assistant + interview-prep skill

### What Got Done

- **Project fork.** Created `Ultimate Job Assistant/` as a clean copy of `Job Assist/` (Session 9 state), preserving all 7 existing skills.
- **SPEC.md authored** as the canonical build plan: scope, architecture, decisions log, acceptance criteria, execution plan. Approved before any execution.
- **Phase 0 — Bootstrap.** Project layout cloned, git initialized, root docs written (SPEC, README, ROADMAP, ONBOARDING), .gitignore expanded for personal data exclusions. Commit `49bc5be`.
  - **PII finding mid-phase.** Discovered the inherited `skills/resume-targeter/evals/files/data_analyst_base.docx` contained a real resume with full PII. Surfaced for user decision. Decision: keep the original in commit `49bc5be` permanently; redact the working-tree version going forward; private repo never goes public; add a public `ONBOARDING.md` instead.
- **Phase 1 — Skill spec.** Authored `skills/interview-prep/SKILL.md` (425 lines) covering six-phase workflow A–F, content authoring rules, pedagogy table, generic-format support (sql/python/plaintext editors). Authored supporting `references/pedagogy.md` and `references/source-attribution-rules.md`. Preserved the original Netflix project's SPECS.md and CLAUDE.md as `skills/interview-prep/references/netflix-example/` for design provenance.
- **Phase 2 — PWA template.** Authored `content-schema.json` (JSON Schema Draft 7 contract), `index.html.template`, `app.jsx.template` (~600 lines React with parameterized SQL/Python/plaintext editor, three-phase per-topic loop, Real Qs tab with sourced attribution, citation footer), `manifest.json.template`, `sw.js`, generated neutral PWA icons, wrote `build_pwa.py` and `smoke_test.cjs` (Playwright headless). Sample content built and smoke-tested green: 45 KB bundle, brace-balanced, React mounted, citations rendered, editable textarea works.
- **Phase 3 — Orchestrator.** Inserted Step 9.5 (Interview Prep PWA) between Networking and Wrap-up in `skills/orchestrator/SKILL.md`. Updated Step 1 announce script and Step 10 wrap-up summary. Added Interview Prep PWA column to `tracker.md`. Added Skill 8 section to `DESIGN_DOC.md`.
- **Phase 4 — CI/CD.** Authored `.github/workflows/ci.yml` (13-step validation: SKILL.md frontmatter, schema validity, sample build, brace balance, bundle size, Playwright smoke, PII scan). Authored `scripts/scan_pii.py` (warn-mode in CI; strict-mode reserved for Phase 7's public-repo sync). Committed Phase 1–4 as `eb0d7ac`. Local CI simulation: 17 ✅, 1 ⚠ (expected PII in private repo), 0 ❌.
- **Phase 5 — Regression test.** Authored `skills/interview-prep/evals/build_netflix_regression.py`, generated `netflix-regression-content.json` at full Netflix shape (11 topics × 3 phases × 3 difficulties = 99 problem cards), built the PWA, ran smoke test green. Bundle: 119 KB. Documented in `skills/interview-prep/evals/netflix-regression.md`. 9 ✅ across structural-parity checks.
- **Phase 6 — Final audit.** Mandatory consistency audit per CLAUDE.md doc-freshness protocol. Surfaced 6 warnings; fixed the 3 I owned (added Last-updated to ONBOARDING.md, bumped DESIGN_DOC.md and memory.md). Other 3 warnings are pre-existing em-dashes in inherited user-facing artifacts (cover-letters, speaking-points, scores) that predate UJA and are out of scope.

### Key Decisions

- **Two-tier repo strategy.** Private repo holds the canonical project (including PII baseline commit) permanently; never goes public. Public artifact is a separate companion repo `ultimate-job-assistant-public` containing only sanitized files. Sync happens via allowlisted script with PII scanner as gate. Branch-based publish was considered and rejected as too risky.
- **Public companion + website.** Confirmed Phase 7 scope: companion repo + landing page + multi-page docs site. Hosted on GitHub Pages. Astro is the default stack for the website. Live demo PWA was option D and is deferred to v0.1.1.
- **Formatting rule scope clarified.** "No dashes as punctuation" applies to user-facing application outputs only (resumes, cover letters, speaking points, anything sent to a recruiter). Internal docs (SKILL.md, SPEC.md, etc.) prioritize readability and are out of scope. Updated `references/patterns/formatting-rules.md` and `memory.md` to match how the project actually behaves.
- **Approval cadence.** Proceed automatically when self-audit is fully green; stop and surface on any ⚠ or ❌. Repeated-but-already-approved warnings (the private-repo PII scanner output) count as informational, not blocking.

### What Got Pushed Where

- Two commits on `main` of the new private repo:
  - `49bc5be` — Phase 0 bootstrap
  - `eb0d7ac` — Phase 1–4 (skill + PWA template + CI/CD)
- Phase 5 (regression test) and Phase 6 (audit fixes) still uncommitted in working tree at the time of this log entry.

### What's Next

Phase 7: companion repo + landing page + GitHub Pages docs site. Then the v0.1.0 tag. See SPEC.md §14 and ROADMAP.md.

---

## Session: 2026-05-02 (UJA Session 2 — same-day continuation) — v0.1.0 ship + v0.1.1 architecture pivot

### What Got Done

- **v0.1.0 shipped end-to-end this session.** Phase 7 completed: `scripts/sync_to_public.py` written with allowlist + PII gate, `website/` source authored as plain static HTML + Tailwind CDN (decision flipped from Astro mid-Phase 7), `.github-pages-workflow.yml` placed for the public companion repo. Tagged `v0.1.0`.
- **GitHub publish executed.** Both repos created on github.com/sharmingmilan: `ultimate-job-assistant` (private, full v0.1.0 history including baseline `49bc5be`) and `ultimate-job-assistant-public` (public at the time, sanitized via sync). Auth done via GitHub device-flow over curl with GitHub CLI's public client_id, since SDK auth doesn't work due to no dynamic client registration. Site deployed to GitHub Pages successfully.
- **Post-ship policy turn 1 — `noindex`.** Site stays live and hosted on GitHub Pages, but `noindex` meta tags + `robots.txt: Disallow /` added. Search engines blocked. README updated with personal-toolkit note. Commit `f02d9d4` (private), `bd975b2` (public).
- **Post-ship policy turn 2 — landing-page simplification.** Rewrote `website/index.html` from product-marketing copy to a download-first design: one big "Download the latest" CTA, HEAD-fetch JS that displays size + last-modified date once the zip exists, secondary links to docs. Old marketing-style landing replaced.
- **Architecture pivot for v0.1.1.** After working through GitHub Pro pricing and hosting alternatives, settled on the final form: both repos private, hosting moves to Netlify (free tier reads private GitHub repos via OAuth), website distributes a zip download as the public artifact. Custom domain (~$12/yr) confirmed for v0.1.1.

### Key Decisions

- **Both repos go private.** The deploy-source repo `ultimate-job-assistant-public` keeps its name but flips to private. Even with `noindex`, a public GitHub repo is searchable on GitHub itself; making it private removes that surface area. See SPEC §13.
- **Netlify replaces GitHub Pages.** GitHub Pages on the free tier requires a public source repo. Netlify's free tier does not. Moving lets both repos go private. URL changes from `*.github.io` to `*.netlify.app` (or to a custom domain when bought).
- **Distribution via website zip download.** The website regenerates `website/downloads/ultimate-job-assistant.zip` on every sync. Anyone with the site URL can download. No GitHub account required to consume.
- **Auto-sync trigger: GitHub Action on canonical private repo push to main.** Every push runs the sync, which gates on the STRICT PII scanner. Edit-to-live latency target ~30 seconds.
- **The implementation work for v0.1.1 happens in a fresh Cowork session.** This session ends with all v0.1.1 design decisions documented in SPEC.md §13 + §14, ROADMAP.md decision log, and a self-contained handoff prompt that the fresh session uses to pick up.

### What Got Pushed Where (this session)

Three more commits landed on canonical `main` after v0.1.0:
  - `f02d9d4` — noindex + robots.txt + personal-toolkit README note
  - `eb0d7ac` and earlier already pushed in Session 1
  - The simplified landing page edit + the v0.1.1 doc updates are in the working tree at log time and will be committed below.

Both GitHub repos are in sync as of v0.1.0 + the noindex commit. The simplified landing page and these doc updates ship in the next commit.

### What's Next

Open a fresh Cowork session (Claude Sonnet 4.6 recommended). Use the handoff prompt at the end of this session to brief that session. The fresh session starts at SPEC §14 Phase 8 (zip generation in `sync_to_public.py`) and works through Phase 12 (custom domain wiring).

### Late addition: public base-resume template

After the v0.1.1 doc commit, added a starter resume template for public users:

- New file: `scripts/generate_template_resume.py` (uses python-docx) generates a clean DOCX that mirrors the section structure of Milan's real base resume (PROFESSIONAL SUMMARY, PROFESSIONAL EXPERIENCE, SKILLS, EDUCATION) but with all values replaced by `[BRACKETED]` placeholder text.
- Output: `references/templates/base-resume-template.docx` (~38 KB).
- Sync allowlist already covers `references/templates/`, so the template flows to the public companion repo automatically.
- ONBOARDING.md Step 3 now points users at this template if they don't already have a resume in a usable shape.
- STRICT PII scan over the new template: zero hits (all content is bracketed placeholders).
- SPEC §13 decisions list now includes item 9 documenting the template.

This unblocks the v0.1.1 zip-distribution model: when someone downloads `ultimate-job-assistant.zip` from the website, they immediately have a fillable resume template alongside the skill code.

---

## Session: 2026-05-02 (UJA Session 3 — same-day continuation) — v0.1.1 Phases 8–12 + curated zip + auto-sync

### What Got Done

- **Phase 8 — zip generation in `scripts/sync_to_public.py`.** Added `build_zip()` that produces a CURATED zip at `website/downloads/ultimate-job-assistant.zip` rather than a snapshot of either repo. The function walks the deploy-source tree, drops maintainer-only paths via `ZIP_DROP_PATHS` (scripts, .github, netlify.toml, website source itself, ROADMAP, .DS_Store), injects user-facing templates from `references/zip-bundle/` (CLAUDE.md, QUICKSTART.md, memory.md.template, tracker.md.template, .gitignore) at top-level archive paths, creates `.gitkeep` entries from `references/zip-bundle/placeholder-folders.txt`, and verifies `ZIP_REQUIRED_MEMBERS` exist before promoting the temp zip into place. Atomic rename + mtime stamp so the live site can show the freshness via HEAD request.
- **Phase 9 — initial sync after zip-build.** Both repos pushed. The first generated zip contained the curated user starter kit including the bracketed base-resume template (`references/templates/base-resume-template.docx`).
- **Phase 10 — hosting migrated GitHub Pages → Netlify.** Connected Netlify (free tier) to the deploy-source repo via GitHub OAuth. `netlify.toml` committed at the repo root pinning the publish dir + headers so the Netlify UI doesn't have to be touched. URL went from `sharmingmilan.github.io/ultimate-job-assistant-public/` to `ultimatejobassist.netlify.app`. GitHub Pages disabled for the deploy-source repo.
- **Phase 11 — deploy-source repo flipped to private.** Set via the GitHub API (`PATCH /repos/.../private`). Anonymous API hits return 404; Netlify still serves 200 because OAuth retains access through the visibility flip.
- **Phase 12 — auto-sync GitHub Action.** Authored `.github/workflows/auto-sync-to-public.yml` that triggers on every push to `main` of the canonical private repo. Pipeline: checkout canonical → set up Python → clone deploy-source repo using `PUBLIC_REPO_TOKEN` → run `scripts/sync_to_public.py --to ./public-clone` (allowlist + STRICT PII gate + curated zip build) → commit and push if anything changed. Initial classic PAT created during workflow setup ran into permission issues; replaced with a fine-grained PAT scoped only to the deploy-source repo with Contents: Read and write. Three successful workflow_dispatch runs + one successful push-event run verified end-to-end. Round-trip latency push → live zip ≈ 30 s.
- **`ONBOARDING.md` Step 7 added.** Public-user-facing walkthrough of the auto-sync setup so future fork-and-publish users can replicate the two-tier publish setup. Covers fine-grained PAT creation (with the exact permissions table), the `PUBLIC_REPO_TOKEN` secret, and the diagnostic walk-through if the workflow fails.
- **Curated zip architecture documented.** The zip is NOT a snapshot of either repo — it's built by `build_zip()` against `ZIP_INJECT_FILES`, `ZIP_DROP_PATHS`, and `ZIP_REQUIRED_MEMBERS`. `references/zip-bundle/CLAUDE.md` carries the user-facing CLAUDE with a "First Session Behavior — Detect Fresh Install And Onboard" block that walks new users through `memory.md.template` → resume drop-in → `tracker.md` initialization → optional first application.
- **Website rebrand.** Public surface text rebranded from "Ultimate Job Assistant" to "Ultimate Job Assist" on the website (titles, header, footer). Internal docs (CLAUDE, SPEC, ROADMAP) intentionally still say "Ultimate Job Assistant" — only the public-facing surface was rebranded.

### Key Decisions

- **Curated zip over snapshot.** `ZIP_DROP_PATHS` actively suppresses maintainer-only paths from the user starter kit. `ZIP_INJECT_FILES` actively injects user-facing templates. `ZIP_REQUIRED_MEMBERS` aborts the build if any of those expected paths is missing — guards against accidental over-curation. If anything in the zip layout changes, update `ZIP_INJECT_FILES` and `ZIP_REQUIRED_MEMBERS` in lockstep.
- **Fine-grained PAT over classic.** Scoped to one repo (`ultimate-job-assistant-public`), one permission (Contents: Read and write). Smaller blast radius if the token leaks. Classic PAT with `repo` scope was the original plan; switched mid-Phase-12.
- **Privacy flip kept Netlify alive via OAuth.** Verified that flipping `ultimate-job-assistant-public` private didn't break Netlify because OAuth credentials persist through visibility changes (only API token / SSH-key access fails).
- **Phase 13 (custom domain) deferred.** Originally part of the v0.1.1 plan; decided to keep the netlify.app URL until Milan buys a domain, then wire it up in a follow-up. Tag `v0.1.1` after Phase 13 ships.

### What Got Pushed Where (this session)

Commits on `main` of canonical (`ultimate-job-assistant`):
- `1faea1b` — Add netlify.toml + sync allowlist entry
- `87a79b9` — netlify.toml: pin base = "." to override stale UI setting
- `ac3c429` — Curate the zip into a working user starter kit (build_zip + ZIP_INJECT_FILES + ZIP_REQUIRED_MEMBERS)
- `0848a13` — Curate website + add First Session Behavior to zip-bundle CLAUDE.md
- `902112f` — Website: rebrand to 'Ultimate Job Assist', unify nav, prune dead pages
- `a66b16c` — ONBOARDING.md: add Step 7 — Auto-sync canonical to deploy-source

Each canonical push triggered an auto-sync run that produced a corresponding commit on the deploy-source repo (`ultimate-job-assistant-public`), authored by `uja-auto-sync`. HEAD as of session end: canonical `a66b16c`, deploy-source `dee6e7f`.

### Outstanding Cleanup

1. The classic PAT used briefly during Phase 12 setup needs revocation — its value briefly appeared in chat history during the device-flow auth.
2. The fine-grained `PUBLIC_REPO_TOKEN` is the only active credential going forward.

### What's Next

A fresh session picks up at v0.2.0 — the self-hosted local web app where users run UJA in a browser against their own Anthropic API key. Open architectural questions: frontend stack, backend stack, skill execution surface, distribution model, branch strategy. Don't push v0.2.0 work to `main` while in flight — the auto-sync workflow will publish it. Use a feature branch.
