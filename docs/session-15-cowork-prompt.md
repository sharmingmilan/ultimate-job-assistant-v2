# Session 15 Cowork prompt — pick up from ADR-003

This is the paste-ready prompt for the next Cowork session. Paste the block under "Paste-ready prompt" into a fresh Claude Desktop conversation to start Session 15. The prompt orients a new Claude on:

1. Where Session 14 left off (ADR-003 PR open or merged; Phase 24 PR #7 still open)
2. What to do first (review + merge ADR-003 if not yet merged; re-edit `docs/session-14-brief.md` to reflect ADR-003)
3. What comes after (Phase 25, stacked on `phase24/export-pipeline`)

The prompt is intentionally self-contained — works whether the next session is Cowork (interactive) or Code (Dispatch). The orientation file list is canonical; the new Claude follows it exactly.

---

## Paste-ready prompt

```
You're picking up the Ultimate Job Assistant v2 project at the start of Session 15.
The Cowork worktree is at /Users/Milan/code/uja-v2; verify with
`ls /Users/Milan/code/uja-v2/CLAUDE.md` before assuming.

REPO: sharmingmilan/ultimate-job-assistant-v2 (public)
PRIOR SESSION: Session 14 — ADR-003 synthesis (Cowork interactive).
  Three PRs landed in Session 14:
    - PR #9 (Phase 24.5 landscape doc, merged at 62dc805 via reflog-recovery sequence)
    - PR #10 (CLAUDE.md freshness pass, merged at c068251)
    - PR #<TBD-from-ADR-merge> (ADR-003 itself — may or may not be merged at session
      start; check via curl GET /pulls?state=all&head=sharmingmilan:adr-003/visual-identity)

OPEN PRS at session start (verify via curl):
  - PR #7 — Phase 24 export pipeline, branch phase24/export-pipeline at 5879f3f.
    Open against main, ~5 commits, 87 tests passing per Session 12 brief. Phase 25
    stacks on top of this; both ship as combined v0.2.3.
  - PR #<TBD> — ADR-003 visual identity, branch adr-003/visual-identity. May or may
    not be merged at session start (see SESSION_LOG Session 14 entry for state).

ORIENTATION (read in this order):
  1. CLAUDE.md — project structure, working principles (HITL / Atomic / Deterministic /
     Evidence-based), Cowork session workflow (load-bearing — sandbox can't write to
     .git/, all git operations from your terminal via prepared blocks).
  2. SPEC.md §14 — committed phase plan; Phase 25 row.
  3. docs/ADR-002-architecture-rethink.md §D4 — visual style guardrails ADR-003 extends.
  4. docs/ADR-003-visual-identity.md — eight decisions for v2 site visual identity.
     Read end-to-end. The Decisions section + Cross-decision interactions are
     load-bearing for Phase 25 implementation.
  5. docs/phase24_5-app-space-research.md — landscape evidence ADR-003 cites.
     Skim; reference back when needed.
  6. SESSION_LOG.md — Session 11 (Phase 23 / v0.2.1) and Session 14 (ADR-003).
     Sessions 12 + 13 entries may be missing if Block 5 of Session 14 didn't land.
  7. docs/session-14-brief.md (on branch docs/session-14-brief-draft, may have been
     merged + re-edited by Session 14 Block 5) — the Phase 25 brief.

WHAT'S NEXT:
  1. If ADR-003 PR is open: review it. Surface concerns; otherwise propose merge with
     --no-ff. Once Milan approves, run the merge from his terminal via the standard
     prepared-block pattern.
  2. If docs/session-14-brief.md was NOT re-edited in Session 14 Block 5 to reflect
     ADR-003: re-edit now. The brief currently predates the ADR and references
     "Canva MCP visual exploration first" as Phase 25 Block 1 — that's superseded by
     ADR-003. Replace Block 1 with "ADR-003 implementation pass: light-variant palette,
     theme toggle, About page, copy review." Open as a separate PR off main.
  3. Once both ADR-003 and the re-edited brief are merged: start Phase 25 per the
     re-edited brief. Phase 25 stacks on phase24/export-pipeline (PR #7) — branch from
     it, not from main. Phase 24 + 25 ship as combined v0.2.3.

LOCKED DECISIONS (do not re-debate):
  - ADR-003 D1-D8 are locked design decisions for the v2 site
  - 8th-grade reading level for v2 site visible copy (Session 13 lock)
  - Slate-950 dark default + light variant via prefers-color-scheme + explicit toggle
    (D2 — extends ADR-002 §D4)
  - About page is load-bearing (only place context + privacy posture lives)
  - Phase 25 stacks on phase24/export-pipeline; combined ship as v0.2.3
  - Cowork-artifact tracker UI parked for post-v0.2.3 ADR territory
  - Dispatch pattern abandoned per Session 13 — all sessions are interactive Cowork

OPERATIONAL NOTES (load-bearing):
  - Cowork session workflow per CLAUDE.md "Credential handling pattern":
    Claude prepares git blocks as terminal-paste copy; you (Milan) run them. Sandbox
    bash cannot write to .git/. PRs open + merge via curl REST API (gh CLI broken
    on Milan's machine).
  - PAT location: /Users/Milan/Documents/Documents - Milan's MacBook Pro
    (Personal)/Claude/pats — fine-grained PAT on line 2.
  - Repo is public; PAT still controls write access. Standard stderr-redaction
    pattern applies as defense in depth, not as PII protection.
  - If a stale .git/index.lock blocks a commit, run `rm .git/index.lock` from
    Milan's terminal first (the sandbox can't clean it up).

START HERE:
  1. Read the orientation files end-to-end
  2. Verify state of PR #7 (Phase 24) and ADR-003 PR via curl GET to GitHub API
  3. Summarize what changed in Session 14 in 5-7 bullets
  4. Propose the next action plan and confirm with Milan before any git operations
```

---

## Notes for Milan

- Paste the block above into the first message of a fresh Cowork session. Claude will read the orientation files and propose the next move.
- If ADR-003 was merged before the new session opens (i.e., you ran the merge block at the end of Session 14 — see SESSION_LOG Session 14 entry), the new Claude will skip step 1 and go straight to re-editing the Phase 25 brief.
- If you want to resume mid-Phase-25 instead of starting fresh, replace the `WHAT'S NEXT` block with the specific Phase 25 sub-step you're picking up from. The orientation file list stays the same.
- The prompt deliberately does NOT carry the Q1-Q8 synthesis content — that lives in `docs/ADR-003-visual-identity.md`. The new Claude reads the ADR; the prompt stays compact.

---

*End of session-15 Cowork prompt.*
