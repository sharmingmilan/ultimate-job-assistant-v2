# Q6 — Test app lock for Phase 25 Block 4 smoke

**Locked:** Session 13 prep (May 3 2026). Confirmed by orchestrator (Milan).

## Identifier

`waymo-bi-analyst-2026-04`

## UJA_PROJECT_ROOT

`/Users/Milan/Documents/Documents - Milan's MacBook Pro (Personal)/Claude/Ultimate Job Assistant`

## Why Waymo

- Tracker tags as "gold-standard reference, full lifecycle test (Steps 1-10)".
- All output types validated and present:
  - `decoded-jds/waymo-bi-analyst-2026-04.md`
  - `resumes/waymo-bi-analyst-2026-04.docx` + `.pdf`
  - `scores/waymo-bi-analyst-2026-04-before.md` + `-after.md`
  - `speaking-points/waymo-bi-analyst-2026-04.md` + `.pdf`
  - `cover-letters/waymo-bi-analyst-2026-04.md` + `.pdf`
  - `portfolio/waymo-bi-analyst-2026-04/` (~620 KB — A/B test analysis)
  - `networking/outreach-harsh-shah-waymo.md`
- Cleanest fixture (no recruiter-stage edge cases like Netflix's thank-you-letter follow-up).
- Compressed zip ~150 KB — fast smoke, low noise.

## Alternative considered

`netflix-data-analyst-2026-04` was second choice. More recent activity, bigger portfolio (1.1 MB Jupyter notebook), exercises the export tool harder. Rejected for Block 4 smoke because (a) Waymo is the canonical reference per tracker.md, (b) Netflix's portfolio bloat adds noise without changing what the smoke validates.

## Action for Session 16 (Phase 25 brief re-edit post-ADR-003)

When re-editing the Phase 25 dispatch brief (currently at `docs/session-14-brief-draft.md` on `docs/session-14-brief-draft` branch), bake in:

```
For Block 4 end-to-end smoke, the dispatch agent runs:

  export_application(
    company_role="waymo-bi-analyst-2026-04",
    project_root="/Users/Milan/Documents/Documents - Milan's MacBook Pro (Personal)/Claude/Ultimate Job Assistant",
    status="interviewing"
  )

Verifies the produced index.json row appears in the rendered card on
file://...website/v2/index.html. Re-runs with status="offer"; verifies the
card updates in place.
```

Replace the brief's current placeholder text ("Netflix or Waymo from `references/examples/` if those still exist; if not, hand-craft a minimum-viable `decoded-jds/` + `resumes/` pair").

## Source of confirmation

Session 13 prep, AskUserQuestion answer May 3 2026.
