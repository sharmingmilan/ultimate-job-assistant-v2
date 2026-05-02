# memory.md -- Milan Sharma
# Location: /Users/Milan/Documents/Claude/Job Assist/memory.md
# Last updated: 2026-04-08

---

## About Milan

- **Name**: Milan Sharma
- **Location**: Culver City, CA
- **Email**: msharm406@gmail.com
- **LinkedIn**: linkedin.com/in/msharm/
- **Education**: BS Managerial Economics, UC Davis (2018)
- **Current role**: Data Analyst III at Apple (September 2025 -- present)
- **Experience**: 6+ years across Apple, Pinterest, Wells Fargo, Nike, Disney
- **Core stack**: SQL (advanced), Python, Snowflake, Tableau, Power BI, Claude AI/LLM tooling

---

## Work Style & Preferences

- **Resume philosophy**: Concise bullets with metrics. Leave the stories for the interview. "I glance at notes and talk candidly."
- **Formatting rules** (enforced on all resume outputs):
  1. No hyphens, en dashes, or em dashes as sentence punctuation. Restructure or use commas.
  2. Contact line must fit on one line. Use `github.com/` not `https://github.com/`.
  3. No empty spacer paragraphs between bullets within a company section. Bullets evenly spaced.
  4. One empty spacer line between each company section (before the company header table).
  5. One empty spacer line before the SKILLS section header.
  6. "Skills:" prefix bold; skill list itself not bold.
  7. Preserve the base resume's table-based layout for company headers (company | date, title | location).
  8. All bullet content must come from the base resume or verified stories in memory.md. No fabrication.
- **Cover letter signature**: "Sincerely,\nMilan"
- **Tone**: Neutral, professional. Milan adapts to his own voice -- doesn't want scripts.
- **Job search pattern**: Batch applies but customizes each resume. Has multiple base resumes for different role types (data analyst, data engineer, analytics manager, etc.).
- **Networking comfort**: Low -- rarely does outreach but is open to coaching. Knows the difference between genuine and spammy outreach intuitively.
- **AI adoption**: Self-directed. Built AI workflows at Apple without being asked -- org-wide GitHub, semantic layer, biweekly training sessions. Comfortable with Claude Code, agentic workflows, skills architecture.

---

## Communication Preferences

- **Mode selection**: Infer from context, confirm with a quick check. No formal toggle menus or excessive options.
- **Updates/changes**: Always proposed, never auto-applied. Dual-layer format: quick summary to skim + detailed changes underneath if he wants to verify.
- **Questions**: Prefers focused, one-at-a-time discussion. Likes to go deep on each topic before moving on.
- **Feedback style**: Direct and concise. Will say "looks good" when satisfied, gives specific callouts when something needs changing.
- **Progress tracking**: Does not want tracker.md status updated automatically. Always ask before marking steps complete. At end of a position's lifecycle, ask whether to move files to archive/.

---

## Key Stories & Experience (for resume targeting)

These are stories surfaced during Q&A sessions. Reuse across applications where relevant.

### Nike -- Studio Scheduling Optimizer
Complex SQL project joining product, sizing, model availability, crew, equipment, and production bay datasets to optimize weekly photo shoot schedules. Resolved resource constraints. Output fed into Tableau dashboards, referenced in daily standups, improved production forecasting.
**Good for**: Production operations, resource optimization, cross-functional data, SQL at scale.

### Apple -- Data Integrity Pushback
Discovered Spend FY/QTR fields weren't mapping correctly, cascading into LOB and function reporting errors. Budget managers asked to hardcode a fix. Milan pushed back -- naming convention had changed upstream without being communicated downstream. Drove correction at the source and initiated upstream auditing for consistency. Faced pressure from non-technical team to ship the quick fix, but framed the conversation as SME educating on root-cause vs. one-off fixes, explaining that hardcoding would only address the symptom and similar issues would recur. Pros/cons framing got the point across.
**Good for**: Courage/candor, data quality ownership, systemic thinking, pushing back constructively, measurement rigor (Waymo safety analog).

### Apple -- Weekly ETL Ownership
Owns a high-priority weekly ETL pipeline that 12 people depend on. Requires 4-7 hours of manual SQL execution due to complex edge cases. Built AI automations and scheduled data refreshes to compress cycle time, freeing capacity for strategic ad hoc requests.
**Good for**: Reliability, prioritization, automation mindset, balancing recurring and ad hoc work.

### Apple -- Self-Directed AI Initiative
Given access to an internal AI CLI with vague mandate. Found no documentation on individual processes. Initiated standardized documentation, created org-wide GitHub, researched AI architecture, planned semantic layer. Now the team shares skills/agents via GitHub. Leads biweekly training sessions and Q&A.
**Good for**: Curiosity, self-direction, team enablement, AI adoption leadership.

### Apple -- Stakeholder Redirection
Stakeholder wanted an Excel pivot. Milan proposed a Tableau dashboard with structured layout (KPIs up top, drill-down bar chart, cumulative quarterly view). Also regularly pushes back on over-engineered requests by suggesting simpler processes that deliver the same output.
**Good for**: Judgment, stakeholder management, knowing when a better tool exists.

### Apple -- KPI Definition & Governance
Defined shared procurement reporting parameters across the analytics team — clarified whether to include all PRs generated vs. only finalized/pending, ensuring consistent metric interpretation across business lines. Documented definitions in Confluence pages and maintained data dictionary in Box folders where all procedures lived. Built governance infrastructure, not just a one-time fix.
**Good for**: Data governance, metric standardization, cross-team alignment, KPI design and governance (Waymo "design, define, and govern KPIs").

### Wells Fargo -- Self-Service Funnel Analysis
Connected call center logs to a parameterized SLA time-series dataset in Redshift to map exactly where customers abandoned the self-service cycle and escalated to the help desk. Identified specific drop-off points, reduced help desk call volume 20%, increased self-service completion 12%.
**Good for**: Product analytics, user journey analysis, behavioral data, measurable outcome, fintech/financial services.

### Pinterest -- Desk Sensor Cross-Validation
Desk sensors reported full capacity but badge data showed otherwise. Investigated and found recurring Pinterest meetings/events brought 100+ external attendees who used any available desk/room. Built a workplace capacity dashboard enabling the team to proactively plan around event-driven demand spikes.
**Good for**: Data quality, instrumentation validation, cross-source reconciliation, product/workplace analytics.

### Disney -- Digital Asset Regression & Bundling Strategy
Noticed a gap in reporting of digital asset sales — vendors weren't reporting timely. Proactively backfilled 2+ years of missing vendor-reported sales data. That dataset became integral to the organization. When COVID hit, having that historical baseline was crucial for measuring trends and forecasting because without the backfill they'd have had no pre-pandemic comparison data. Discovered digital assets sell better when an IP has a content release (TV show, movie, or trailer). Regression analysis (dimensional modeling and relational modeling, Python-heavy execution, SQL for querying structured tables ingested by Python scripts) showed bundled same-IP products consistently outperformed individual items. Shifted marketing meetings to incorporate bundling strategy aligned with content release calendars.
**Good for**: Strategic insight, regression analysis, proactive problem identification, foresight, media/entertainment, data driving business decisions, IP analytics, analytical modeling methodology.

### Apple + Wells Fargo -- Knowledge Sharing & Best Practices
At both companies, partnered with directors to hold office hours and schedule biweekly meetings to deep-dive into business processes and topics for knowledge sharing. Pattern across two companies, not a one-off.
**Good for**: Culture of excellence, establishing best practices, team enablement, leadership without authority.

---

## Design Principles (for this project)

- **No fabrication** -- all company claims sourced and cited with credible sources
- **Human-in-the-loop** -- nothing auto-generated without approval
- **Specific over vague** -- metrics, tools, outcomes in every bullet
- **Plug-and-play** -- skill logic separated from user data so repo is forkable
- **Doc freshness** -- propose updates at end of every session
- **Modular skills** -- each skill standalone, orchestrator chains them
