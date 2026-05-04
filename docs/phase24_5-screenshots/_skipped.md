# _skipped.md — binary-screenshot skip log (all 15)

**Status:** URL-only fallback per R4 is active for the entire 15-app list. No `<slug>.png` or `<slug>.jpg` files were committed to this directory. Each `<slug>-source.md` file remains as evidence of the Chrome browser agent's capture metadata (URL, view, method, retry notes), but the binary the agent rendered did not bridge from the Chrome conversation into the Cowork worktree.

**Why all 15 fell back:** Cowork bash is forbidden from URL fetching by the system prompt, so binaries cannot be downloaded server-side. The Chrome browser agent successfully captured 15/15 hero or in-product views on 2026-05-03 (image-IDs `ss_*` recorded in each `<slug>-source.md`'s view notes), but those image-IDs are scoped to the Chrome conversation's image storage and are not retrievable from the orchestrator's Cowork session. After the table of view metadata bridged successfully on the second relay, drag-drop of the binaries into Cowork chat was offered as the next bridge but Milan elected the URL-only fallback to ship Block 2-4 prose without further bridge-friction overhead.

**What the landscape doc uses instead:** every per-app section in `../phase24_5-app-space-research.md` carries a `**Screenshot:** [view title](URL)` line per R4's URL-only-fallback format. The synthesis session (Session 14) can paste any of those URLs into a browser to see the same hero or in-product surface the Chrome agent saw — the `<slug>-source.md` retry notes tell it exactly which tab / category / Wayback path to follow when an original URL has drifted (notably airtable-ats).

**Coverage delta vs Phase 24.5 success_criteria #2:** the target was ≥80% binary capture (≥12 of 15). Actual binary commit count was 0 of 15 — a full downgrade. This is documented here, in each per-app `<slug>-source.md`, and explicitly in the Block 5 PR description.

## Skip log

| Slug | Reason | URL-only fallback |
|---|---|---|
| huntr | binary-bridge unresolved | https://huntr.co/ |
| teal | binary-bridge unresolved | https://www.tealhq.com/ |
| simplify | binary-bridge unresolved | https://simplify.jobs/ |
| rezi | binary-bridge unresolved | https://www.rezi.ai/ |
| enhancv | binary-bridge unresolved | https://enhancv.com/ |
| jobscan | binary-bridge unresolved | https://www.jobscan.co/ |
| notion-job-tracker-official | binary-bridge unresolved | https://www.notion.com/templates/the-job-application-tracker-815 |
| notion-notinova | binary-bridge unresolved | https://www.notion.com/templates/application-traker-job-internship |
| airtable-ats | binary-bridge unresolved (URL drift recovered to simple-applicant-tracker template — see source.md) | https://www.airtable.com/templates/simple-applicant-tracker/exp1ozXL39xexSu2s |
| levelsio | binary-bridge unresolved | https://levels.io/projects/ |
| stephango | binary-bridge unresolved | https://stephango.com/ |
| rknight | binary-bridge unresolved | https://rknight.me/ |
| arena | binary-bridge unresolved | https://www.are.na/ |
| pinboard | binary-bridge unresolved | https://pinboard.in/ |
| hellocv | binary-bridge unresolved | https://hello.cv/ |
