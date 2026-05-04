# Phase 24.5 — Job Assist app space research (landscape)

**Status:** in-progress (Block 1 complete; Blocks 2-4 pending).
**Branch:** `phase24_5/research`.
**Phase:** 24.5 (no version bump). Inserts between Phase 24 and Phase 25 per the Phase 22.5 precedent.
**Purpose:** assemble a competitive landscape across 4 buckets of job-search-toolkit apps + cross-domain outliers, so the next interactive synthesis session (Session 14) can draft `docs/ADR-003-visual-identity.md` from evidence rather than first principles.
**Out of scope:** writing the ADR, any code changes, any v2 site touches, any v0.1.x or v0.2.x deploy-source touches. See `docs/session-13-brief.md` `## Out of scope`.
**Working scratchpad:** `docs/phase24_5-research-scratchpad.md` (committed for transparency about Block 1's selection process per Success criteria #9).
**Screenshots:** `docs/phase24_5-screenshots/<app-slug>.png|.jpg` per R4. Each accompanied by `<app-slug>-source.md` documenting where the image came from.

---

## App selection

Twelve in-bucket apps + three cross-domain outliers = **15 total**. Locked end of Block 1.

### Bucket 1 — Application trackers (SaaS)

The closest direct competitors. Pipeline-stage + status-badge UX is the load-bearing pattern v2 will either inherit or deliberately reject.

| # | App | URL | Rationale for inclusion |
|---|-----|-----|-------------------------|
| 1 | **Huntr** | https://huntr.co | Kanban-pipeline reference. Mobile-first. Industry default for "drag a card from Saved to Applied." Per-2026 round-ups consistently the visual-pipeline benchmark. |
| 2 | **Teal** | https://www.tealhq.com | All-in-one. Resume optimizer + tracker + LinkedIn integration in one surface. Per-2026 round-ups the "overall winner" reference. Useful for testing the "everything-on-one-page" anti-pattern hypothesis. |
| 3 | **Simplify Jobs** | https://simplify.jobs | Autofill across Workday / Greenhouse portals. High-volume-applicant UX. Different shape from kanban — utility-first browser-extension-driven. Tests whether a non-pipeline tracker shape is viable. |

R6 (user reviews) is mandatory for ≥3 apps spanning ≥2 categories — Huntr + Teal will get the user-review subsection (G2 / Capterra / ProductHunt).

### Bucket 2 — AI resume / cover-letter tools

Not direct competitors to a tracker, but visually load-bearing — they own the same "personal job toolkit" mental shelf in user heads. Three-axis spread chosen deliberately.

| # | App | URL | Rationale for inclusion |
|---|-----|-----|-------------------------|
| 4 | **Rezi** | https://www.rezi.ai | Utility / ATS-focused end of the spectrum. "Strongest ATS focus with keyword targeting and resume scoring." Clean, almost stark UI. |
| 5 | **Enhancv** | https://enhancv.com | Design-forward end of the spectrum. "Visually stunning, design-forward resumes with unique sections for expressing personality." The maximalist counter-reference. |
| 6 | **Jobscan** | https://www.jobscan.co | Analytical-tool end of the spectrum. Paste-resume-vs-JD → match score + recommendations. Surfaces the "report card" UX shape v2 score-reports could draw from. |

R6 user-review subsection on **at least one** of these (Rezi the most likely, given its volume of public reviews).

### Bucket 3 — Personal job dashboards (Notion / Airtable templates)

The DIY end. Closest to v2's "personal toolkit, files in folders" positioning shape — these are templates users adopt and customize, not SaaS they subscribe to.

| # | App | URL | Rationale for inclusion |
|---|-----|-----|-------------------------|
| 7 | **Notion: "The Job Application Tracker" (official)** | https://www.notion.com/templates/the-job-application-tracker-815 | Notion-listed dashboard-style template. The reference for "dashboard with multiple linked databases." |
| 8 | **Notion: "Job & Internship Application Tracker" (NotiNova)** | https://www.notion.com/templates/application-traker-job-internship | Third-party kanban-first Notion template. Visual contrast with #7's dashboard shape. |
| 9 | **Airtable: Applicant Tracking System** | https://www.airtable.com/templates/applicant-tracking-system | Relational-database shape. Structurally different from Notion's block-based shape. Even though the template is recruiter-facing, multiple round-ups call out its adaptability for personal use. |

### Bucket 4 — Indie maker download hubs / "tools I built" sites

The closest visual / posture analog to v2's positioning. Personal sites that function as tool delivery hubs. The three picks intentionally span three different visual personalities.

| # | App | URL | Rationale for inclusion |
|----|-----|-----|-------------------------|
| 10 | **Levels.io / Projects** | https://levels.io/projects/ | Pieter Levels' running list of projects + side projects. "Personal site as project hall of fame." Neon-on-black brutalist visual personality. |
| 11 | **Stephango.com** | https://stephango.com | Steph Ango (Obsidian CEO) personal site. Ships Minimal theme + ancillary tools. Austere-serif visual personality. The closest "small set of tools, well-curated" posture analog to v2. |
| 12 | **Robb Knight (rknight.me)** | https://rknight.me | Self-described "maker of web things." Personal site that doubles as a download / portfolio hub. Warm-blog visual personality. The third axis of the indie-hub spectrum. |

R6 user-review subsection is N/A for Bucket 4 — these are personal sites, not products with public review aggregators.

### Outliers — cross-domain personal-toolkit shapes (R7)

Outside the job-search space entirely. Each surfaces a positioning shape v2 is closer to than to any of the four buckets above.

| # | App | URL | Rationale for inclusion |
|----|-----|-----|-------------------------|
| 13 | **Are.na** | https://www.are.na | Visual research / collection tool. "Calm internet" aesthetic. Anti-attention-economy posture. The closest positioning analog to v2's "personal local-first toolkit" shape outside job-search. |
| 14 | **Pinboard** | https://pinboard.in | Minimalist bookmarking service. Single-developer, anti-SaaS, ASCII-tier UI. Anti-pattern reference for the extreme minimal end of the density spectrum. |
| 15 | **Hello.cv** | https://hello.cv | Minimal personal profile / personal-site successor to the now-shut-down Read.cv. ".cv" identity-as-personal-site shape. Reference Wayback Machine for Read.cv's pre-shutdown UI as supplementary if useful. |

R6 user-review reading is **not required** for outliers per R7's last sentence.

---

## Per-app deep dives

> **Status:** Block 2 pending. Each per-app section will follow the R2 rubric: URL, visual takeaway, layout pattern, palette, status conventions, density, standout pattern, anti-pattern, screenshot reference. **No copy-voice line per-app per R5.** User-review subsections appear only on the apps flagged above. Group under four `## Category:` headings + the outliers section.

### Category: Application trackers (SaaS)

_TODO Block 2 — Huntr, Teal, Simplify Jobs._

### Category: AI resume / cover-letter tools

_TODO Block 2 — Rezi, Enhancv, Jobscan._

### Category: Personal job dashboards (templates)

_TODO Block 2 — Notion (official), Notion (NotiNova), Airtable._

### Category: Indie maker download hubs

_TODO Block 2 — Levels.io / Projects, Stephango.com, Robb Knight._

## Outliers — cross-domain personal-toolkit shapes

_TODO Block 2 — Are.na, Pinboard, Hello.cv._

---

## Cross-app patterns

> **Status:** Block 3 pending. This section aggregates findings across categories: layout-shape frequency, color conventions, status nomenclature variance, density conventions, where v2 guardrails (ADR-002 §D4) align with the landscape vs where they diverge.

### Copy voice across the landscape

_TODO Block 3 — single ~250-400 word subsection per R5, 4-6 representative phrases (≤15 words each, in quotes, URL-attributed), voice clusters classified, with notes on which clusters dominate which categories. This is the only place copy-voice gets systematic treatment._

### Privacy-first messaging conventions

_TODO Block 3 — ~200-300 words, 3-4 representative phrases (≤15 words each, in quotes, URL-attributed). How "local-first" / "no tracking" / "your data stays yours" is positioned visually and verbally across the landscape, with attention to the indie-maker bucket and any privacy-leaning entries elsewhere._

---

## Recommendations for ADR-003 synthesis

> **Status:** Block 4 pending. 5-10 specific patterns the orchestrator should consider, framed as questions ADR-003 will answer (NOT foregone conclusions).

_TODO Block 4._

## Open questions

> **Status:** Block 4 pending. Things the research surfaced but couldn't resolve, plus any ambiguities Phase 24.5 chose to defer.

_TODO Block 4._

---

*End of landscape doc (Block 1 complete).*
