---
name: interview-prep
description: "Research-driven interview prep skill that builds a deployable single-file study PWA tailored to a specific role. Pulls from decoded-jds/, research/, scores/, and credible web sources (Glassdoor, Blind, Levels.fyi, official tech blogs). Produces a 3-phase study site (worked-example → faded-scaffold → free-recall) with topic content, a 'Real Qs' tab of sourced reported interview questions, and an installable PWA wrapper. Use this skill whenever the user wants to: prepare for a specific company's technical or case-study interview rounds, build a study site for an interview, generate practice problems for a CoderPad/HackerRank screen, or convert a decoded JD into a tailored prep plan. Also trigger when the user says 'help me prep for [company]', 'build a study site for [role]', 'I have a Netflix-style data analyst interview next week', or any interview-prep request that follows resume targeting."
---

# Interview Prep

A research-driven, human-in-the-loop skill that converts a decoded JD plus company research into a deployable single-file Progressive Web App for one specific interview. Grounded in evidence-based learning science (worked examples → fading → retrieval, plus interleaving and spacing).

> **Read this first if you are about to invoke or modify this skill.** The full design rationale (why these phases, why these citations, why a static PWA and not a dynamic app) lives in `../../SPEC.md` §5–§6. This SKILL.md tells you *how to run the skill operationally*.

## Why This Skill Exists

Most interview-prep advice is "re-read your notes, watch a YouTube playlist." That feels productive but doesn't build durable recall. The candidates who do well in 45–60-minute timed coding screens have practiced **active retrieval under time pressure** on problems shaped like the ones they'll see.

This skill builds that practice surface for one specific interview:

- **Tailored to the actual role** by pulling from the user's `decoded-jds/[convention].md` and `research/[company].md`
- **Sourced, not invented** — reported real interview questions cite Glassdoor / Blind / Levels.fyi / official posts; synthetic worked examples are clearly marked as such
- **Pedagogically structured** as a fixed three-phase loop per topic that maps to Renkl's worked-example → fading → retrieval sequence
- **Installable on the user's phone** as a PWA so 20-minute prep sessions during the day are frictionless
- **Cheap to ship and reproduce** — single HTML file, CDN-loaded, no backend, zero monthly cost

The skill intentionally does NOT teach a topic from first principles. It assumes the user has working familiarity with the topic area and needs to *re-activate, stretch, and stamp in* what they already half-know.

## Core Principles

1. **No fabrication.** Every reported real-world interview question must cite a credible source (Glassdoor with date and role, Blind post URL, Levels.fyi thread, official Netflix tech blog, etc.). Synthetic worked examples are allowed and marked as such — but they must reflect domain vocabulary and patterns that *are* sourced from the company's real materials.

2. **Human-in-the-loop at every phase.** The skill checkpoints with the user after each of its six phases. Topic lists, content drafts, and the final build are all reviewed before the next phase runs.

3. **Specific over generic.** Schema panels show realistic data with consistent identifiers across topics. Walkthroughs explain *choices* ("INNER JOIN because orphan payments should drop out"), not just code. Domain vocabulary from the company's real world (e.g., "fiscal-month-close," "ATL/BTL," "burn rate") is surfaced deliberately.

4. **Evidence-based pedagogy.** The three-phase per-topic loop and the interleave mode are not ergonomic flourishes — they map to citable cognitive-science findings. Citations render in the PWA footer so the user can verify.

5. **Deliverable owns its own deployment story.** The output folder is drag-and-drop deployable to Netlify/Vercel; the user is never asked to run npm or wait for a build.

## Prerequisites

**Required inputs:**

- `decoded-jds/[convention].md` — the decoded job description for the target role (output of the `decoded-jd` skill). If missing, prompt the user to run `decoded-jd` first.
- `research/[company].md` — company research brief (output of the `resume-targeter` skill's Phase 2 or built standalone). If missing, prompt the user to provide it or run a research pass.

**Optional inputs (used when present):**

- `scores/[convention]-after.md` — flags a topic area as a known weak spot if the score report cites it
- `memory.md` — surfaces the user's preferred study style and anchor stories
- `interview-prep/[convention]-recruiter-prep.md` and similar pre-existing prep notes — Claude reads these to avoid duplicating content

**Naming convention:** the skill follows the project-wide convention `[company]-[role-slug]-[YYYY-MM]`. The orchestrator passes these variables; standalone invocations infer them from the decoded JD.

## Workflow

The skill runs in six phases (A through F). Each phase has a deliverable saved to disk and a checkpoint where Claude self-audits and presents progress to the user. Per the project's approval cadence, Claude proceeds automatically when self-audit is fully green and stops on any warning or failure.

### Phase A: Gather Inputs

**Goal:** Confirm all required inputs exist and read them carefully.

**Actions:**

1. Read `decoded-jds/[convention].md` — extract job title, team, location, technical stack mentioned, explicit responsibilities, required vs. preferred qualifications.
2. Read `research/[company].md` — pull culture, values, interview process notes, recent news. Note the dated subsection for this specific role if one exists.
3. Read `scores/[convention]-after.md` if it exists — flag concept gaps the scorer surfaced.
4. Read `memory.md` — pull study-preference notes and anchor stories.
5. Check `interview-prep/[convention]-*` for pre-existing prep materials. Read them; do not overwrite.

**If any required input is missing,** stop and tell the user which earlier skill they need to run first (or which file to provide).

**Output:** internal context only; no file written.

**Checkpoint:** ✅ all required inputs read; missing optional inputs noted.

### Phase B: Format Inference

**Goal:** Identify the exact interview format you're prepping for.

**Actions:**

From the decoded JD and research, infer:

- **Round types** that will appear (recruiter screen, hiring manager, technical screen, take-home, on-site/loop, behavioral, case study)
- **For each technical round:** language/dialect (Presto, Postgres, BigQuery, Python/Pandas), platform (CoderPad, HackerRank, Karat, Zoom whiteboard), duration, problem count
- **Domain vocabulary** the interviewer will use (e.g., "ATL/BTL crew costs," "DAU retention curve," "north-star metric")
- **Behavioral framing** the company emphasizes (Amazon Leadership Principles, Netflix Culture Memo, Stripe Operating Principles)
- **Hard expectations** ("must verbalize reasoning while typing," "no autocomplete," "no internet access")

If web research is needed to fill gaps, do focused searches (max 3–5 queries) on:

- "[Company] [role] interview process site:glassdoor.com"
- "[Company] [role] technical screen Blind"
- "[Company] data analyst interview Levels.fyi"
- "[Company] tech blog [data infrastructure | engineering]"

**Output:** `interview-prep/[convention]-format.md` with this structure:

```
# [Company] [Role] — Interview Format
# Last updated: YYYY-MM-DD

## Round Sequence
1. Recruiter screen — 30 min, behavioral + logistics
2. Hiring manager screen — 45 min, behavioral + role-specific case Q&A
3. Technical screen — [duration], [platform], [problem mix]
4. ...

## Technical Screen Detail
- Language / dialect: ...
- Tool: ... (CoderPad, HackerRank, etc.)
- Problem count and difficulty mix: ...
- What's evaluated beyond correctness: ...

## Domain Vocabulary
- term — meaning / context
- ...

## Sources
- [Glassdoor (2025-08, anonymous senior DA)](url)
- [Blind thread, 2024-11](url)
- [Company tech blog post on data infrastructure](url)
```

**Checkpoint:** ✅ format file written; sources cited; user has reviewed and approved before Phase C.

### Phase C: Topic Synthesis

**Goal:** Produce a ranked topic list calibrated to interview frequency.

**Actions:**

1. Use the format inference from Phase B to draft a topic list:
   - Technical screens: **7–12 topics** ranked T1 (very likely, every interview), T2 (likely for this role), T3 (possible but lower-frequency)
   - Behavioral / case rounds: **4–6 topics** corresponding to round-type categories (conflict, scope ambiguity, metric drop, etc.)
2. For each topic, attach:
   - `tier` — T1 / T2 / T3 / PY (Python sub-track) / SD (system design)
   - `frequency_signal` — one-sentence rationale citing a source ("appears in every Glassdoor SQL screen for Netflix DA")
   - `sources` — 1–3 URLs supporting the inclusion
3. Rank by tier then by sourced frequency.

**Output:** appended to `interview-prep/[convention]-format.md`:

```
## Topic List (ranked by interview frequency)

| # | Topic | Tier | Frequency Signal | Sources |
|---|---|---|---|---|
| 1 | Multi-Table Joins | T1 | Every Glassdoor SQL screen | url1, url2 |
| 2 | Window Functions | T1 | ... | ... |
| ... | ... | ... | ... | ... |
```

**Checkpoint:** ✅ topic list complete; every topic has a sourced frequency signal; user has approved the list before Phase D.

### Phase D: Content Authoring

**Goal:** Generate the three-phase content for every topic.

For each topic, produce:

#### Worked examples (the "Came" phase)

Three solutions at increasing difficulty (easy, medium, hard). Each includes:

- A natural-language `prompt` stating the **mechanical ask** AND the **business motivation** ("Return the top 3 vendors per production by total spend, **so we can flag concentration risk**")
- A `schemas` panel listing every referenced table with column names and 3–5 sample rows. Sample rows must be **internally consistent** across panels (vendor V001 means the same thing everywhere)
- A complete `solution` that actually runs in the target dialect (no pseudo-SQL, no untested Python)
- A `walk` array of **6–10 walkthrough bullets** explaining the *choices* — not just the code. Bullets should look like:
  - ✅ "I used INNER JOIN here because orphan payments should drop out — we only care about payments that match a production"
  - ❌ "This is an INNER JOIN" (just labels, no reasoning)
- After the first worked example only, an italic prompt to self-explain ("Before moving on, explain this back to yourself in your own words")

#### Faded scaffolds (the "Saw" phase)

Three scaffolds — same prompts as the worked examples, but with **4–8 strategically placed `_____` blanks** inserted at error-prone tokens:

- ✅ Blank these: join type, NULL operator (`IS NULL` vs `= NULL`), window function choice (ROW_NUMBER vs RANK vs DENSE_RANK), threshold literals, ORDER BY direction in window functions, COALESCE / NULLIF arguments
- ❌ Don't blank: aliases, formatting, the obvious SELECT *, ORDER BY direction on the outer query

The full solution is available on tap, but the first instinct should be to recall.

#### Retrieval problems (the "Conquered" phase)

Three brand-new problems (not the same prompts as worked or faded), with:

- A `prompt` (same business-motivation requirement)
- A `schemas` panel
- A `solution` for self-check
- A `selfExplain` seed question ("Why did I choose a LEFT JOIN here?") to scaffold elaboration
- An `explanation` paragraph for post-attempt self-check
- A `difficulty` field

Difficulty calibration:

| Difficulty | Target | Description |
|---|---|---|
| easy | < 5 min | Single table or one join, one or two clauses, direct aggregation or filter |
| medium | 10–15 min | 2–4 joins or CTEs, window function with partition+order, conditional aggregation, or date boundary logic |
| hard | 20+ min | 4+ CTEs, layered windowing, NULL-aware boolean logic, or reconciliation with tolerance |

**Output:** `interview-prep/[convention]-content.json` matching `content-schema.json`. Top-level keys:

```json
{
  "metadata": { "company": "...", "role": "...", "convention": "...", "generated_at": "..." },
  "topics": [
    {
      "id": "joins",
      "title": "Multi-Table Joins",
      "tier": "T1",
      "frequency_signal": "...",
      "sources": ["..."],
      "worked": [ { "difficulty": "easy", "prompt": "...", "schemas": [...], "solution": "...", "walk": [...] }, ... ],
      "faded":  [ { "difficulty": "easy", "prompt": "...", "schemas": [...], "scaffold": "...", "solution": "...", "walk": [...] }, ... ],
      "retrieval": [ { "difficulty": "easy", "prompt": "...", "schemas": [...], "solution": "...", "selfExplain": "...", "explanation": "..." }, ... ]
    }
  ],
  "real_questions": [ ... see Phase E ... ],
  "exam_meta": { "format": "...", "alternateFormat": "...", "keyInsight": "...", "highROI": "..." },
  "patterns": { "sql": [...], "python": [...] }
}
```

**Checkpoint:** ✅ every topic has 3 worked + 3 faded + 3 retrieval; schemas internally consistent; walkthroughs explain choices not labels; user has approved a representative topic before Claude commits to authoring all of them.

> **Iteration tip.** For the user's first review, Claude should generate only **one fully fleshed-out topic** as a representative sample. Once the user approves the structure and depth, Claude generates the remaining topics in batches (3–4 at a time) with brief checkpoints between batches.

### Phase E: Real Questions Tab

**Goal:** Compile a sourced collection of reported interview questions for the company.

**Actions:**

Search the web with focused queries:

- "[Company] [role] interview questions site:glassdoor.com"
- "[Company] [role] interview Blind"
- "[Company] [role] Levels.fyi"
- "[Company] [role] InterviewQuery DataLemur 1point3acres"

For every question that surfaces, record:

```json
{
  "id": "rq_001",
  "category": "SQL | Python | System Design | Behavioral | Case",
  "title": "Short title",
  "prompt": "Verbatim or near-verbatim prompt as reported",
  "concepts": ["window functions", "deduplication"],
  "difficulty": "easy | medium | hard",
  "source": "Glassdoor (2025-08, anonymous senior DA)",
  "source_url": "https://...",
  "solution": "...",        // optional, only for high-frequency patterns
  "hint": "...",            // optional
  "note": "..."             // optional candidate-reported notes
}
```

**Hard rules:**

- Every question MUST have `source` and `source_url`. No source → not included.
- If you can't find at least 3 credible sourced questions for the role, do NOT pad with invented content. Output an honest "no sourced questions found" state and note this in the PWA's user-facing README.
- For high-frequency patterns (cited in 3+ sources), Claude may write a hand-crafted solution — but it must be marked `"solution_authored_by": "claude"` and the source attribution must remain on the prompt.

**Output:** the `real_questions` array inside `[convention]-content.json`. Also append a sources summary to `[convention]-format.md`:

```
## Real Questions Sources

- [N] questions sourced from Glassdoor
- [N] from Blind
- [N] from Levels.fyi / InterviewQuery / DataLemur
- [N] flagged as "high-frequency pattern" with hand-authored solutions
```

**Checkpoint:** ✅ all questions have sources; if zero sourced questions, the empty state is documented; user has reviewed source quality before Phase F.

### Phase F: Build and Ship

**Goal:** Produce the deployable PWA folder, smoke-test it, and write the user-facing README.

**Actions:**

1. **Render the template.** Inject `[convention]-content.json` into `skills/interview-prep/template/app.jsx.template`, then into `index.html.template`. Run the build script (`scripts/build-pwa.sh` — written in Phase 2 of the project build). Output goes to `interview-prep/[convention]-pwa/`.
2. **Smoke test.** Run a headless Playwright check:
   - Page loads without `pageerror` events
   - Bundle is brace-balanced (programmatic `{` vs `}` count)
   - Bundle ≤ 400 KB
   - Manifest validates; service worker registers
   - Key strings present: every topic title, the "Came / Saw / Conquered" labels, the citation footer
3. **Write the user-facing README** at `interview-prep/[convention]-pwa/README.md`. It should explain:
   - What the site is and how the three phases work
   - How to deploy (Netlify Drop in 30 seconds)
   - How to install as a PWA on iPhone Safari and Android Chrome
   - That progress is browser-local; tips for not losing it
   - Where the citation footer's references come from
4. **Update `tracker.md`** — set `interview_prep_pwa` for this row to ✅ + filename of the deploy folder.
5. **Present files** to the user with a `computer://` link to the deploy folder's README.

**Output structure:**

```
interview-prep/[company]-[role-slug]-[YYYY-MM]-pwa/
├── index.html
├── app.jsx                  ← unminified source for reference
├── content.json
├── manifest.json
├── sw.js
├── icon-192.png             ← shared neutral UJA icon
├── icon-512.png
└── README.md
```

**Checkpoint:** ✅ smoke test green; bundle under budget; README explains deployment; tracker updated.

## Content Authoring Rules (Mandatory)

These rules govern every problem Claude authors.

### Every worked example must:

- State the **mechanical ask** AND the **business motivation** in the prompt
- Include a schema panel for every referenced table with realistic, **internally consistent** sample data
- Present a solution that actually runs in the target dialect (no pseudo-syntax)
- Provide 6–10 walkthrough bullets that explain **choices**, not just code

### Every faded scaffold must:

- Reproduce the worked example's solution with 4–8 strategic `_____` blanks
- Blank the things candidates most often get wrong (join type, NULL operator, window function choice, threshold literals, ORDER BY in window)
- NOT blank trivia (aliases, formatting, ORDER BY direction on the outer query)

### Every retrieval problem must:

- Be solvable without the worked example visible
- Include a `selfExplain` seed question to scaffold elaboration
- Include an `explanation` paragraph for post-attempt self-check
- Scale in cognitive demand per the difficulty calibration table

### Problems should be realistic, not contrived

If a problem is just "find the 3rd-highest salary," discard it. Every problem should map to a real scenario from the company's domain — vendor concentration risk, monthly close rollups, A/B test analysis, retention curves, conflict-of-interest detection, etc.

### Every claim about real interview format must cite a source

Glassdoor anecdotes need a date and rough role title. Blind threads need URLs. Tech blog claims need post URLs. If a claim can't be sourced, drop it.

## Pedagogical Foundation (Citations)

The skill enforces these evidence-backed strategies:

| Principle | Source | Where it manifests in the PWA |
|---|---|---|
| Worked examples | Sweller & Cooper (1985); Renkl (2014) | "Came" phase shows complete solutions before any practice |
| Fading | Atkinson, Renkl & Merrill (2003) | "Saw" phase strips strategic portions |
| Retrieval practice | Roediger & Karpicke (2006) | "Conquered" phase forces free recall — blank editor, no scaffold |
| Interleaving | Rohrer (2012); Taylor & Rohrer (2010) | "Interleave" mode mixes problems across topics |
| Spacing | Cepeda et al. (2006) | Flagged problems resurface after a cooldown |
| Dual coding | Paivio (1971); Mayer (2009) | Schema panels render visual tables alongside prompts |
| Elaboration | Chi et al. (1994) | Italic self-explain prompts; `selfExplain` seed on retrieval problems |

These citations render in the PWA footer so the user can independently verify the approach. The expanded reference list lives at `references/pedagogy.md`.

## Generic Across Interview Formats

The skill must handle more than just SQL. Topic types and editor modes:

| Round type | Topic example | Worked-example shape | Editor mode |
|---|---|---|---|
| SQL technical | Window Functions | SQL solution + walkthrough bullets | `mode: 'sql'` (syntax highlight) |
| Python / Pandas | groupby + merge + rolling | Python solution + walkthrough | `mode: 'python'` (syntax highlight) |
| System design | Design a feed ranker | Reference architecture + tradeoff bullets | `mode: 'plaintext'` (notes) |
| Behavioral | Conflict with PM (STAR) | STAR-formatted answer + analysis | `mode: 'plaintext'` |
| Case study | Diagnose a metric drop | Framework walk + computed answer | `mode: 'plaintext'` |

The PWA's editor component is parameterized by `mode`. Tokenizer and persistence keys vary; the rest is shared. See SPEC §6.2.

## Output Files

```
interview-prep/[convention]-format.md           ← Phase B + C output
interview-prep/[convention]-content.json        ← Phase D + E output (intermediate)
interview-prep/[convention]-pwa/                ← Phase F deliverable
├── index.html
├── app.jsx
├── content.json
├── manifest.json
├── sw.js
├── icon-192.png, icon-512.png
└── README.md
```

The `[convention]-pwa/` folder is git-ignored (per project `.gitignore`) because per-application output may contain company- or candidate-specific specifics.

## Relationship to Other Skills

- **Reads from `decoded-jd`** — required input
- **Reads from `resume-targeter` (research file)** — required input
- **Reads from `resume-scorer` (after report)** — optional, used to flag weak topic areas
- **Reads from `why-this-company` (speaking points)** — optional, used to surface the candidate's planned narrative for behavioral round content
- **Updates `tracker.md`** — the orchestrator handles the actual write; this skill just provides the line item
- **Wired into `orchestrator` as Step 9.5** — optional step between Networking and Wrap-up

## Failure Modes and Recovery

| Failure | What it means | Recovery |
|---|---|---|
| Web research returns thin / nothing for the company | Company is too niche or too new for sourced questions | Output honest empty state on the Real Qs tab; offer the user the option to manually paste questions they've gathered |
| Bundle exceeds 400 KB | Content is heavier than the template can carry | Move heavy content (long walk arrays, oversized schemas) into externally-loaded JSON; document in PWA README |
| Smoke test fails with `pageerror` | JSX syntax error or missing prop | Show the error to the user, offer to roll back the last topic batch |
| User rejects a worked example | Content doesn't match their voice or the company's style | Don't proceed to remaining topics until structure is approved (Phase D iteration tip) |
| Decoded JD or research file missing | Required input absent | Stop; tell the user which earlier skill to run first |

## Important Reminders

- **Do NOT fabricate interview questions.** No source = not included.
- **Do NOT auto-deploy.** The skill produces a folder; the user deploys it.
- **Always run the smoke test before presenting the final PWA** — a broken HTML file with no error message wastes user trust.
- **Always cite the pedagogy references in the PWA footer** — this is part of the skill's identity, not a footer decoration.
- **Honor the project formatting rules** in `memory.md` and `references/patterns/formatting-rules.md` for any markdown the skill generates.
- **The PWA is single-user, browser-local.** Don't claim or imply multi-user features. SaaS plans live in `ROADMAP.md`.

---

*See SPEC.md §5–§6 for the higher-level rationale.*
