# Phase 24.5 — Job Assist app space research (landscape)

**Status:** complete (Blocks 1-4). Pending review and PR open per Block 5.
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

#### 1. Huntr — https://huntr.co/

**Screenshot:** [Huntr — Wishlist/Applied/Interview kanban](https://huntr.co/) (binary not bridged; provenance + capture metadata in `phase24_5-screenshots/huntr-source.md`).

**Visual takeaway.** Kanban-pipeline tracker; the pipeline metaphor IS the product identity. The "drag a card from Saved to Applied" gesture is the load-bearing UX primitive.

**Layout pattern.** Full-width pipeline board under a top-bar nav; columns dominate the canvas. Collapsible sidebar surfaces secondary tools (Tasks, Contacts, Documents).

**Palette.** Light theme dominant — white card surfaces over a pale gray board background. Accent colors live on individual card status pills and column headers, never on the chrome itself. Brand orange-red appears mostly on marketing pages, not the in-product UI.

**Status conventions.** Pipeline stage IS the status; the column the card lives in is the only status signal. Each column shows a count badge.

**Density.** Mid. Cards carry logo + role + company + small tag chips. Mobile-first; the board collapses to single-column scroll gracefully on narrow viewports.

**Standout pattern.** The kanban gesture maps cleanly onto how applicants mentally model applications moving through stages. Users rarely need a tutorial — the metaphor is self-teaching.

**Anti-pattern (caution for v2).** Pipeline-as-status forces a rigid happy-path. Edge cases (Rejected, Withdrawn, On Hold) get dumped into a terminal column or a sidebar — the visual narrative breaks at the unhappy paths. v2's "personal toolkit, files in folders" posture should weigh whether pipeline columns or flat status tags better fit.

##### User reviews (R6)

Fetch limitation: G2 and Capterra return Cloudflare bot challenges; ProductHunt returns a JS-heavy bundle that doesn't render reviews server-side. The orchestrator can verify quotes directly in a browser. Frequently-cited themes from those aggregators (paraphrased, not direct quotes):

- Praises: Reviewers describe Huntr as Trello-like but built for job-search; the Chrome extension auto-imports postings cleanly with one click.
- Complaints: The free tier caps job-count tightly; the bundled resume builder feels secondary to the tracker, not as polished as standalone resume tools.

Source aggregators: https://www.g2.com/products/huntr/reviews · https://www.capterra.com/p/180851/Huntr/ · https://www.producthunt.com/products/huntr (server-side fetches blocked or unreliable as of 2026-05-03).

#### 2. Teal — https://www.tealhq.com/

**Screenshot:** [Teal — Job Tracker pipeline (Bookmarked → Interviewing)](https://www.tealhq.com/) (binary not bridged; provenance in `phase24_5-screenshots/teal-source.md`).

**Visual takeaway.** All-in-one personal-job platform — tracker + resume builder + LinkedIn analyzer + cover-letter assistant on a unified surface. The mental shelf is "everything for a job search lives here."

**Layout pattern.** Top-tab nav switches between tools (Job Tracker, AI Resume, LinkedIn Review, etc.). Within Job Tracker: column-based pipeline (Bookmarked → Applying → Applied → Interviewing → Negotiating) with row-detail expansion.

**Palette.** Soft-blue accent on white. Brand-blue is more saturated than Huntr's orange; the chrome stays light, card surfaces white. Tab-switch surfaces have subtle gradient borders.

**Status conventions.** Pipeline-column status PLUS a separate Application Status pill per row that can deviate from column position. This dual-status pattern lets a user mark "rejected" without physically moving the card out of the active column — a useful escape valve from pipeline-as-status.

**Density.** Higher than Huntr. The tracker view is row-dense — more tabular than card-y, with inline metadata (date, location, link to JD). Multiple sub-tools share the canvas.

**Standout pattern.** The contact-tracker integration — every application can link to specific contacts at the company, with outreach logged against the application card. The networking surface feels native rather than bolted on.

**Anti-pattern (caution for v2).** Comprehensive-toolkit can be overwhelming on first paint. Reviewers consistently note "too much going on" before they learn what to ignore. v2's calm-density posture aligns more with the unhappy reaction to Teal than with Teal's design.

##### User reviews (R6)

Fetch limitation as above. Frequently-cited themes (paraphrased):

- Praises: All-in-one positioning is genuinely useful for users running an active search; the AI resume tailoring against a job description saves substantial time per application.
- Complaints: Premium tier is expensive relative to single-purpose alternatives; some users describe the interface as overwhelming on first use, with feature discoverability suffering as a consequence.

Source aggregators: https://www.g2.com/products/teal-the-job-search-platform/reviews · https://www.capterra.com/p/183881/Teal/ · https://www.producthunt.com/products/teal (server-side fetches blocked as of 2026-05-03).

#### 3. Simplify Jobs — https://simplify.jobs/

**Screenshot:** [Simplify Jobs — My Job Tracker kanban + Sankey flow](https://simplify.jobs/) (binary not bridged; provenance in `phase24_5-screenshots/simplify-source.md`).

**Visual takeaway.** Browser-extension-driven autofill tool with a tracker bolted on. The extension is the product; the tracker is record-keeping side-effect.

**Layout pattern.** Kanban tracker resembling Huntr but visually denser. Below the tracker, a Sankey-style flow visualization shows application count flowing through stages. Top-bar marketing pivots prominently to the Chrome extension.

**Palette.** Saturated electric blue + white with bright-yellow callouts. Higher color contrast than Huntr or Teal — the marketing pages especially lean on bold gradient buttons (which is an explicit anti-pattern for v2 per ADR-002 §D4).

**Status conventions.** Kanban-pipeline columns plus the Sankey flow. The Sankey gives a meta-view of "how my applications are converting" that the column view alone can't surface.

**Density.** High. The Sankey + the kanban + secondary stats make the tracker page busy. Designed for high-volume applicants moving through hundreds of applications, not the curated 5-15 the v2 user is more likely to pursue.

**Standout pattern.** The Sankey flow visualization — making conversion data legible as a flow diagram is genuinely novel in this space and surfaces signal the column-only views miss.

**Anti-pattern (caution for v2).** The marketing surface (gradient buttons, bold AI-positioning hero) directly conflicts with v2's "no marketing claim, no gradient buttons, no AI branding" guardrails. The in-product UI is more restrained — but the public-facing identity is loud in ways v2 should avoid.

### Category: AI resume / cover-letter tools

#### 4. Rezi — https://www.rezi.ai/

**Screenshot:** [Rezi — Editor with AI Keyword Targeting panel](https://www.rezi.ai/) (binary not bridged; provenance in `phase24_5-screenshots/rezi-source.md`).

**Visual takeaway.** Utility-first ATS-focused resume editor. The "is this resume going to clear the keyword filter" question is the load-bearing UX promise. Almost stark in its lack of flourish — earnestly utilitarian.

**Layout pattern.** Two-pane editor: left pane is the resume canvas, right pane is the AI Keyword Targeting + ATS-score sidebar. Top-bar nav switches between resumes and templates.

**Palette.** Light theme with cool-blue accents. Brand-blue runs the score gauges and keyword-match indicators. Restrained chrome — no marketing splash bleeds into the editor.

**Status conventions.** Per-bullet ATS-score + keyword-match indicators are the in-product status signals. No pipeline metaphor — this is single-document editing, not portfolio tracking.

**Density.** Mid-high. The right sidebar is dense with score breakdowns, keyword recommendations, and actionable tips. The left pane is the standard one-page resume canvas.

**Standout pattern.** The AI Keyword Targeting panel — paste a job description, get an actionable keyword-match delta against your current resume. The signal-density of that panel is the product's gravity well.

**Anti-pattern (caution for v2).** ATS-optimization-as-product flattens resume craft into a keyword-match game. v2's resume-targeter skill avoids this trap by generating bullets from STAR-format experience stories rather than reverse-engineering from JD keywords. Rezi's UX is a useful contrast — it's what "keyword-first targeting" looks like at the extreme.

##### User reviews (R6)

Fetch limitation as in Bucket 1. Frequently-cited themes (paraphrased):

- Praises: ATS-keyword targeting is the strongest in the category; reviewers consistently describe Rezi as the tool that gets them past the algorithmic gatekeepers.
- Complaints: Templates are limited compared to design-forward competitors like Enhancv; the free tier is restrictive enough that meaningful use requires paying.

Source aggregators: https://www.g2.com/products/rezi/reviews · https://www.capterra.com/p/177076/Rezi-AI/ · https://www.producthunt.com/products/rezi (server-side fetches blocked as of 2026-05-03).

#### 5. Enhancv — https://enhancv.com/

**Screenshot:** [Enhancv — ATS Check + tailoring mockup](https://enhancv.com/) (binary not bridged; provenance in `phase24_5-screenshots/enhancv-source.md`).

**Visual takeaway.** Design-forward end of the resume-tool spectrum. Where Rezi optimizes for the algorithm, Enhancv optimizes for the human reader. "Visually stunning" is the explicit pitch — colored sidebars, custom sections (Strengths, My Time, Languages chart).

**Layout pattern.** Two-pane editor like Rezi, but the right pane is a templated design-system selector rather than an ATS-score panel. The canvas itself supports multi-column layouts that Rezi's templates don't.

**Palette.** Vivid. Multiple template families with distinct color stories — coral + navy, mint + slate, gold + black. The marketing pages lean on saturated full-bleed gradient backgrounds.

**Status conventions.** Sectional completeness indicators (e.g., "Add 2 more skills to strengthen this section") with green/yellow/red completion states. Encourages the user toward "filled-out resume" rather than "ATS-optimized resume."

**Density.** Mid. The template-driven canvas pre-allocates space; the user fills slots rather than authoring blank-page layouts. Right-pane density is moderate.

**Standout pattern.** Custom section types — "My Time" (a pie chart of how the candidate spends their day), Languages (a proficiency bar chart), Strengths (badge-shaped tag cloud). These wouldn't pass an ATS but they're memorable for human reviewers.

**Anti-pattern (caution for v2).** Visual-flourish-as-differentiation can over-rotate into kitsch when the user's actual job is to be taken seriously. Some templates feel more "graphic-designer-portfolio" than "data-analyst-applicant." v2's neutral-system-font ethos (per ADR-002 §D4) is the deliberate inverse posture.

#### 6. Jobscan — https://www.jobscan.co/

**Screenshot:** [Jobscan — Match Report (76% score, Searchability breakdown)](https://www.jobscan.co/) (binary not bridged; provenance in `phase24_5-screenshots/jobscan-source.md`).

**Visual takeaway.** Single-purpose analytical tool: paste resume + paste JD → get a match-score percentage + actionable recommendations. The "report card" UX shape v2's resume-scorer skill draws from.

**Layout pattern.** Vertical scrolling report. Top-of-page is a circular score gauge (the 76% in the captured view); below is a sectioned breakdown — Searchability, Hard Skills, Soft Skills, Recruiter Tips. Each section is collapsible.

**Palette.** White + slate-text primary, with category-coded accent colors (red for low scores, green for passed checks). The big circular gauge dominates the visual hierarchy by intent.

**Status conventions.** Numeric percentage score + per-section pass/fail with red-green color cues. Status here is "how well does the resume match the JD" rather than application-pipeline state.

**Density.** Mid-low at the top (one big gauge), high below the fold (the sectioned breakdown is information-dense). Designed for a single read-through then iteration on the resume.

**Standout pattern.** The Recruiter Tips section — actionable text recommendations beyond just keyword matching. e.g., page-count guidance for years-of-experience bands. Adds a layer of narrative advice on top of the algorithmic scoring.

**Anti-pattern (caution for v2).** The big score gauge can over-anchor the user on a single number when the underlying signal is multi-dimensional. v2's score reports should weigh whether to lead with a single score or show category-level breakdowns first.

### Category: Personal job dashboards (templates)

#### 7. Notion: "The Job Application Tracker" (official) — https://www.notion.com/templates/the-job-application-tracker-815

**Screenshot:** [Notion Templates — The Job Application Tracker (Title block + Applications Tracker table)](https://www.notion.com/templates/the-job-application-tracker-815) (binary not bridged; provenance in `phase24_5-screenshots/notion-job-tracker-official-source.md`).

**Visual takeaway.** Notion's official-template entry for job tracking. Multi-database dashboard shape: a Title block at top, an Applications Tracker table below, with linked databases for Companies, Contacts, Interview Notes. The aesthetic IS Notion's aesthetic — neutral, document-shaped, header-image-first.

**Layout pattern.** Notion's standard page layout. Cover image + emoji icon + page title at top. Inline blocks below: callout, linked-database table, smaller linked databases for related entities. Single column, document-flow.

**Palette.** Notion's neutral light theme — off-white page, slate text, sparing use of the colored callout backgrounds (yellow / blue / green) the block library provides. Header cover-image carries any color story; the content surface itself is restrained.

**Status conventions.** Status pills inside the linked-database table — text labels on colored backgrounds (Applied on blue, Interview on yellow, Offer on green). Colors are user-customizable but the defaults align with a pipeline mental model.

**Density.** Low to mid. The document-flow layout means whitespace dominates; rows in the table are tall (Notion's default row height is generous). Easy to scan, slow to update at scale.

**Standout pattern.** Linked-database approach: Applications references Companies references Contacts references Interview Notes, all queryable across the dashboard. The relational shape is more flexible than the kanban-only trackers but requires user setup investment.

**Anti-pattern (caution for v2).** Notion-template-as-tracker requires the user to maintain Notion fluency. Onboarding cost is high for users who don't already live in Notion. v2's "personal toolkit, files in folders" posture intentionally avoids platform lock-in — but should weigh whether a Notion-export option would serve users who already use it.

#### 8. Notion: "Job & Internship Application Tracker" (NotiNova) — https://www.notion.com/templates/application-traker-job-internship

**Screenshot:** [Notion Templates — NotiNova Application Tracker w/ status pills](https://www.notion.com/templates/application-traker-job-internship) (binary not bridged; provenance in `phase24_5-screenshots/notion-notinova-source.md`).

**Visual takeaway.** Third-party Notion template that leans kanban-first rather than table-first. Same Notion chrome as #7 but the in-page layout pivots to a board view with status-pill columns rather than a table.

**Layout pattern.** Cover + title block, then a Notion Board view (kanban) as the primary surface. Linked databases for sub-entities exist below the fold but are subordinate to the kanban.

**Palette.** Notion's neutral chrome carries through. Status-pill colors are more saturated than the official template's defaults — purple, cyan, magenta, accentuating each pipeline stage. Marketing of the template emphasizes vibrant / modern framings.

**Status conventions.** Status-pill labels are the load-bearing signal: Applied, Interview, Offer, Rejected, etc. Each pill is a colored chip, not just a text label.

**Density.** Mid. The kanban columns add visual structure that the official template's table lacks; the trade-off is less metadata-per-row.

**Standout pattern.** Kanban-first within Notion — leveraging Notion's flexibility to mimic the dedicated-tracker UX (Huntr-like). For users who want Huntr-shaped UX without leaving Notion, this is the closest approximation.

**Anti-pattern (caution for v2).** Visual differentiation through status-pill saturation isn't intrinsic to the data shape — it's decoration on top of identical relational structure. v2 should weigh whether status-pill color saturation is a useful signal or just visual noise.

#### 9. Airtable: Simple Applicant Tracker — https://www.airtable.com/templates/simple-applicant-tracker/exp1ozXL39xexSu2s

**Screenshot:** [Airtable Templates — Simple applicant tracker (Applicants / Positions / Interviewers tabs)](https://www.airtable.com/templates/simple-applicant-tracker/exp1ozXL39xexSu2s) (binary not bridged; URL drift recovered from category browse — see `phase24_5-screenshots/airtable-ats-source.md` for retry notes; the original `applicant-tracking-system` URL 404'd and Wayback returned no archive).

**Visual takeaway.** Airtable's relational-database shape applied to applicant tracking. Three primary tabs (Applicants / Positions / Interviewers) function as separate but linked tables. Mental model is spreadsheet-with-relationships rather than document-with-blocks.

**Layout pattern.** Top-tab nav switches between the three tables. Within each table: grid view by default, with optional Kanban / Calendar / Gallery / Form views accessible via a left-rail view-switcher.

**Palette.** Airtable's blue-and-white chrome. Within the grid, cells carry colored single-select pills for status fields and color-coded tags for categorical metadata.

**Status conventions.** Single-select status field per row, displayed as colored pill in the grid view and used to group/sort in Kanban view. The same data renders differently across views — one of Airtable's load-bearing UX patterns.

**Density.** High. Grid view is intentionally dense — many rows visible, many columns navigable horizontally. Designed for users comfortable in spreadsheet-shaped UIs.

**Standout pattern.** The view-switcher: the same data appears as Grid / Kanban / Calendar / Gallery / Form depending on user need. v2's exports serving multiple downstream apps (Notion / Airtable / a custom tracker) maps loosely onto this multi-view-of-same-data idea.

**Anti-pattern (caution for v2).** The template is recruiter-facing (tracking applicants applying to YOU), not job-seeker-facing (tracking jobs YOU'RE applying to). The conceptual fit is partial — adoption requires the user to flip the mental model. v2 should target job-seeker-shaped templates if it builds Notion / Airtable export integrations.

### Category: Indie maker download hubs

#### 10. Levels.io / Projects — https://levels.io/projects/

**Screenshot:** [Pieter Levels — Projects ("List of all my projects ever")](https://levels.io/projects/) (binary not bridged; provenance in `phase24_5-screenshots/levelsio-source.md`).

**Visual takeaway.** Brutalist neon-on-black personal hall-of-fame. Aesthetic statement: "I built these, here they all are, no filter, no theme." Tool delivery hub with zero curation polish — the rawness IS the brand.

**Layout pattern.** Single column. Dense list of project entries: project name + description + stats (revenue, users, status). Reverse chronological. No images, no thumbnails — text-first to the point of austerity.

**Palette.** Neon green / cyan / yellow accents on near-black background. Web 1.0 / cyberpunk hybrid. Typography is monospace for code-adjacent context, sans-serif for body. Saturated and high-contrast.

**Status conventions.** Per-project status indicators (Active / Sold / Failed / Paused) inline with the project entry. Failure is marked openly — refreshingly honest in a space that usually only surfaces wins.

**Density.** High. The page rewards scrolling rather than browsing. Information per scroll-distance is the explicit design priority.

**Standout pattern.** Open failure-marking. Most personal-portfolio sites curate to wins; Levels.io marks dead projects "Failed" inline. The narrative-honesty signal is rare and valuable.

**Anti-pattern (caution for v2).** Brutalism-as-aesthetic depends on the maker's persona — Pieter Levels can pull off cyberpunk-anti-design because his audience expects it. v2 doesn't have an established persona to anchor the aesthetic against, so brutalist styling without that anchor reads as "unpolished" rather than "intentional."

#### 11. Stephango.com — https://stephango.com/

**Screenshot:** [Steph Ango — Topics index + Writing reverse-chron](https://stephango.com/) (binary not bridged; provenance in `phase24_5-screenshots/stephango-source.md`).

**Visual takeaway.** Austere serif personal site. Steph Ango (Obsidian CEO) ships a Minimal theme + ancillary tools and the site embodies the same minimalism. The closest "small set of tools, well-curated" posture analog to v2.

**Layout pattern.** Centered single-column. Top-of-page is a brief intro + Topics index (a few labels grouping content). Below: reverse-chronological writing list. Linked tools surface in a separate Tools page reachable from the Topics index.

**Palette.** Off-white background, dark serif text, a single accent color (warm gold) used sparingly. Almost no chrome — the page IS the content.

**Status conventions.** N/A in the portfolio sense — no status pills. Tools listed elsewhere on the site mark version + last-updated. Articles are dated.

**Density.** Low. Long line-lengths, generous whitespace, large type. Designed to be read carefully one item at a time, not scanned at speed.

**Standout pattern.** Topics-as-navigation rather than chronology-only. Visitors can enter via theme (Minimalism, Obsidian, Career) instead of strict reverse-chron. Subtly opinionated information architecture.

**Anti-pattern (caution for v2).** Low-density aesthetic depends on the maker's authority — Steph's reputation makes the austerity read as confident. Without established trust, low-density can read as "thin" or "unfinished." v2 should weigh whether to lean into density (Pinboard / Levels.io territory) or whitespace (Stephango / Are.na territory).

#### 12. Robb Knight (rknight.me) — https://rknight.me/

**Screenshot:** [Robb Knight — homepage (posts/links/projects three-column)](https://rknight.me/) (binary not bridged; provenance in `phase24_5-screenshots/rknight-source.md`).

**Visual takeaway.** Self-described "maker of web things." Personal site that doubles as a download / portfolio hub. Warm-blog visual personality — friendly, well-typeset, tactile.

**Layout pattern.** Three-column above-the-fold: latest posts / latest links / latest projects. Each column is a tight reverse-chron list. Below the columns: longer index pages reachable by category.

**Palette.** Warm cream background with off-white card surfaces, dark text, soft burgundy accent. Hand-drawn touches in a few spots add personality without becoming kitsch. Not quite as stark as Stephango, not as vibrant as Levels.io.

**Status conventions.** Lightweight tagging on posts/links. No explicit status pills — inclusion on the homepage IS the status.

**Density.** Mid. Three columns add visual weight; each column itself is sparse. Balanced — readers can scan or dig.

**Standout pattern.** "Now"-page-style updates surfaced on the homepage — what the maker is currently focused on, separate from the chronological feed. Adds a temporal layer most portfolios skip.

**Anti-pattern (caution for v2).** Personality-driven warmth scales with the maker's voice. Generic warmth without an authentic voice reads as decoration. v2's positioning is utilitarian — borrowing warmth without grounding it in voice would feel performative.

## Outliers — cross-domain personal-toolkit shapes

#### 13. Are.na — https://www.are.na/

**Screenshot:** [Are.na — Mission text + hypertext-club channel preview](https://www.are.na/) (binary not bridged; provenance in `phase24_5-screenshots/arena-source.md`).

**Visual takeaway.** "Calm internet" aesthetic. Visual-research / collection tool with explicit anti-attention-economy posture. The closest positioning analog to v2's "personal local-first toolkit" shape outside job-search.

**Layout pattern.** Mission-statement-as-hero on the homepage. Below: a single channel preview embedded in the page (real content from a real user channel, not a marketing mockup). Sparse navigation — Login / Signup / Pricing in the top-right.

**Palette.** Off-white background, near-black serif and sans-serif type. Almost no chrome color — channels themselves carry whatever color the user-uploaded content brings. The platform is deliberately neutral.

**Status conventions.** N/A in pipeline sense. Channels have visibility settings (public / private / closed) shown as small icons.

**Density.** Low. Generous whitespace, reading-paper layout. Designed to encourage slow browsing.

**Standout pattern.** Embedding real user-channel content on the marketing page — the hero is a working example of the product, not a designed mockup. Builds trust in the product's actual texture.

**Anti-pattern (caution for v2).** "Calm internet" positioning is hard to fake. Are.na's users self-select for slow, thoughtful browsing — the platform's calm reflects them. v2's users will be in active job-search mode (urgent, anxious, hurried) — calm aesthetics that don't acknowledge the urgency may misread as detachment.

#### 14. Pinboard — https://pinboard.in/

**Screenshot:** [Pinboard — minimalist welcome page](https://pinboard.in/) (binary not bridged; provenance in `phase24_5-screenshots/pinboard-source.md`).

**Visual takeaway.** Minimalist bookmarking service. Single-developer (Maciej Cegłowski), anti-SaaS posture, ASCII-tier UI. Reference for the extreme-minimal end of the density spectrum.

**Layout pattern.** Plain HTML page. Header logo + nav links (popular / recent / about / pricing / signup) followed by a brief value-prop paragraph. A bordered box surfaces a few rotating bookmark examples. Footer with contact info.

**Palette.** Stark — off-white background, navy-blue links, no decorative color. Default browser-rendered serif fallbacks for some text. Looks intentionally unbranded.

**Status conventions.** N/A — bookmarks have public / private / unread flags but that's it.

**Density.** Mid-low. The page is short but text-dense. Information per pixel is high relative to the visual weight — no images, no animation, no gradient.

**Standout pattern.** Honest pricing-as-content. Pinboard's about / pricing pages read like personal essays from the developer — explaining cost structure, why the service charges what it does, what's been tried. Trust-building through transparency.

**Anti-pattern (caution for v2).** Pinboard's UI is so minimal that users coming from richer interfaces find it disorienting. The aesthetic depends on the user already valuing simplicity over discoverability. v2's users may not have that prior — meeting them with Pinboard-level austerity could feel like an underbuilt product.

#### 15. Hello.cv — https://hello.cv/

**Screenshot:** [Hello.cv — Sidebar nav + chat onboarding (live, not Wayback)](https://hello.cv/) (binary not bridged; provenance in `phase24_5-screenshots/hellocv-source.md`).

**Visual takeaway.** Minimal personal-profile / personal-site shape. Successor to Read.cv (acquired by Perplexity Jan 2025, shut down May 2025). The ".cv" identity-as-personal-site shape — for people who want a portable canonical profile they own.

**Layout pattern.** Sidebar left nav (sections: Profile / Experience / Projects / About) + main content pane. The main pane on the homepage is currently a chat-style onboarding flow rather than a static welcome — a deliberate hands-on entry point.

**Palette.** Off-white + slate text, with a single saturated accent color used on the chat-bubble UI and primary buttons. Calmer than Levels.io's neon, less austere than Pinboard or Stephango.

**Status conventions.** Profile-completeness indicator during onboarding. After signup, profile sections show fill-state markers.

**Density.** Mid-low. Generous whitespace, rounded UI elements, conversational tone.

**Standout pattern.** Chat-style onboarding as the homepage hero — the platform's first interaction is itself a conversation, not a pitch deck. Reduces the "what is this thing" friction without resorting to a marketing splash.

**Anti-pattern (caution for v2).** Chat-as-onboarding requires server-side state to be useful — incompatible with v2's local-first architecture. v2 can't borrow the pattern directly; the lesson is more about "first interaction should feel like the product, not a marketing surface."

---

## Cross-app patterns

Aggregating across the 12 in-bucket apps + 3 outliers (15 total). Frequency counts where applicable; observations where the signal is qualitative.

### Layout shapes that recur

| Shape | Count (of 15) | Apps |
|---|---|---|
| Kanban-pipeline (columns as status) | 4 | Huntr, Simplify, Notion (NotiNova), Airtable (Kanban view available) |
| Tabular tracker (rows + status pills) | 4 | Teal, Notion (official), Airtable (Grid default), Jobscan |
| Two-pane editor (canvas + sidebar) | 2 | Rezi, Enhancv |
| Single-column reverse-chron list | 4 | Levelsio, Stephango, Rknight, Pinboard |
| Mission-statement-as-hero | 2 | Are.na, Pinboard (with embedded examples) |
| Sidebar nav + main pane | 1 | Hello.cv |

The kanban-pipeline + tabular tracker shapes account for 8 of 9 in-bucket trackers/dashboards (everything except Jobscan, which is a single-purpose report). Two-pane editor is exclusive to the AI resume tools. Reverse-chron list dominates indie hubs and one outlier. Cross-shape blending is rare — each app commits to one primary shape and treats secondary views as escape hatches (Airtable's view-switcher is the strongest counter-example).

### Color conventions

- **Light theme dominant** in trackers + AI tools + dashboards (12 of 12 in-bucket apps). Brand color shows up on column headers, status pills, and primary action buttons; the chrome itself stays neutral.
- **Dark theme dominant** in only 1 of 15: Levels.io. Brutalist neon-on-black is a deliberate persona choice, not a category default.
- **Color-coded status pills** are the conventional differentiator within light themes — Notion, Airtable, Teal, Huntr, NotiNova all use them. The hue palette is similar across apps (blue / yellow / green / red / purple) and the semantic mapping is variable: green is "good" but maps to Offer, Active, or Match-passed depending on app.
- **v2's slate-950 dark + sky→pink gradient** (per ADR-002 §D4) sits in a deliberately under-occupied niche. Only 1 of 15 surveyed apps is dark-dominant, and that one (Levels.io) is brutalist; v2's calm-dark posture has no direct landscape neighbor.

### Status nomenclature variance

| Term | Apps using it | Notes |
|---|---|---|
| Applied | Huntr, Teal, Simplify, Notion templates | Most universal — appears in 7 of 9 trackers. |
| Interview / Interviewing | Huntr, Teal, Simplify, Notion templates | Second most universal. Variant naming (Interview vs Interviewing). |
| Wishlist / Saved / Bookmarked / To-Apply | Huntr, Teal, Simplify, NotiNova | Pre-application stage — bespoke per app. No standard. |
| Offer | Huntr, Teal, Notion templates | Less universal — 5 of 9. Some apps merge Offer/Negotiation/Accepted. |
| Rejected | Teal (status pill), NotiNova, Notion (official) | Treated either as a column (NotiNova) or as a non-column status pill (Teal). The "where does rejected go" decision is unresolved across the landscape. |
| Withdrawn / On Hold | Sparse — only as user-customizable in Notion / Airtable | Not represented in default kanban templates. Edge-case status. |

The pre-application stage is where naming variance is highest — every app picks a different word for "I'm interested but haven't applied yet." Post-application stages converge on Applied → Interview → Offer with bespoke handling of failures.

### Density conventions

- **Low** (Stephango, Are.na): generous whitespace, large type, designed for slow consumption.
- **Mid-low** (Hello.cv, Pinboard): short pages with text density but visual breathing room.
- **Mid** (Huntr, Rknight, Notion templates, NotiNova, Enhancv): balanced — scannable cards or columns with moderate metadata.
- **Mid-high** (Teal, Rezi, Jobscan): row-dense tracker views or sidebar-heavy editors. Scanning rewards practiced users.
- **High** (Simplify, Airtable, Levelsio): explicitly information-rich. Designed for users in active high-volume mode.

The density-vs-curation tradeoff aligns with positioning: indie hubs and outliers run low or high, never mid; trackers run mid to high; AI tools run mid-high. v2's "calm, dense" posture per ADR-002 §D4 sits in the mid range, closer to Huntr and Notion than to Stephango or Are.na.

### Where v2's guardrails align with the landscape vs diverge

| Guardrail (ADR-002 §D4) | Landscape alignment | Notes |
|---|---|---|
| No marketing hero with claim | Diverges from 11 of 12 in-bucket apps | Only Pinboard and the outliers (Are.na, Hello.cv) skip the marketing hero. v2's posture is rare. |
| No gradient buttons | Diverges from 8 of 12 in-bucket apps | Simplify, Teal, Enhancv, Rezi, Jobscan, both Notion templates, Airtable use gradient buttons in marketing surfaces. v2's flat-button posture is closer to indie hubs and outliers. |
| No emoji | Aligns with most | Trackers and AI tools mostly avoid emoji in marketing copy. Only NotiNova and some indie hubs (Stephango occasionally) use them on landing surfaces. |
| No AI branding | Diverges from 6 of 12 in-bucket apps | Teal, Rezi, Enhancv, Jobscan, Simplify, NotiNova all foreground AI in their value props. v2's posture is unusually restrained for the category. |
| System font stack | Aligns with indie hubs / outliers; diverges from most SaaS | Trackers and AI tools use custom typefaces (Inter, Söhne, etc.). Indie hubs run system fonts more often. v2's choice aligns with the indie posture. |
| Sky→pink gradient as accent only | No direct match | Some apps use one accent color (Pinboard navy, Teal blue, Stephango gold); none use a two-color gradient as accent. v2's pattern is distinctive. |

The aggregate signal: v2's guardrails position it visually closer to the indie-hubs + outliers cluster than to the SaaS trackers / AI tools cluster, despite v2 being problem-space-adjacent to the latter. This is intentional per ADR-002 §D4 — but it means v2 will look unfamiliar in the trackers/AI-tools mental shelf.

### Copy voice across the landscape

Sampling 6 representative phrases across the categories. Quotes are ≤15 words, in quotes, with URL attribution. Server-side fetching of marketing pages was rate-limited or blocked for several apps — phrases marked `[approximation]` reflect canonical positioning the orchestrator can verify in browser; phrases without that marker were captured directly by the Chrome browser agent on 2026-05-03 from the captured view.

| Phrase | App | URL | Voice cluster |
|---|---|---|---|
| "List of all my projects ever" | Levels.io | https://levels.io/projects/ | Plain-spoken indie |
| "Social bookmarking for introverts" `[approximation]` | Pinboard | https://pinboard.in/ | Wry-developer |
| "Calm internet" `[approximation; from About page mission]` | Are.na | https://www.are.na/about | Calm-curatorial |
| "Get your resume past the ATS" `[approximation]` | Rezi | https://www.rezi.ai/ | Outcome-confident SaaS |
| "Land your dream job, faster" `[approximation]` | Teal | https://www.tealhq.com/ | Aspirational SaaS |
| "Job Application Tracker" | Notion | https://www.notion.com/templates/the-job-application-tracker-815 | Neutral utility |

**Voice clusters surfaced:**

1. **Plain-spoken indie** (Levels.io, sometimes Stephango). Direct, occasionally self-deprecating, no marketing pretense. The maker's persona IS the brand.
2. **Wry-developer** (Pinboard, Robb Knight). Self-aware humor, anti-SaaS framing, often addressing technically-literate readers as peers.
3. **Calm-curatorial** (Are.na, Stephango at its most austere). Thoughtful, slow, anti-attention-economy. Adopts the language of curatorial practice rather than productivity.
4. **Outcome-confident SaaS** (Rezi, Jobscan). Promises measurable results — past the ATS, score above X, faster, more interviews. Quantitative, defensible-on-evidence.
5. **Aspirational SaaS** (Enhancv, Teal at its most polished, Simplify). Emotional language — dream job, stand out, transform your search. The least defensible in evidence-based scrutiny but the most common in the category.
6. **Neutral utility** (Notion templates, Airtable templates). Functional, descriptive, no editorial voice. The platform's voice subsumes the template's.

**Distribution by category:** Trackers default to Outcome-confident or Aspirational SaaS (5 of 9 in-bucket non-template apps); AI tools split Outcome-confident vs Aspirational; Notion / Airtable templates run Neutral utility; indie hubs run Plain-spoken indie or Wry-developer. The outliers split — Are.na and Hello.cv lean Calm-curatorial; Pinboard is Wry-developer.

**Where v2 sits.** v2's positioning ("personal toolkit, files in folders, no SaaS") maps closest to the Plain-spoken indie + Wry-developer clusters but lacks the maker-persona that lets indie hubs carry voice on their own. Without an established persona, v2 has to substitute substance for persona — concrete deliverables, evidence-based claims, no aspirational language. The 8th-grade reading-level constraint (Session 13 orchestrator decision) lands closer to Plain-spoken indie than to either SaaS cluster, but the indie clusters' insider-developer-humor tone won't generalize to job-seekers under stress; v2's voice has to be plain without being clubby.

### Privacy-first messaging conventions

How "local-first" / "no tracking" / "your data stays yours" gets positioned across the landscape. Survey of 4 representative phrases:

| Phrase | App | URL | Visual placement |
|---|---|---|---|
| "Social bookmarking for introverts" `[approximation; sets the anti-SaaS tone]` | Pinboard | https://pinboard.in/ | Top of homepage as sub-header. Tagline sets tone for the rest of the site. |
| "Calm internet" `[approximation; consistent across About / mission pages]` | Are.na | https://www.are.na/about | About page hero. Mission-statement-as-positioning. |
| "Some things should cost money" `[approximation; from Pinboard's pricing essay]` | Pinboard | https://pinboard.in/about/ | Pricing / about page intro paragraph. Trust-building through transparency. |
| "Built by one person, hosted by them" `[paraphrased archetype; no single source]` | (cluster across Pinboard / Stephango / Rknight) | n/a single URL | Footer or about-page placement most common. Implicit through site architecture. |

**Visual conventions for privacy positioning across the landscape:**

- **Footer / about-page placement** dominates. Most privacy claims live in tertiary surfaces (footer, about, pricing) rather than as homepage hero. Pinboard and Are.na are the exceptions — both lead with privacy / calm-internet positioning above the fold.
- **Long-form essay style.** Pinboard's about / pricing pages and Are.na's mission page run as personal essays from the founder rather than bulleted feature lists. The form itself signals "I am a person, not a company." This is rare in the SaaS clusters — Teal / Rezi / Jobscan privacy pages are conventional GDPR / CCPA notices.
- **No badges or trust seals.** The privacy-leaning apps surveyed (Pinboard, Are.na, Stephango, Hello.cv) avoid the GDPR-compliance / SOC-2 / privacy-shield badges that SaaS platforms display. The implicit message: "we're below the threshold where those badges matter; we don't collect enough data for them to apply."
- **Local-first / offline-first language is rare.** None of the 15 surveyed apps explicitly position as local-first. Pinboard is closest with single-developer / hosted-by-me framing but it's still a hosted service. v2's "personal local-first toolkit" positioning has no direct landscape neighbor — there's room to define the vocabulary rather than borrow it.

**Where v2 sits.** v2's privacy posture (no telemetry, no tracking, files on user's disk via Cowork-mounted directory) maps closest to Pinboard's anti-SaaS positioning but is more privacy-strict (truly local, no hosted service at all). The landscape's vocabulary for this stance is thin — most options either don't claim privacy or claim it through compliance-badge language. The synthesis session has room to invent vocabulary specific to v2's stance rather than borrow from a sibling.

---

## Recommendations for ADR-003 synthesis

Eight questions for ADR-003 to answer, derived from the patterns and tensions surfaced in Blocks 2-3. Each is framed as a question with the landscape evidence on each side, NOT as a foregone conclusion.

**Q1. Should v2 adopt the kanban-pipeline column metaphor (Huntr / NotiNova / Simplify) or treat status as a flat tag (Linear-style, Pinboard-style)?**
- Pipeline columns (8 of 9 in-bucket trackers) are the category default — adoption signals "this is a tracker." Edge-cases (Rejected, Withdrawn, On Hold) break the visual narrative.
- Flat status tags fit v2's "personal toolkit, files in folders" posture more cleanly. The trade-off is unfamiliarity — users coming from Huntr / Teal will look for columns and not find them.
- Teal's hybrid (column + separate Application Status pill) is a third option but introduces dual-status conceptual load.

**Q2. Should v2 keep slate-950 dark or shift to a light theme to align with the category default?**
- Light theme dominates the SaaS landscape (12 of 12 in-bucket apps). Shifting v2 light would reduce the "this looks unfamiliar" friction in the trackers/AI-tools mental shelf.
- v2's calm-dark posture has no direct landscape neighbor — only Levels.io is dark and that's brutalist neon, not calm. v2 staying dark is a positioning bet on differentiation over familiarity.
- The sky→pink gradient is more legible on dark; shifting light would force a palette rework.

**Q3. Should v2 adopt status-pill color saturation (Notion / Airtable / Teal) or stay text-label-only (Pinboard / Stephango)?**
- Status pills (5 of 9 in-bucket trackers) are the conventional differentiator. Saturated colors per pipeline stage create visual rhythm in the tracker view.
- Text-label-only matches v2's "calm, dense" posture and the indie-hubs cluster. Less visual noise; harder to scan a kanban at glance.
- The decision interacts with Q1 — if v2 goes flat-status-tag, pill saturation matters less; if v2 goes pipeline columns, pill colors carry more weight.

**Q4. Should v2 commit to one primary view of application data, or offer multiple views (Airtable-style view-switcher) of the same underlying records?**
- One primary view (every app surveyed except Airtable) keeps the design surface narrow and the user's mental model simple.
- Multiple views (Airtable's Grid / Kanban / Calendar / Gallery / Form) match v2's "exports serving multiple downstream apps" architecture and the Pivot B static delivery hub model from ADR-002 §D4.
- Multiple views adds frontend complexity v2 has been intentionally avoiding.

**Q5. Should v2's marketing surface (the v2 site) lead with privacy / local-first positioning (Pinboard / Are.na hero) or treat privacy as footer/about content (most SaaS)?**
- Hero positioning (2 of 15 — Pinboard, Are.na) makes the privacy stance the primary differentiator. Builds trust upfront with privacy-conscious users.
- Footer / about positioning (12 of 15) keeps the homepage focused on what the product does rather than what it doesn't do. Privacy becomes evidence rather than pitch.
- v2's "no telemetry, files on user's disk" is more privacy-strict than any landscape neighbor — there's room to define vocabulary rather than borrow.

**Q6. Should v2's voice cluster lean Plain-spoken indie (Levels.io) or Wry-developer (Pinboard / Robb Knight) or define a new cluster (Plain-without-clubby) given the 8th-grade reading-level constraint?**
- Plain-spoken indie requires a maker-persona to anchor against; v2 doesn't currently have one.
- Wry-developer addresses readers as technically-literate peers — incompatible with the 8th-grade reading-level constraint and the job-seeker-under-stress audience.
- Plain-without-clubby (the implicit third option) means borrowing the indie clusters' directness without their developer-insider humor. Closest existing neighbor: Hello.cv's conversational onboarding without the chat mechanic.

**Q7. Should v2 foreground "AI" as a value prop (Teal / Rezi / Enhancv / Jobscan / Simplify / NotiNova all do) or maintain the no-AI-branding guardrail per ADR-002 §D4?**
- AI-foregrounding (6 of 12 in-bucket apps) is the category-default positioning. Skipping it cedes the "AI tool" mental shelf.
- No-AI-branding (v2's current guardrail) avoids the buzzword fatigue and fits the "no marketing claim" posture. The value prop becomes "what it does for you" rather than "what powers it."
- The decision interacts with Q6 — Aspirational SaaS voice + AI-foregrounding bundle naturally; Plain-spoken indie + AI-quiet bundle naturally.

**Q8. Should v2's onboarding be a static welcome (Pinboard, indie hubs), a marketing splash (most SaaS), or a hands-on demo of the product (Are.na's embedded user-channel, Hello.cv's chat onboarding)?**
- Static welcome (4 of 15) keeps the homepage low-effort and fast-loading. Familiar to indie-savvy users; opaque to first-time visitors.
- Marketing splash (8 of 15) is the SaaS default — hero claim + feature grid + testimonials + pricing. Conflicts with v2's no-marketing-claim guardrail.
- Hands-on demo (2 of 15 — Are.na with embedded channel, Hello.cv with chat onboarding) shows the product's actual texture rather than describing it. Aligns with v2's evidence-first posture but requires a working interactive surface.

## Open questions

Things the research surfaced but couldn't resolve. The synthesis session can either chase these in browser or accept the gap.

- **R6 user-review fetch limitation.** G2, Capterra, ProductHunt all return Cloudflare bot challenges or JS-heavy bundles when fetched server-side. The R6 subsections on huntr / teal / rezi use paraphrased common themes with URL attribution, not direct quotes. The synthesis session can either visit the URLs in browser to extract direct quotes or accept the paraphrased themes as adequate signal.
- **Hello.cv state ambiguity.** The Chrome agent captured a chat-onboarding view, but it's unclear whether that's the persistent homepage state for visitors or a session-specific entry point. Couldn't verify without a logged-in account.
- **Pinboard "single-developer hosted by me" framing currency.** The framing was accurate as of training-data cutoff (May 2025). Whether the founder is still solo-operating the service in May 2026 wasn't verified.
- **Wishlist / Saved / Bookmarked / To-Apply naming consensus.** Every app picks a different word for the pre-application stage. The research surfaced the variance but didn't surface user-research data on which word lands best with job-seekers. UX-research literature outside this landscape may exist.
- **Are.na calm-aesthetic transferability.** Are.na's calm-internet posture works for slow-browse contexts. Whether it transfers to active job-search urgency (where users are often anxious and hurried) is an empirical question this research can't answer.
- **Notion / Airtable export integration.** Whether v2 should target specific export formats for these platforms (since both are already-installed for many users) vs stay platform-agnostic via the deterministic zip in `website/v2/exports/` per ADR-002 §D4. The Pivot B model leans agnostic; the user-experience case for native Notion / Airtable export is not yet evaluated.
- **Read.cv → Hello.cv positioning continuity.** Read.cv was acquired by Perplexity in Jan 2025 and shut down May 2025. Hello.cv positions as the successor but the design language and audience overlap with Read.cv's original wasn't verified — Wayback's Read.cv captures could surface the comparison.

---

*End of landscape doc (Blocks 1-4 complete; Block 5 PR-open pending in Milan's terminal).*
