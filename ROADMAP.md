# ROADMAP.md — Ultimate Job Assistant

**Last updated:** 2026-05-02
**Status:** Living document. The full v0.1.0 build plan lives in SPEC.md. This file captures *post-v0.1.0* work.

---

## How this file works

Each section below describes a possible future direction with rough scope, cost, and prerequisites. Items here are NOT committed work. They become committed when:

1. Milan approves an item for active build, AND
2. A SPEC update or follow-up SPEC document is written (every committed item earns its own spec)

Items live here so the design seams in v0.1.0 stay aware of where we might go later.

---

## Track 1 — SaaS pivot

Convert the personal toolkit into a multi-user product where strangers can sign up, run the workflow on their own JDs, and download their own deliverables.

### Why this might happen

Milan said: *"I want to build this out so someone random can use it for their job applying needs."*

### What changes from v0.1.0

| Concern | v0.1.0 (today) | SaaS |
|---|---|---|
| Auth | none | Clerk free tier (10K MAU free) or Supabase Auth |
| Database | filesystem + git | Supabase (Postgres) free tier (500 MB, 50K MAU) |
| Skill execution | Claude in chat (Cowork) | Anthropic API server-side, wrapped as serverless functions |
| Hosting | Netlify Drop, free | Vercel Pro $20/mo or Cloudflare Pages free + Workers |
| Payments | none | Stripe (test mode free; ~3% on real txns) |
| Privacy / compliance | n/a (single user) | GDPR, CCPA, data deletion, ToS, privacy policy |
| File storage | filesystem | Supabase Storage or R2 (~$0/mo at low volume) |
| Per-user PWA | folder on disk | hosted subdomain or download link |

### Architecture seams already in place

- Content separated from rendering at `content.json` (SaaS can swap from a DB)
- Skill spec is YAML frontmatter + markdown — easy to ship as an API contract
- No hardcoded Milan-specific paths in skill code (only in personal-data folders, which are git-ignored)

### Cost ladder

| Stage | Users | Stack | Cost / mo |
|---|---|---|---|
| Hobby | 1–10 | Vercel free + Supabase free + Clerk free | ~$0 (excluding Anthropic API) |
| Light | 10–500 | Vercel Pro + Supabase Free + Clerk free | ~$20 |
| Growth | 500–5K | Vercel Pro + Supabase Pro + Clerk Pro | ~$70 |
| Scale | 5K+ | Custom; depends on usage | $200+ |

Anthropic API costs are usage-based. At ~$0.05–0.50 per workflow run depending on model choice and how aggressively the skill leans on web research.

### Open design questions (do not need answers yet)

- Bring-your-own-API-key vs. operator-provided?
- Do users own their data file-by-file, or only via export?
- Real-time collaboration on a resume targeting session, or single-user only?
- Resume-targeter's "human-in-the-loop" model: how does that translate to async web UI?

### Prerequisites

1. v0.1.0 ships and gets a real successful run
2. Decision: flip repo to public (currently private)
3. A separate SPEC document (`SPEC-saas.md`) before any code

---

## Track 2 — Browser-driven skills (without backend)

Lighter version of the SaaS pivot: package each skill as a static page that runs Claude *via the user's own API key*, kept entirely in the browser. No server, no auth, no database, no payments.

### Why this might happen

Lower bar than full SaaS. Anyone with an Anthropic API key gets the toolkit; Milan never has to operate a service.

### Cost / mo

$0 to operator. Users pay their own Anthropic bill.

### Tradeoffs

- ✅ No operator infrastructure
- ✅ User data never leaves their browser
- ❌ User must sign up for Anthropic API (friction)
- ❌ Web research from a browser is rate-limited and CORS-restricted
- ❌ File handling is awkward (downloads, no persistent project state)

---

## Track 3 — Code execution for self-grading

Add a real SQL playground inside the PWA so retrieval problems can be self-checked.

### Approach options

1. **DuckDB-Wasm** — runs SQL fully in the browser, no backend needed. Bundle adds ~3 MB; works for analytical SQL but not Postgres/Trino dialect features that DuckDB lacks
2. **Server-side executor** — pushes the project into "needs a backend" territory; only worth it if SaaS pivot happens first
3. **Worker that proxies to Snowflake/Trino sandboxes** — most realistic dialect parity but $$$ and complex

### Recommendation

Start with DuckDB-Wasm. Document dialect divergences from Trino. Server-side only if SaaS happens.

---

## Track 4 — Spaced repetition (real)

Replace the v0.1.0 flag-and-cooldown with a proper SM-2 / Anki-style scheduler.

### Why later

The flag-and-cooldown is fine for a 7-day prep horizon. SM-2 only matters when content volume exceeds what someone can churn through in a week and the user has a multi-week study horizon (e.g., a junior candidate prepping for their first analyst role).

### Implementation

- Two new fields per problem: `next_review_at`, `ease_factor`
- localStorage today; database when SaaS happens
- Standard SM-2 update on every "Conquered" attempt: ease ± based on self-rating
- Anki-style 4-button rating (Again, Hard, Good, Easy)

---

## Track 5 — Cross-application analytics

Today, each application's `interview-prep` PWA is isolated. There's no view that says "Milan tends to struggle with window functions across companies."

### What this would unlock

- Resume-targeter could surface: "you've struggled with X concept in 3 of your last 5 prep sites — call it out as a growth area on your resume"
- Portfolio-coach could pick: "your last 4 study sites had a deduplication topic; you've never done a portfolio piece on dedup — recommend it"
- Speaking-points could rehearse: "in your last 3 interviews, the case-study round used a metric-drop framing; here's a refresher"

### Implementation

A small `analytics.json` at the project root; every PWA writes summary stats on completion (topics attempted, retrieval pass rate, time-on-task). Skills read it. No identifying info, all on disk.

---

## ~~Track 6 — Auto-deploy (CD on tag)~~ — promoted to v0.1.1

This track is now part of the committed v0.1.1 build (SPEC §14). The form is slightly different from the original framing: rather than auto-deploying on tagged release, the v0.1.1 plan auto-deploys on **every push to main** of the canonical private repo, via a GitHub Action that:

1. Runs `scripts/sync_to_public.py` with strict PII scan
2. Pushes the sanitized result to the deploy-source repo
3. Netlify (now the host) auto-rebuilds when the deploy-source repo changes

Edit-to-live latency target: ~30 seconds.

---

## Anti-roadmap

Things explicitly NOT planned, even with infinite time:

- ❌ A native mobile app — PWA install on iOS/Android is good enough
- ❌ A built-in chat with Claude inside the PWA — the toolkit's value is in the structured workflow, not yet another chat box
- ❌ Resume parsing OCR for paper/scanned PDFs — out of scope; users provide text-based resumes
- ❌ LinkedIn API integration — terms-of-service hostile; not worth it
- ❌ "Auto-apply" features that submit applications — bad outcomes for users; we coach the application, the user submits

---

## Decision log

| Date | Decision | Rationale |
|---|---|---|
| 2026-05-02 | v0.1.0 stays personal/local | Faster to ship; SaaS pivot kept open via content/rendering separation |
| 2026-05-02 | Repo private at start | Path to public after first real successful run, with explicit Milan approval |
| 2026-05-02 | Single shared neutral icon for all PWAs | Simpler than per-app generation; brand consistency across applications |
| 2026-05-02 (revised) | **Two-tier repo strategy: private repo never public; public artifact is ONBOARDING.md** | Earlier plan was to flip private → public after first run. Revised after PII was discovered in the v0.1.0 baseline commit. Private repo can hold real Milan data permanently; public reach happens via a sanitized onboarding doc (and optionally a future public companion repo). See SPEC §13. |
| 2026-05-02 | Do NOT amend commit `49bc5be` | The original commit retains the unredacted resume fixture. Per the new repo strategy, this is fine — the repo is private and stays private. Working-tree redacted version remains for use as the active eval fixture. |
| 2026-05-02 | **Public companion repo confirmed (option b)** | Selected over single-doc and branch-based publish. New repo `ultimate-job-assistant-public` will hold sanitized skill code + templates + ONBOARDING + website source. Sync via allowlisted script with PII scanner; never automatic. See SPEC §13.1. |
| 2026-05-02 | **Public website: shape C, GitHub Pages, part of v0.1.0** | Landing page + multi-page docs site. Astro is the default stack (decision flips during Phase 7 design if MkDocs Material fits better). Live demo PWA (option D) deferred to v0.1.1. See SPEC §13.2 and Phase 7 in §14. |
| 2026-05-02 (Phase 7 design) | **Stack flipped from Astro to plain static HTML + Tailwind CDN** | Mirrors PWA-template philosophy. ~1 hr build vs 3+ for Astro. GitHub Pages serves directly with `upload-pages-artifact` + `deploy-pages`. |
| 2026-05-02 (post-v0.1.0 same day) | **noindex + robots.txt added** | Site stays live and public-repo-hosted but is invisible to search engines. Personal-toolkit note added to README. URL becomes the credential. |
| 2026-05-02 (post-v0.1.0 evening) | **Landing page simplified to download-first** | One primary CTA: "Download the latest". HEAD-fetch JS displays zip size + date. Documentation pages still exist but understated. |
| 2026-05-02 (final architecture revision) | **Both repos go private, hosting moves to Netlify, zip distribution** | Even with `noindex`, a public GitHub repo is still searchable on GitHub itself. Moving hosting from GitHub Pages to Netlify (free tier, reads private repos via OAuth) lets both repos go private while keeping the site live. The website exposes `/downloads/ultimate-job-assistant.zip` for anyone with the URL — that becomes the public artifact. Auto-sync via GitHub Action on the canonical private repo. Custom domain (~$12/yr) confirmed for v0.1.1. See SPEC §13 (current state) and §14 v0.1.1 phases 8-12. |

Append future decisions here as they're made.
