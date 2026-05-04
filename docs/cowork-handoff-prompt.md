You're picking up the Ultimate Job Assistant v2 project mid-stream. The Cowork worktree is at `/Users/Milan/code/uja-v2`; verify with `ls /Users/Milan/code/uja-v2/CLAUDE.md` before assuming. All referenced commits/branches/PRs are real and on origin (`sharmingmilan/ultimate-job-assistant-v2`).

CURRENT STATE

* `main` includes PR #8 — Phase 24.5 dispatch brief landed at `docs/session-13-brief.md`. Latest tag is `v0.2.1`.
* Phase 24 PR #7 still open against `main`, branch `phase24/export-pipeline` at `5879f3f`. Stacked under future Phase 25.
* Phase 25 brief temporarily moved to `docs/session-14-brief.md` on branch `docs/session-14-brief-draft` (will be re-edited post-ADR-003 later).
* Q6 (Phase 25 Block 4 test app) locked to `waymo-bi-analyst-2026-04`; full details in `docs/notes-q6-test-app-lock.md` (untracked, readable).

WHAT'S NEXT — Phase 24.5 research, executed INTERACTIVELY in this Cowork session (not dispatched). The dispatch pattern was abandoned in the previous session — all future sessions are Cowork interactive. The Phase 24.5 brief at `docs/session-13-brief.md` was written assuming a 4-5 hour autonomous dispatch; ignore the "autonomous agent" framing, treat it as the plan you and Milan execute together over 1-2 sessions.

Brief substance: 4 buckets of apps to research (trackers / AI tools / dashboards / indie hubs), R6 user reviews for ≥3 apps, R7 cross-domain outliers (Read.cv / Linktree / etc.), R5 cross-app copy voice subsection, Block 3 privacy messaging subsection, ≥80% screenshot coverage target. Output: `docs/phase24_5-app-space-research.md` on branch `phase24_5/research`. Feeds the next session's synthesis to `docs/ADR-003-visual-identity.md`.

LOCKED DECISIONS — do not re-debate

* 8th-grade reading level for all v2 site copy
* 4 buckets of reference apps (dev-tool brand pages dropped from original 5)
* R6 user reviews + R7 cross-domain outliers + R5 copy voice as cross-app subsection + privacy messaging subsection — all mandatory in the landscape doc
* Phase 25 stacks on `phase24/export-pipeline` branch, NOT `main`
* Phase 24 + Phase 25 ship as combined `v0.2.3` (skip v0.2.2)
* Waymo locked as Q6 test app at `/Users/Milan/Documents/Documents - Milan's MacBook Pro (Personal)/Claude/Ultimate Job Assistant`
* Cowork-artifact-route (Option 3) parked for post-v0.2.3 ADR-003 territory; static site work continues in v0.2.x

OPERATIONAL NOTES — load-bearing

* Cowork sandbox CAN'T read `.session-secrets/` — the credential pattern in CLAUDE.md is broken in Cowork (works in Dispatch). All git operations run from Milan's terminal via the manual block pattern. CLAUDE.md needs a Cowork caveat someday.
* `gh` CLI is broken (keyring token invalid). PR creation via `git credential fill | curl` REST API from Milan's terminal.
* GitHub MCP plugin's OAuth flow fails with "does not support dynamic client registration" — can't auto-push from Cowork. Manual only.
* PAT was leaked in Session 12 transcript; rotation deferred to post-deploy. Risk grows as sessions accumulate.
* Dispatch pattern abandoned per Milan's decision in Session 13. Don't suggest dispatching anything.

ORIENTATION FILES (read in this order before any work)

1. `/Users/Milan/code/uja-v2/CLAUDE.md` — project structure, working principles (HITL / Atomic / Deterministic / Evidence-based), credential pattern (note: broken in Cowork).
2. `/Users/Milan/code/uja-v2/SPEC.md` §14 — committed phase plan.
3. `/Users/Milan/code/uja-v2/docs/ADR-002-architecture-rethink.md` — v0.2.x architecture, §D4 visual style guardrails are load-bearing for v2 site work.
4. `/Users/Milan/code/uja-v2/SESSION_LOG.md` — most recent entries for predecessor context.
5. `/Users/Milan/code/uja-v2/docs/session-13-brief.md` — Phase 24.5 plan (execute interactively, ignore "autonomous" framing).
6. `/Users/Milan/code/uja-v2/docs/notes-q6-test-app-lock.md` — Q6 test-app confirmation.

PENDING WORK (across remaining sessions)

* Phase 24.5 research (active — this session, possibly next)
* Phase 24.5 design-language synthesis → `docs/ADR-003-visual-identity.md` (interactive)
* Phase 24.5 reference mockup
* Re-edit Phase 25 brief at `docs/session-14-brief.md` post-ADR-003
* Phase 25 implementation (now interactive, no longer dispatched)
* PR + merge Phase 24 + Phase 25 as combined v0.2.3
* Regenerate `docs/post-merge-wrap-v0.2.3.md`
* Live smoke checklists for Phase 24 + Phase 25 (human-driven Cowork-chat walkthroughs, NOT bash assertions)
* PAT rotation (deferred but still hanging)
* CLAUDE.md edit: flag that `.session-secrets/` credential pattern is broken in Cowork

USER PREFERENCES — non-procedural

* Milan is not the subject-matter expert; flag gaps and unconsidered angles proactively, especially in design / research / wording substance.
* Concrete actions over paragraphs of explanation. Numbered lists, copy-pasteable commands when terminal work is required.
* When asking clarifying questions, use AskUserQuestion with multi-choice options, not freeform prompts.
* All v2 site visible copy is 8th-grade reading level. Internal docs (briefs, ADRs, SESSION_LOG) stay at expert level.

START HERE

Read the orientation files above end-to-end. Then ask Milan: "Ready to start the Phase 24.5 research, or do you want to address one of the open architectural questions first?" Open architectural questions Milan flagged in Session 13 but didn't address: the screenshot ≥80% target may be unachievable, the time pressure of 4-5 sessions before any v2 site change, and the possibility that research concludes "nothing in this space looks like us" forcing first-principles design anyway.
