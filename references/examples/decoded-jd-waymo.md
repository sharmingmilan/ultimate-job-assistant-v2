# decoded-jd.md -- Waymo Business Intelligence Analyst
# Decoded: 2026-04-08 | Mode: Deep

---

## Must-Have Requirements

| # | Requirement | Source | Evidence in JD |
|---|-------------|--------|----------------|
| 1 | SQL — complex data pipelines, advanced querying | Explicit | "Coding experience with Python and SQL to design and implement complex data pipelines following best practices" |
| 2 | Python — data pipeline design and implementation | Explicit | Same line as above |
| 3 | 3+ years in a related technical field | Explicit | "3+ years of experience in a related technical field or equivalent practical experience" |
| 4 | Statistical knowledge and data intuition | Explicit | "Statistical knowledge/data intuition" |
| 5 | Experience presenting to / interacting with senior leadership | Explicit | "Experience interacting with senior leadership" |
| 6 | Ambiguity scoping — structure and solve open-ended problems independently | Explicit | "Ability to scope, structure, and solve ambiguous problems independently" |
| 7 | Report and visualization building | Explicit | "build the right reports and visualizations to drive insights" |
| 8 | Cross-functional partnership (PM, Engineering, Program Management) | Explicit | "Partner with Product Managers, Engineers, Program Managers" |
| 9 | Data pipeline ownership (build + maintain) | Explicit | "Build and maintain state of the art reporting infrastructure to enable continuous decision making" |
| 10 | Advanced analytical modeling | Explicit | "Perform advanced analytical modelling as necessary to help drive the right decisions" |

---

## Nice-to-Have Requirements

| # | Requirement | Source | Notes |
|---|-------------|--------|-------|
| 1 | AV / Mapping / Ridesharing / Consumer Tech / People Analytics experience | Explicit | Stated as "We Prefer" — not a hard filter |
| 2 | GCP / BigQuery | Implicit [HIGH] | Google subsidiary, Product Data Science team — GCP is the default stack |
| 3 | Looker or similar BI tool | Implicit [HIGH] | BI analyst role at a Google company, Looker is Google's BI product |
| 4 | dbt or similar data modeling tool | Implicit [MED] | "best practices" for pipelines often implies dbt in modern data stacks |
| 5 | A/B testing / experimentation | Implicit [MED] | "advanced analytical modelling" + DS team context implies experimentation familiarity |

---

## Implicit Expectations

These aren't stated in the JD but are strongly implied by context, company culture, and role framing:

| Expectation | Confidence | Evidence |
|-------------|-----------|---------|
| Mission alignment — safety, long-term thinking over short-term wins | [HIGH] | Waymo's core identity is safety-first AV. Glassdoor reviews and interview guides emphasize cultural fit on this dimension. |
| Rigor over speed — comfortable slowing down when data is incomplete | [HIGH] | Autonomous vehicles require high-stakes decision-making. Interview process specifically tests for "transparency in reasoning when data is ambiguous." |
| Metric definition ownership, not just execution | [HIGH] | "identify the right measurement for business performance" — they're not handing you a metric sheet, you're defining it |
| Working with novel, ambiguous datasets (AV telemetry, simulation data) | [MED] | "rich business and operational context across the entire product landscape" — this is not standard product analytics |
| Strong written/verbal communication to non-technical partners | [MED] | Cross-functional partnership listed first; "drive insights" framing implies communication is as important as analysis |
| Culture of intellectual curiosity and openness to new information | [MED] | JD literally says "We are data-driven, curious, open-minded, and adapt quickly to new information" — this is a values statement |
| Comfort with Google-style engineering culture (code reviews, PR best practices) | [MED] | "following best practices" for pipelines at a Google subsidiary implies code-level quality standards |

---

## Red Flags

| Flag | Confidence | Notes |
|------|-----------|-------|
| Operations team culture issues (Glassdoor) | [MED] | Several reviews mention toxic Operations culture. Product Data Science team is likely different but worth noting. |
| Management rated 3.3/5 on Glassdoor | [MED] | Below average. Cross-reference: 77% recommend overall, so this may be team-specific. |
| Hybrid role — requires SF Bay Area proximity | [LOW] | Milan is in Culver City. Not a dealbreaker but worth confirming relocation/commute expectations. |

---

## Key Themes

1. **Data pipeline ownership at scale** — This isn't a reporting role. You're building the infrastructure that enables decision-making, not running reports on top of it.

2. **Metric definition and rigor** — Waymo's BI challenge is unusual: how do you measure "is the car driving safely" in a way that drives product decisions? Whoever can think carefully about measurement will stand out.

3. **Cross-functional breadth** — Engineering, Product, Operations, Program Management. This role is a connective tissue role, not a siloed analyst seat.

4. **Mission/safety alignment** — Cultural fit is tested explicitly in interviews. Candidates who understand why autonomous vehicle analytics is different from standard product analytics (stakes, validation rigor, incomplete data) will land better.

5. **Advanced modeling + infrastructure combo** — "Advanced analytical modelling" combined with "data pipelines" means they want someone who can both build the plumbing and run the analysis.

---

## Fit Assessment

**Overall**: Strong — with one gap to address.

**Strengths:**
- SQL complexity: Milan's Apple ETL pipeline (4-7 hrs/week, 12-person dependency, complex edge cases) and Nike scheduling optimizer (6+ dataset joins) demonstrate exactly the pipeline depth this role requires
- Cross-functional partnership: consistent across all roles
- Senior leadership interaction: Apple experience
- Statistical reasoning: Disney regression + bundling strategy, Wells Fargo funnel analysis
- Python: present in skills, used for automation at Apple
- Ambiguity scoping: Apple AI initiative (vague mandate, no documentation, built from scratch)
- Curiosity/self-direction: directly maps to Waymo's stated values

**Gap:**
- No AV/GCP/BigQuery experience. The "We Prefer" is a soft preference, not a hard filter — but it's worth addressing in the resume with any cloud/data engineering signals.
- No direct exposure to Looker (has Tableau and Power BI which are comparable)

**Authentic connection:**
- Milan's Apple safety/rigor story (data integrity pushback — drove upstream correction instead of hardcoding) is a direct analog to Waymo's "rigor over speed" culture signal
- Self-directed AI initiative at Apple maps to Waymo's curiosity/open-mindedness values
