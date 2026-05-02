# Source attribution rules — interview-prep skill

The `interview-prep` skill mixes two kinds of content:

1. **Synthetic** — worked examples, faded scaffolds, retrieval problems. Authored by Claude, using domain vocabulary and patterns drawn from sourced research. **Allowed.**
2. **Sourced** — real reported interview questions in the "Real Qs" tab. Each must cite a real source. **Required.**

This file is the canonical rule set for what counts as a credible source, what attribution is required, and what failure modes to watch for.

If you (Claude or human) are unsure whether a piece of content is OK to ship, the answer is in this file.

---

## What synthetic content can claim

Synthetic worked examples and retrieval problems can:

- ✅ Use domain vocabulary the company actually uses ("ATL/BTL crew costs," "north-star metric," "1099 vendor") **provided** that vocabulary is sourced from the company's real materials (tech blog, careers page, JD, public earnings calls)
- ✅ Pose realistic business scenarios in the company's industry (vendor concentration risk for a streaming service, retention curves for a social product)
- ✅ Use a **target SQL dialect** the company is known to use (Presto/Trino for Netflix, BigQuery for Google, Snowflake for Pinterest) **provided** the dialect choice is sourced
- ✅ Cite the **schema panel data as fictional but representative**

Synthetic content **MUST NOT**:

- ❌ Claim that a specific named person at the company asked the question
- ❌ Claim to be a "real Netflix question" or "real Stripe question" — those are reserved for the sourced tab
- ❌ Use real customer names, real internal project codenames, real employee names
- ❌ Fabricate financial figures and present them as company performance data

When in doubt, label synthetic content as such in the walkthrough: *"This is a synthetic example built around the kinds of vendor-concentration questions Netflix Production Finance teams actually face — see [source] for the public framing."*

---

## What counts as a credible source for the "Real Qs" tab

Every entry must cite at least one source. Sources fall into tiers:

### Tier 1 — preferred

- **Glassdoor** interview reports — must include the report date and rough role title
- **Blind** posts — must include the URL; Blind posts are anonymous but the platform is established
- **Levels.fyi** interview-experience threads — preferred for FAANG roles
- **Company tech blog** — when the company publishes its own data infrastructure or interview process docs
- **Reddit** technical career subreddits (r/cscareerquestions, r/dataengineering) — only for posts with high upvote scores and detailed candidate accounts

### Tier 2 — acceptable with caveats

- **InterviewQuery / DataLemur / 1point3acres / LeetCode discuss** — these aggregate questions but rarely cite their sources well. Use as supporting evidence only when the question also surfaces in a Tier 1 source.
- **Medium / Substack posts** — only from authors who clearly attended a real interview at the company; one-off opinion pieces don't count
- **YouTube interview-prep channels** — only when the host shows the question coming from a real source; "here's what I think they'd ask" doesn't count

### Tier 3 — not acceptable

- ❌ "Common interview question" without a specific source attribution
- ❌ ChatGPT / Claude / other LLM output (recursive: this skill won't cite another LLM as a source)
- ❌ Forum posts older than 5 years for questions that turn on current company practice (the interview process changes; old reports may be stale)
- ❌ Paid courses' question banks (often lifted without attribution from Tier 1 sources; cite the original)

---

## Required attribution per question

Every question in the `real_questions` array must have:

```json
{
  "source": "Glassdoor (2025-08, anonymous senior DA)",
  "source_url": "https://www.glassdoor.com/Interview/..."
}
```

Both fields are required. The `source` field should:

- Name the platform
- Include the **date or year** of the report when available
- Include the **role title** the source person was applying for
- Note if the report is anonymous

Examples of good `source` strings:

- `"Glassdoor (2025-08, Data Analyst Production Finance)"`
- `"Blind post by 'verified Netflix DA', 2024-11"`
- `"Levels.fyi interview thread, 2025-03, Senior Data Scientist"`
- `"Netflix Tech Blog post, 2024-06, on Iceberg + Trino architecture"`

Bad `source` strings (would fail review):

- `"Glassdoor"` — no date, no role
- `"Online interview prep guide"` — too vague
- `"A friend who works there"` — unverifiable
- `"Common knowledge"` — no, it isn't

---

## Solution authorship

For high-frequency patterns (a problem that surfaces in 3+ Tier 1 sources), the skill may write a hand-crafted solution. When it does:

```json
{
  "source": "Glassdoor (2025-08, Senior DA)",
  "source_url": "...",
  "solution": "WITH ranked AS (...) SELECT ...",
  "solution_authored_by": "claude",
  "note": "Solution authored by Claude based on the prompt and reported feedback. The original Glassdoor report did not include the answer."
}
```

The `solution_authored_by: "claude"` flag and the explanatory `note` are non-negotiable when the solution did not come from the source. **Never present a Claude-authored solution as if the original interviewer's answer is being quoted.**

---

## Empty-state behavior

If credible sources for a company turn up fewer than 3 questions, **do not pad the list with synthetic content presented as real**. Instead:

1. Output a real_questions array with whatever you have (could be empty)
2. Set `"empty_state_explanation"` in the metadata to a candid note: e.g., `"Only 2 sourced questions found for this role. The Real Qs tab shows what was found; consider asking your recruiter for example questions or pasting any you've collected manually."`
3. Surface the empty-state explanation in the PWA's user-facing README

The skill's value collapses if it pretends to have sourced content it doesn't have. Honest empty states preserve trust.

---

## Date freshness

Sources that turn on current company practice (interview format, technical stack, team structure) should be **less than 18 months old**. Older sources may still be valid for foundational topics (basic SQL hasn't changed in 30 years) but shouldn't be the primary source for "what does Netflix's DA interview look like in 2026."

The skill should record the source date in the `source` string and prefer the most recent credible report when multiple exist.

---

## Audit trail

The Phase B/C output (`[convention]-format.md`) lists every URL the skill consulted. The Phase E output (the `real_questions` array) cites a subset of those URLs per question. Together they form the audit trail — a reviewer can trace any claim in the PWA back to the source that supports it.

If the audit trail is incomplete, the build is incomplete. The Phase F smoke test should fail loudly if any `real_questions` entry is missing `source` or `source_url`.
