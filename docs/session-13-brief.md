# Session 13 brief — Phase 24.5 (Job Assist app space research, no version bump)

**Target:** produce a comprehensive landscape doc of the job-search-toolkit app space — application trackers, AI resume/cover-letter tools, personal job dashboards, indie download hubs, dev-tool brand pages — that feeds the upcoming `docs/ADR-003-visual-identity.md` synthesis. Deep, ADR-flavored research; not a quick grep. The output is reference material for human design decisions, not autonomous design lock.

**Estimated time:** 3–4 hours autonomous. Pure research / writing — no code, no MCP changes, no v2 site touches.

**Surface:** intended for a Claude Code Dispatch session launched via `bash scripts/dispatch-session.sh 13`. Equally executable from a regular Cowork session.

**No prerequisite stacking.** Unlike Phase 25 (which stacks on `phase24/export-pipeline`), Phase 24.5 is pure docs. Branches off `main` directly. The open Phase 24 PR (#7) is unaffected; nothing about Phase 24.5 touches `host/`, `website/`, or any code path.

**Why this exists.** The original Phase 25 Block 1 ("Try Canva, fall back to text wireframes") was a thin design-exploration step. The orchestrator Cowork session decided that's not enough — for a v2 site that's the user's daily-look surface, the design decisions deserve a real competitive landscape behind them. Phase 24.5 is that landscape. Phase 25 then inherits a locked visual identity (ADR-003) instead of inventing one mid-implementation.

---

## You are an autonomous Phase 24.5 research agent

You are not waiting for the originating Cowork session to approve every micro-decision. You are the planner, executor, evaluator, and quality gate. Drive Phase 24.5 to a comprehensive landscape doc that the next interactive session can actually use to draft an ADR.

If something genuinely blocks you (an app you can't access, a research direction the brief doesn't anticipate, a finding that contradicts an assumption), surface it in the PR description and proceed with reasonable judgment.

**If the brief and the orientation files disagree, the orientation files win.** This brief is a derived plan, not a re-statement of the ADR.

---

## Orientation — read in this order before any research

1. **`CLAUDE.md`** — project structure, working principles (HITL / Atomic / Deterministic / Evidence-based), Dispatch-session pattern, doc freshness protocol.
2. **`SPEC.md`** — committed phase plan. You are implementing **Phase 24.5** (insert between Phase 24 and Phase 25; no version bump, mirrors the Phase 22.5 precedent).
3. **`docs/ADR-002-architecture-rethink.md` §D4** — load-bearing. The "Visual style" subsection enumerates current guardrails: no hero with marketing claim, no gradient buttons, no emoji, no AI branding, system font stack, sky → pink gradient as accent only, `noindex` + `robots.txt: Disallow /`. Phase 24.5's research must respect these — patterns that violate the guardrails (e.g., aggressive marketing heroes) should still be captured in the landscape doc but flagged as "incompatible with our guardrails" rather than recommended.
4. **`website/index.html`** (v1 site) and **`website/v2/index.html`** (current v2 placeholder) — confirm the existing brand pattern (Tailwind via CDN, slate-950 dark, sky→pink gradient) so research findings can be evaluated against it.
5. **The deferred Phase 25 brief** at `docs/session-14-brief-draft.md` (after the brief-renaming commit) — read this to understand what Phase 25 will inherit from your work. Your landscape doc should produce findings Phase 25's Block 1 can directly act on.

---

## Resolved decisions

These were ambiguities surfaced during Phase 24.5 planning. Resolved up-front so the dispatch agent doesn't escalate.

### R1 — The output is a landscape doc, NOT an ADR

**Decision:** Phase 24.5 produces `docs/phase24_5-app-space-research.md` (the landscape) plus optional supporting files. It does NOT produce `docs/ADR-003-visual-identity.md` — that's the next interactive session's job.

**Why:** ADRs codify decisions. A dispatch agent doing 3–4 hours of autonomous research can produce findings, observations, and recommendations, but the actual decision-making (what to adopt, what to reject, what positioning to claim for v2) should happen interactively with the orchestrator. The dispatch agent's role is to assemble the evidence; the orchestrator's role is to choose the direction.

**How to apply:** the landscape doc ends with a "Recommendations for ADR-003" section listing 5–10 specific patterns (with rationale) that the orchestrator should consider adopting, rejecting, or remixing. Frame each as a question the ADR will answer, not as a foregone conclusion.

### R2 — Coverage over depth-per-app

**Decision:** target 12–15 reference apps with consistent depth-per-app, rather than 5 apps with deep dives. Each app gets ~100–200 words covering: URL, visual takeaway, layout pattern, palette, status conventions, density, one standout pattern, one anti-pattern, link to a publicly-fetchable screenshot or a captioned URL if no screenshot is available. **Copy voice is NOT captured per-app — it lives in a single cross-app subsection per R5.**

**Why:** the orchestrator needs a wide map to compare against, not deep portraits of a few apps. The synthesis session derives signal from "8 of 12 apps use sky-blue for active status" not "Linear's color system has 47 named tokens".

**How to apply:** if an app's depth-per-app exceeds 250 words, condense. If you find an app that doesn't fit the rubric (e.g., it's a fundamentally different shape than the others), capture it in a separate "Outliers" subsection with a paragraph each — don't force it into the main rubric.

### R3 — App categories: 4 buckets, ~3 apps per bucket

**Decision:** four categories the landscape must cover. Each gets ~3 apps (up to 4 if a category has unusual variety). Total ≈ 12–15 apps.

1. **Application trackers (SaaS)**: Huntr, Teal, Simplify Jobs, JibberJobber. Pick 3.
2. **AI resume / cover-letter tools**: Resume Worded, Rezi, Jobscan, Kickresume, Enhancv, Final Round AI. Pick 3.
3. **Personal job dashboards (Notion / Airtable / templates)**: representative templates from each. Pick 3.
4. **Indie maker download hubs / "tools I built" sites**: any 3 from indie-hackers, GitHub releases pages, Astro/Tailwind portfolio sites that double as tool delivery hubs.

**Why these four:** they cover the actual problem space (job-search tooling) plus the closest adjacent shape (indie-maker download hubs that share v2's "personal local-first, no SaaS" positioning). An earlier draft included a fifth bucket of dev-tool brand pages (Linear / Vercel / Raycast etc.); the orchestrator dropped it as off-target — those are visual analogs but not problem-space matches, and the indie-maker bucket already covers the closest visual adjacency.

**How to apply:** if a category's 3 apps don't surface enough variety, add a 4th. If a category turns out to be barren (e.g., indie maker download hubs all look the same), drop to 2 and document why.

### R4 — Screenshots are required, retry hard before falling back

**Decision:** for each app, allocate 5+ minutes to find a publicly-fetchable hero screenshot. Try multiple fetch strategies before giving up: the app's homepage, the app's press / media / about page, the app's product-shots gallery, the Wayback Machine (`web.archive.org`) for a recent capture, the app's GitHub repo README if it's open-source, screenshots embedded in product-review articles or blog posts. Only fall back to a captioned URL if all strategies fail.

**Why:** the orchestrator explicitly chose this policy over the lighter "2-3 min then fall back" approach. A more complete screenshot deck means the synthesis session (Session 14) can compare visual patterns side-by-side without having to re-fetch every reference interactively. The deeper visual analysis Phase 24.5 demands depends on this — visual claims need visual evidence the orchestrator can hold in one view.

**How to apply:** save any successfully-fetched screenshots to `docs/phase24_5-screenshots/<app-slug>.png` (or .jpg). Reference them inline in the landscape doc with markdown image syntax. The target is to have screenshots for ≥80% of the locked app list — if you fall under that ratio, document why in the PR description. For the rare URL-only entry, use the format `**Screenshot:** [Title of view](URL)` so the synthesis session can fetch on demand. Also save a `<app-slug>-source.md` next to each screenshot listing where the image came from (homepage / press kit / Wayback / etc.) so the orchestrator can re-derive it if needed.

### R5 — Copy voice is a single cross-app subsection, not per-app

**Decision:** the landscape doc treats copy voice as secondary to visual layout. **Don't capture copy phrases per-app.** Instead, after Block 2's per-app deep dives, write ONE cross-app subsection in Block 3 (~250–400 words) that surveys voice register across the landscape: pick 4–6 representative phrases total (one quote each from a handful of apps, ≤15 words per quote), classify the voice clusters you see (corporate-confident, friendly-helpful, ironic-developer, etc.), and note which clusters dominate which categories.

**Why:** v2's 8th-grade reading-level constraint (orchestrator decision in Session 13) makes copy load-bearing for differentiation, but the cross-app patterns matter more than per-app prose for the ADR-003 synthesis. Per-app copy capture across 12–15 apps would consume 60–90 minutes for marginal additional signal — the synthesis session derives "v2 sits between corporate-tracker voice and ironic-dev voice" from a tight cross-app survey just as well as from a sprawling per-app catalog.

**How to apply:** Block 2's per-app rubric does NOT include a copy voice line — agents should focus visual time on layout, palette, density, status conventions, standout patterns. Block 3's cross-app section gets a dedicated `### Copy voice across the landscape` subsection. Quote ≤15 words per phrase, in quotes, with URL attribution. Comply with the copyright requirements in `CLAUDE.md` — never reproduce more than that per source. If a per-app section in Block 2 includes a striking copy phrase the agent can't resist quoting, that's fine in moderation, but the systematic copy analysis lives only in the cross-app subsection.

### R6 — User reviews drive failure-mode capture for ≥3 apps

**Decision:** for at least 3 of the 12–15 selected apps (spanning at least 2 of the 4 categories), spend 10–15 min per app reading 5+ user reviews from G2, Capterra, ProductHunt, or app-store reviews. Capture the top 2 complaints + top 2 praises per app in a `### User reviews` subsection of that app's per-app entry.

**Why:** visual-only research surfaces what the apps DO. Review-reading surfaces what they GET WRONG. The synthesis session needs both — knowing Huntr's pipeline columns are pretty doesn't matter if users describe them as "cluttered" or "intimidating." Failure modes drive what v2 should AVOID. The orchestrator added this requirement explicitly during brief review.

**How to apply:** add ~15 min × 3 apps ≈ 45 minutes to the Block 2 budget. The `### User reviews` subsection appears only on the 3+ chosen apps — don't force it on every app, the doc would balloon. Quote ≤15 words per review snippet, in quotes, with reviewer-handle attribution if available + URL of the review page. Pick apps where review-readability is highest (G2 / Capterra > app store reviews > Reddit threads); pick across categories so the failure-mode signal isn't bucket-skewed.

### R7 — Cross-domain outliers (personal-toolkit shapes outside job-search)

**Decision:** add a dedicated `## Outliers — cross-domain personal-toolkit shapes` section after the four category sections in Block 2. Cover 2–3 sites OUTSIDE the job-search space that share v2's "personal local-first toolkit" positioning shape. Candidates: Read.cv, Linktree, Beli, Are.na, Pinboard, indie portfolio template starters that double as tool delivery hubs. Pick 2–3 that surface useful patterns.

**Why:** the four-bucket landscape covers job-search-tooling. v2's actual positioning is "personal toolkit that delivers files." That shape exists OUTSIDE job-search (link-in-bio sites, personal directories, indie portfolios) — and those shapes might inform v2's design more than another job tracker. The synthesis session benefits from the stretch. The orchestrator added this requirement explicitly during brief review.

**How to apply:** R2 rubric applies (URL, visual takeaway, layout pattern, palette, status conventions, density, standout pattern, anti-pattern, screenshot reference per R4). User-review reading per R6 NOT required for outliers. Adds ~30 min to the dispatch.

---

## Deliverable — Block-by-Block

### Block 1 — Initial discovery (60–90 min)

- Run WebSearch queries to surface candidates per category. Capture the search query + top 5 hits per query in a working scratchpad (`docs/phase24_5-research-scratchpad.md` — get pruned at end of session).
- For each candidate, do a quick triage pass: open the URL, take 30 seconds to assess fit, decide if it makes the final 3 per category. Goal of this block: lock the final 12–15 app list.
- Atomic commit on branch `phase24_5/research-brief` (base = `main`): the scratchpad + a `## App selection` section in the landscape doc with the locked list.

### Block 2 — Per-app deep dives + user reviews + outliers (115–175 min)

- For each of the 12–15 selected apps, write a per-app section in `docs/phase24_5-app-space-research.md` covering the R2 rubric: URL, visual takeaway, layout pattern, palette, status conventions, density, standout pattern, anti-pattern, screenshot reference (R4). **No copy voice line per-app per R5.**
- Group by category (R3). Four `## Category:` headings, ~3 apps each.
- For at least 3 of the apps (spanning 2+ categories) per R6: add a `### User reviews` subsection capturing top 2 complaints + top 2 praises from G2 / Capterra / ProductHunt. ≤15-word quotes, URL-attributed.
- After the four category sections, add a `## Outliers — cross-domain personal-toolkit shapes` section per R7 with 2–3 entries (Read.cv, Linktree, Are.na, indie portfolio starters, etc.). R2 rubric applies; R6 user reviews NOT required for outliers.
- Atomic commit per category (4–6 commits across categories + outliers; or one big "Block 2" commit, both acceptable per "atomic = one logical change").

### Block 3 — Cross-app synthesis (60–75 min)

- After per-app sections, write a `## Cross-app patterns` section that aggregates findings across the landscape:
  - Layout shapes that recur (cards / table / hybrid / dashboard) and their frequency
  - Color conventions (which categories default dark, which default light, which use both)
  - Status nomenclature variance (open / submitted / interviewing / etc. — what's standardized, what's bespoke)
  - Density conventions (cramped / breathing / inbetween) and what tends to drive each
  - Where the v2 guardrails (ADR-002 §D4) align with the landscape vs where they diverge
- Inside this section, dedicate a `### Copy voice across the landscape` subsection (~250–400 words) per R5: 4–6 representative phrases total (≤15 words each, in quotes, URL-attributed), classified into voice clusters, with notes on which clusters dominate which categories. This is the ONLY place copy voice gets systematic treatment.
- ALSO inside this section, dedicate a `### Privacy-first messaging conventions` subsection (~200–300 words): how do apps that emphasize "local-first" / "no tracking" / "no SaaS" / "your data stays yours" position themselves visually and verbally? Survey across the landscape — both the indie maker bucket and any privacy-leaning entries elsewhere. Capture 3–4 representative phrases (≤15 words, quotes, URL-attributed) and observations on visual conventions (footer placement / dedicated page / hero callout / etc.). v2's positioning sits in this space; the synthesis session pulls from this subsection directly.
- This section is the bridge between per-app data and the recommendations. The agent's deeper visual analysis time (freed by R5's per-app drop) goes here — make the visual-pattern subsections richer than they would otherwise be.
- Atomic commit.

### Block 4 — Recommendations + open questions for ADR-003 (30 min)

- Write the closing `## Recommendations for ADR-003 synthesis` section: 5–10 specific patterns the orchestrator should consider, framed as questions ADR-003 will answer.
- Examples of good framings: "Should v2 adopt the application-tracker convention of pipeline-stage columns, or treat status as a flat tag like the dev-tool brand pages do? See Huntr (pipeline) vs Linear (flat)."
- Examples of bad framings: "Use cards with status badges." (Foregone conclusion; deprives the synthesis session of choice.)
- Add a `## Open questions` subsection for things the research surfaced but couldn't resolve — e.g., "Did Teal's recent pivot away from explicit status tags hurt or help adoption? Need usage data we don't have."
- Atomic commit.

### Block 5 — PR open + handoff (15 min)

- Open ONE PR titled `Phase 24.5: Job Assist app space research` against `main` from `phase24_5/research-brief`. Description should include: high-level summary (3–5 lines), the locked app list, key cross-app patterns surfaced, and explicit "Next: Session 14 interactive synthesis to ADR-003".
- **Do not merge yourself.** **Do not tag — Phase 24.5 is no version bump.** The originating Cowork session reviews + merges with `--no-ff` to preserve the merge-commit pattern.
- Atomic commit (this block's commit is the PR-open metadata if any; usually there's nothing new on disk).

---

## Working principles (verbatim from CLAUDE.md — non-negotiable)

- **Human-in-the-loop.** Phase 24.5 is autonomous research, but the synthesis (which patterns to adopt) is the next interactive session's job. If you find yourself making a strong design recommendation, reframe it as a question for ADR-003 instead.
- **Atomic.** One logical change per commit. The Block 2 per-category commits or one combined Block 2 commit are both fine; what matters is that any single commit is revertible without surgery on unrelated changes.
- **Deterministic.** Same research approach should produce the same findings. Cite all sources by URL. Don't make claims about an app without a URL backing them.
- **Evidence-based.** Every claim backed by a URL or a quoted phrase. "Linear uses sky-blue for active status" needs a URL. "Most application trackers use pipeline-stage columns" needs a count + the apps backing it.

If the brief and the orientation files disagree, the orientation files win.

---

## Branch + PR mechanics

- **Base branch: `main`.** Phase 24.5 is research, no code-stack dependency.
- **Feature branch: `phase24_5/research-brief`.** Multiple atomic commits, one PR.
- PR mechanics: same as Phase 23 / 24. The `gh` CLI is broken on this machine; PR creation uses `git credential fill` → REST API. Pattern documented in Sessions 8–12 SESSION_LOG entries.
- Credential handling: same `.session-secrets/` pattern from CLAUDE.md "Credential handling pattern (Session 8 — load-bearing)". PAT lives in `.session-secrets/`, never in chat, stripped from origin URL after operations.
- If you cannot push the feature branch, output `git format-patch main..HEAD --stdout` at end of session.

---

## Success criteria

Phase 24.5 ships when ALL of the following hold:

1. `docs/phase24_5-app-space-research.md` exists at the head of `phase24_5/research-brief` with all R3 categories populated and 12–15 apps total covered to R2 depth.
2. Cross-app synthesis section (Block 3) is present and aggregates findings across categories with frequency counts where applicable.
3. Recommendations section (Block 4) contains 5–10 framed-as-questions for the ADR-003 synthesis, NOT foregone conclusions.
4. `docs/phase24_5-screenshots/` exists with screenshots for ≥80% of the locked app list per R4 (each accompanied by a `<app-slug>-source.md` documenting where the image came from). URL-only references for any remaining apps are inline in the landscape doc, with rationale in the PR description.
5. Every claim about an app traces to a URL.
6. Copy-voice analysis lives in a SINGLE `### Copy voice across the landscape` subsection inside Block 3's cross-app patterns (per R5). Per-app sections do NOT contain a copy voice line. Quotes inside the cross-app subsection are ≤15 words each, in quotes, URL-attributed, ≤6 phrases total, comply with `CLAUDE.md` copyright rules.
7. The Phase 24 / 25 work is unchanged — Phase 24.5 adds files under `docs/` and `docs/phase24_5-screenshots/` only. No edits to `host/`, `website/`, `scripts/`, `references/`, or any other tree.
8. PR is open against `main`. No merge yet — orchestrator merges interactively.
9. `docs/phase24_5-research-scratchpad.md` is either committed (transparency about Block 1's selection process) or pruned cleanly (the final landscape doc stands on its own). Either is acceptable; document the choice in the PR description.
10. ≥3 apps (spanning 2+ categories) have a `### User reviews` subsection with top 2 complaints + top 2 praises, ≤15-word quotes, URL-attributed (per R6).
11. `## Outliers — cross-domain personal-toolkit shapes` section exists with 2–3 entries (per R7).
12. Block 3 cross-app synthesis includes a `### Privacy-first messaging conventions` subsection (~200–300 words) with 3–4 representative phrases.

---

## End-of-session deliverables (in your final message back)

1. The PR URL.
2. Block-by-block summary of what landed, with commit SHAs.
3. The locked app list (12–15 apps across 4 categories + 2–3 outliers).
4. The top 5 cross-app patterns surfaced, one line each.
5. The 5–10 questions framed for ADR-003 synthesis.
6. Any apps you tried to research but had to drop (auth wall, paywall, content-restricted), with rationale.
7. Any time-budget surprises — apps that were quick to assess vs apps that took longer than expected.

---

## Out of scope for this session

- Drafting `docs/ADR-003-visual-identity.md` (next interactive session's job per R1).
- Building any reference mockups (Session 14+ work).
- Any code changes anywhere in the repo.
- Touching the open Phase 24 PR (#7).
- Touching the deferred Phase 25 brief (now at `docs/session-14-brief-draft.md`).
- Editing `CLAUDE.md` to flag Phase 24.5 status — that's a wrap commit the orchestrator handles after merge.
- Any v1 or v2 deploy-source touches.
- Adding Phase 24.5 to `SPEC.md` as a numbered phase — the orchestrator does that during the merge wrap.
- Live-smoke-testing anything (n/a; Phase 24.5 is pure research).

---

## Questions for orchestrator (flag for review before approving the brief)

All five original questions were resolved by the orchestrator before the brief was finalized:

1. **R3 app categories** — bucket 5 (dev-tool brand pages) dropped; the landscape covers 4 buckets (trackers / AI tools / dashboards / indie hubs) at ~3 apps each.
2. **R5 copy voice** — demoted from per-app to a single cross-app subsection in Block 3.
3. **R4 screenshots** — retry-hard policy locked; 5+ min per app, multiple fetch strategies, ≥80% screenshot coverage target.
4. **App list discretion** — no must-includes; dispatch agent picks the locked 12-15 apps freely from the candidate lists in R3.
5. **Branch naming** — `phase24_5/research-brief` confirmed.

No open questions for the dispatch agent. If a new ambiguity surfaces during the run, flag it on the PR and proceed with reasonable judgment per the working-principles "human-in-the-loop" rule.

---

*End of brief.*
