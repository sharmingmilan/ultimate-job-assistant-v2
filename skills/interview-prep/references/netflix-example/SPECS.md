# SPECS.md — Netflix SQL Prep

Product specification for the study app. This file documents *what* the product is, *why* it is that way, and *what it is deliberately not*. For implementation details, directory structure, and build pipeline, see CLAUDE.md.

---

## 1. Purpose

A single-user, offline-capable study tool that prepares one candidate for one specific interview (Netflix Data Analyst, Production Finance Operations & Innovation, JR38497) over a ~7-day window.

The app's job is not to teach SQL from scratch. Its job is to **re-activate, stretch, and make durable** the SQL and pandas skills Milan already has, using retrieval-based practice over realistic Netflix-flavored problems.

---

## 2. User and context assumptions

- **User** has prior SQL exposure (intermediate — can write joins and subqueries unaided) and some pandas (beginner-to-intermediate). Is not a total beginner.
- **Device.** Primary study device is an iPhone (via Safari "Add to Home Screen"), secondary is a laptop. UI must work at 375px width and desktop width without separate codepaths.
- **Time budget.** ~1 hour per day for ~7 days. Not enough time to grind an arbitrary course; every minute needs to be high-leverage.
- **Exam conditions.** 45–60 minute CoderPad session. ~4 SQL problems + 1 Python problem. No autocomplete, no syntax check. Must verbalize reasoning while typing.
- **Target dialect.** Presto / Trino (Netflix's warehouse engine). Postgres-style DATE arithmetic is closely compatible and is the app's default; dialect notes appear where behavior diverges.

---

## 3. Pedagogical model

### The core claim

Durable skill in SQL under time pressure comes from **retrieval practice with spaced, interleaved variation** — not from reading, watching videos, or re-copying solutions. The app is built around this claim.

### Three-phase learning flow per topic

Each of the 11 topics presents content in a fixed sequence:

**Phase 1 — Came (worked examples).** The learner sees three progressively harder complete solutions (easy, medium, hard) with:

- A natural-language prompt grounded in a Netflix Production Finance scenario
- A schema panel (column names + sample rows) for every referenced table
- The full SQL (or Python) solution
- A **numbered walkthrough of 6–10 bullets** explaining not just what the code does but *why each construct was chosen* (e.g., "ROW_NUMBER not RANK because we want exactly 3 per group even with ties")
- After the first worked example only, an italic prompt to self-explain the solution in one's own words

**Phase 2 — Saw (faded practice).** Same three prompts reappear, but each solution has strategic blanks (`_____`) inserted at the points where learners most often go wrong (join type, window function choice, NULL-aware operator, threshold constant, etc.). Learner fills the blanks in a plain textarea; the full solution is available on tap.

**Phase 3 — Conquered (retrieval).** The learner gets three new prompts (easy/medium/hard) with schema panels but **no scaffolding**. A full SQL editor lets them type and test their recall freely. Solutions are hidden until tapped.

### Why this specific order

This maps to **worked-example → fading → retrieval**, the sequence Renkl (2014) identifies as optimal for complex problem-solving domains. The effect is:

- Worked examples **reduce cognitive load** on the initial encode (Sweller 1988) so the learner's brain can focus on the reasoning, not on generating syntax
- Fading **gradually shifts** cognitive load back to the learner as competence grows (Atkinson et al. 2003)
- Retrieval **stamps in** long-term memory (Roediger & Karpicke 2006) by forcing active recall

### Evidence-based strategies and their manifestations

| Strategy | Source | Where it appears |
|---|---|---|
| Retrieval practice | Roediger & Karpicke, 2006 | Conquered phase: blank editor, no crib |
| Worked examples | Sweller & Cooper, 1985 | Came phase: complete solutions up front |
| Fading | Renkl, 2014; Atkinson et al., 2003 | Saw phase: blanks at common-error points |
| Interleaving | Rohrer, 2012 | "Interleave" mode shuffles problems across topics |
| Spacing | Cepeda et al., 2006 | Review scheduling for flagged problems |
| Dual coding | Paivio, 1971; Mayer, 2009 | Schema panels render visual tables alongside prompts |
| Elaboration | Chi et al., 1994 | "Explain back to yourself" prompts; self-explain seeds |

These citations are surfaced in the app footer so the user can independently verify the approach.

### Spacing and interleaving policy

- **Interleave mode** (toggleable in the top nav) pulls from the full retrieval-problem pool across all 11 topics. Order is Fisher-Yates shuffled with a topic-spread constraint: no two consecutive problems come from the same topic.
- **Spaced review.** Problems can be flagged for review; flagged problems resurface after a cooldown (initially 1 day, lengthening on each correct pass).
- **Topic progress** ("0/3 completed") is shown per topic but does not gate access — the user can revisit Came / Saw / Conquered in any order.

---

## 4. Content inventory

### Topic list (11 topics, 33 retrieval problems, 33 worked examples, 33 faded scaffolds)

| # | Topic | Tier | Frequency signal |
|---|---|---|---|
| 1 | Multi-Table Joins | T1 | Appears in every SQL interview |
| 2 | Window Functions | T1 | Very common — ranking, running totals, period-over-period |
| 3 | CTEs & Query Structure | T1 | Signals senior-level code organization |
| 4 | Date Manipulation | T1 | Fiscal periods, rolling windows, durations — constant in finance ops |
| 5 | Deduplication | T1 | Core skill — vendor name normalization, fuzzy dup detection |
| 6 | CASE & Conditional Aggregation | T1 | Bucketing, pivoting, flag composition |
| 7 | NULL Handling | T1 | Every messy dataset has them; NULL semantics trip even experienced candidates |
| 8 | FULL OUTER JOIN & Reconciliation | T2 | Production Finance Ops often compares two systems (AP vs HUB) |
| 9 | Self-Joins | T2 | Intervals, overlaps, first/last-per-group |
| 10 | Set Operations | T2 | UNION / INTERSECT / EXCEPT for snapshot diffs and DQ |
| 11 | Pandas — the 1 Python question | PY | groupby, merge, rolling, date-range reindex |

### Difficulty calibration per topic

- **Easy.** Single table or one join, one or two clauses, direct aggregation or filter. Target: candidate can write in <5 min without hesitation.
- **Medium.** 2–4 joins or CTEs, window function with partition + order, conditional aggregation, or date boundary logic. Target: 10–15 min with some thinking time.
- **Hard.** 4+ CTEs, layered windowing (e.g., LAG over rolling avg), NULL-aware boolean logic, or reconciliation with tolerance. Target: 20+ min; in an interview, candidate should scope, clarify, then code.

### Domain vocabulary the content teaches

The prompts and solutions deliberately surface Netflix Production Finance terms:

- **ATL / BTL** (Above-the-Line / Below-the-Line crew cost categorization)
- **1099 vendor** (U.S. tax form for independent contractors)
- **SAP AP** (Accounts Payable extract from SAP)
- **HUB ledger** (fictional name for a 2nd system used for reconciliation scenarios)
- **Burn rate, burn acceleration** (spend velocity metrics)
- **Fiscal month / fiscal-month-close**
- **Shoot days, principal photography dates**
- **Concentration risk** (vendor over-exposure on a single production)
- **Composition flag** (ATL-heavy vs vendor-heavy vs balanced spend composition)
- **Tentpole / micro / mid / major** (production budget tier conventions)

This vocabulary is a strategic side-effect: if the candidate uses these terms naturally in the interview, it signals domain fit.

---

## 5. UI and interaction specification

### Top-level navigation

- **Left sidebar:** topic list with 11 items, progress indicator ("0/3") per topic, highlighted current topic. Collapses on mobile.
- **Top nav:** mode toggle (Learn / Interleave), global progress counter, schema-reference shortcut ("ALL TABLES ▶").
- **Main panel:** current topic's three-phase flow with section headers (Came / Saw / Conquered).

### Schema panel

Every prompt that references tables shows a compact grid of those tables. Each table shows column names and 3–5 realistic sample rows. Sample rows are **consistent across panels** — vendor V001 "ACME Post Production" appears in multiple topics so the user builds a mental model of one coherent dataset.

### SQL editor

- Transparent `<textarea>` layered over a syntax-colored `<pre>`
- Keyword (pink), function (cyan), string (green), number (amber), comment (gray)
- Tab = 2 spaces; Shift+Tab unindents
- Auto-indent on Enter preserves prior-line leading whitespace
- Per-question persistence via `localStorage` under key `netflix_sql_prep_q_{topicId}_{difficulty}`

### Learn mode vs Interleave mode

- **Learn mode** walks topic-by-topic in order. This is what you do on days 1–4.
- **Interleave mode** pulls one problem at a time from across all topics in shuffled order with topic-spread. This is what you do on days 5–7. It simulates interview conditions by forcing context-switching.

---

## 6. Content authorship guidelines

The following rules governed how every problem was authored. Future edits should follow them.

### Every worked example must

- Have a prompt that states both the mechanical ask ("return X for each Y") **and** the business motivation ("...to flag vendor concentration risk")
- Include a schema panel for every referenced table
- Present a solution that actually runs in Presto/Trino (or Postgres, which is close enough); no pseudo-SQL
- Be accompanied by 6–10 walkthrough bullets that explain **choices**, not just code. Prefer "I used INNER JOIN here because orphan payments should drop out" over "This is an INNER JOIN."

### Every faded scaffold must

- Reproduce the worked example's SQL with 4–8 strategically placed `_____` blanks
- Blank out the things learners most often get wrong: join type, aggregate function, NULL operator (`IS NULL` vs `= NULL`), window function choice, threshold literals, order keywords
- Not blank the obvious or trivial (formatting, aliases, ORDER BY direction on the outer query)

### Every retrieval problem must

- Be genuinely solvable without the worked example visible
- Have a `selfExplain` seed question ("Why did I choose a LEFT JOIN here?") to scaffold elaboration
- Include an `explanation` paragraph for post-attempt self-check
- Scale in cognitive demand: easy (~5 min), medium (~15 min), hard (~20 min)

### Problems should be realistic, not contrived

If a problem is just "find the 3rd highest salary" it gets discarded. Every problem is sourced from a real production-finance scenario: vendor deduplication, monthly close rollups, burn-rate tracking, AP-vs-HUB reconciliation, crew assignment conflict detection.

---

## 7. Non-goals and deliberate omissions

The app does **not**:

- **Execute the user's SQL.** No DB backend. The editor is for typing and thinking; the user self-checks against the provided solution. A live executor would need a backend and materially changes the threat model (credentials, rate limits, costs).
- **Track time per problem.** Timers add pressure that interferes with learning; pressure belongs in the interview, not in practice.
- **Have spaced-repetition with SM-2 or Anki-level fidelity.** A simple flag-and-cooldown is sufficient for a 7-day horizon; full SRS is over-engineered.
- **Support multiple users.** No accounts, no sync, no sharing. One device, one learner.
- **Teach SQL from first principles.** There is no "what is a JOIN" introduction. The content assumes working SQL familiarity.
- **Cover ML/stats interview topics.** The job description and interview format do not emphasize these; including them would dilute focus.
- **Cover behavioral or case-study interview rounds.** These are separate preparation tracks; this app is for the coding screen specifically.

---

## 8. Quality criteria

A shipped version of the app is considered acceptable when:

1. All 11 topics render three worked examples (easy/medium/hard) in Came
2. All 11 topics render three faded scaffolds in Saw
3. All 11 topics render three retrieval problems in Conquered
4. SQL editor works: typing, tab, auto-indent, syntax coloring, persistence
5. No JavaScript errors on page load (verified via Playwright headless)
6. Brace-balanced source compiles via Babel with no syntax errors
7. Bundle is a single `index.html` under 300 KB
8. Installs as a PWA on iOS Safari and works offline after first load

All eight criteria are currently met.

---

## 9. Success metric

The true success metric is binary and post-hoc: **did Milan get the offer?**

Proximate metrics the app tries to optimize for:

- Milan completes ≥ 66 of 99 problem-attempts (each of 33 retrieval problems in at least 2 modes: Learn → Interleave)
- Milan can, by day 6, verbalize *why* a given construct was chosen (join type, window function, NULL idiom) — not just write the construct
- Milan recognizes the Production Finance domain vocabulary when an interviewer uses it in a case setup

These are self-assessed, not instrumented.

---

## 10. References

Key citations that shape the pedagogy:

- Atkinson, R. K., Renkl, A., & Merrill, M. M. (2003). Transitioning from studying examples to solving problems. *Journal of Educational Psychology*, 95.
- Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., & Rohrer, D. (2006). Distributed practice in verbal recall tasks. *Psychological Bulletin*, 132.
- Chi, M. T. H., et al. (1994). Eliciting self-explanations improves understanding. *Cognitive Science*, 18.
- Dunlosky, J., et al. (2013). Improving students' learning with effective learning techniques. *Psychological Science in the Public Interest*, 14.
- Mayer, R. E. (2009). *Multimedia Learning* (2nd ed.). Cambridge University Press.
- Paivio, A. (1971). *Imagery and Verbal Processes*. Holt, Rinehart and Winston.
- Renkl, A. (2014). Toward an instructionally oriented theory of example-based learning. *Cognitive Science*, 38.
- Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning. *Psychological Science*, 17.
- Rohrer, D. (2012). Interleaving helps students distinguish among similar concepts. *Educational Psychology Review*, 24.
- Sweller, J. (1988). Cognitive load during problem solving. *Cognitive Science*, 12.
- Sweller, J., & Cooper, G. A. (1985). The use of worked examples as a substitute for problem solving. *Cognition and Instruction*, 2.
- Taylor, K., & Rohrer, D. (2010). The effects of interleaved practice. *Applied Cognitive Psychology*, 24.
