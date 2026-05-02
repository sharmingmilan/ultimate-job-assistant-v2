# Netflix Interview Prep — Reference Build

This folder contains the documents from the original Netflix Interview Prep project, preserved as the canonical reference for the `interview-prep` skill. The skill in this project is a generalization of that build.

## What's in this folder

| File | Purpose |
|---|---|
| `SPECS.md` | The product specification for the Netflix prep app — what it is, why it's that way, what it deliberately is not. Written by the original Claude session. Treat as the design north star for any new build. |
| `NETFLIX_PROJECT_NOTES.md` | Originally the Netflix project's own `CLAUDE.md` — internal working notes from the build sessions. Useful for understanding tradeoffs that aren't visible in the final artifact (Tailwind CDN gotchas, Babel-standalone quirks, str_replace pitfalls in long files). |
| `README_USER_FACING.md` | The user-facing README that shipped with the Netflix prep PWA — Milan reads this on the deployed site. Useful as a template for the README the skill generates per application. |

## What is NOT in this folder

- **The actual built `index.html`** — at ~344 KB it's not a useful reference (it's a build artifact, not a spec). The shape it took is described in `SPECS.md` §5 and `NETFLIX_PROJECT_NOTES.md` §6.
- **`netflix-sql-prep.jsx`** — the source JSX (~5500 lines). Heavy and Netflix-specific. The skill recreates the structural patterns generically; reading the original line-by-line isn't necessary.
- **The original PWA assets** (icon, manifest, sw.js) — UJA uses its own neutral icons and a templated manifest.

## How to use these references

When generating content in Phase D of the skill workflow:

1. Open `SPECS.md` §6 ("Content authorship guidelines") for the rules on what makes a good worked example, faded scaffold, and retrieval problem
2. Open `SPECS.md` §3 ("Pedagogical model") for the mapping from learning-science principles to the three-phase loop
3. Open `NETFLIX_PROJECT_NOTES.md` §4 ("Content architecture inside app.jsx") for how the original organized content data structures — the new template uses a similar (but more clearly separated) approach via `content.json`

When generating the PWA in Phase F:

1. `NETFLIX_PROJECT_NOTES.md` §6 ("The SQL editor") explains the editor implementation approach
2. `NETFLIX_PROJECT_NOTES.md` §7 ("Deployment model") explains the single-file CDN approach and why
3. `NETFLIX_PROJECT_NOTES.md` §10 ("Testing template") gives the Playwright smoke-test pattern

## What changed in the generalization

The Netflix project hard-coded its content into `app.jsx`. The new skill separates concerns:

```
content.json    ← all problems, walkthroughs, real-questions tab
app.jsx         ← rendering only (reads content.json at build time)
```

This means a future SaaS pivot or a CMS-backed content layer doesn't require rewriting React.

## Provenance

These docs were authored during the original Netflix prep build (April 2026 sessions 1–4). They are preserved here without modification. If they conflict with this project's `SPEC.md`, this project's SPEC wins.
