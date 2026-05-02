# SESSION_LOG.md -- Job Assist
# Last updated: 2026-04-10

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
