# Session 10 brief — Phase 22.5 (deprecation marking)

**Target:** mark the chat-style frontend + agent-loop-in-host modules as deprecated per ADR-002 D3, and demote the OS-keychain + auth modules. No code is deleted; everything stays on `main` as a working reference. No version bump.

**Estimated time:** 30-45 minutes. This is also a deliberate small test of the Dispatch-session pattern before Session 11 (Phase 23 MCP server) commits to a longer Dispatch run.

**Surface:** intended for a Claude Code Dispatch session launched via `bash scripts/dispatch-session.sh 10`. Equally executable from a regular Cowork session — the brief makes no surface-specific assumptions.

---

## You are an autonomous Phase 22.5 implementation agent

You are not waiting for the originating Cowork session to approve every micro-decision. You are the planner, executor, evaluator, and quality gate. The brief tells you exactly what "done" looks like; you decide how to get there atomically and deterministically.

If something genuinely blocks you (e.g. a file referenced here doesn't exist, or a CLAUDE.md working principle conflicts with a brief instruction), surface that and ask before improvising.

---

## Orientation — read in this order before any edits

1. **`CLAUDE.md`** — project structure, working principles (HITL / Atomic / Deterministic / Evidence-based), credential handling pattern, doc freshness protocol.
2. **`SPEC.md` §14** — committed phase plan. You are implementing **Phase 22.5**. Phase 23 (the MCP server itself) is Session 11; do not start Phase 23 work in this session.
3. **`docs/ADR-002-architecture-rethink.md` §D3** — the source of truth for which files survive, which are demoted, which are deprecated-as-reference. The "Repository layout post-rethink" tables in D3 enumerate every file's fate.
4. **`SESSION_LOG.md` Session 9 entry** — the immediate predecessor work (ADR-002 ship + v0.2.0 tag). Confirms what's already on disk.
5. **The files you'll be editing** (read each before annotating):
   - `host/frontend/` — entire Vite/React tree. You're adding a `README.md` here, not editing source.
   - `host/uja_host/main.py` — FastAPI entrypoint.
   - `host/uja_host/api/chat.py` — the deprecated agent loop.
   - `host/uja_host/api/conversations.py` — the deprecated conversation history surface.
   - `host/uja_host/keystore.py` — OS keychain wrapper.
   - `host/uja_host/api/auth.py` — API key write endpoint.

You do **not** need to read SKILL.md files, the test suite, or the rest of `host/uja_host/` for this session. Phase 22.5 is purely annotation; no behavioral changes.

---

## Deliverable — one atomic commit, one PR

### Block A — `host/frontend/README.md` (net-new file)

Create `host/frontend/README.md` containing:

- A "Deprecated reference" header (clearly marks the directory's status).
- Two-paragraph explanation:
  - Paragraph 1: what this code IS (the chat-style frontend shipped in Phase 17 + 17.5; React + Vite + Tailwind + shadcn/ui; three tabs + onboarding).
  - Paragraph 2: why it's preserved (HITL UX patterns in `ChatTab.tsx` — `PendingChangeSet`, `PendingQuestion`, `streamTurn` / `resumeStream`, `toolResultByUseId` correlation — are the cleanest extant demonstration of the HITL contract; v0.4.0's workflow tracker will need the same patterns in a different visual frame).
- A "Status" section: not maintained; not part of release artifacts; runnable locally via `npm install && npm run build` for inspection.
- A "See also" footer pointing at `docs/ADR-002-architecture-rethink.md` §D1 (the new architecture) and §D3 (the file-fate categorization).

Keep it under 60 lines. Plain markdown. No emoji. No marketing voice.

### Block B — Docstring headers on deprecated modules

For each of these three files, prepend a docstring header that:

1. Marks the module as deprecated per ADR-002 D3.
2. States what replaces it in the v0.2.x architecture.
3. Notes that the module is preserved as a working reference, not maintained.

Files + replacement pointers:

- `host/uja_host/main.py` → "deprecated; see `host/uja_mcp/server.py` (added in v0.2.1)"
- `host/uja_host/api/chat.py` → "deprecated; the agent loop now lives in Cowork. The MCP server (`host/uja_mcp/`) exposes tools; Cowork drives the loop."
- `host/uja_host/api/conversations.py` → "deprecated; conversation history is no longer a host-side concern in v0.2.x."

Keep each header to 4-8 lines. Place ABOVE any existing module docstring (or replace the existing one if it predates ADR-002). Make sure imports + behavior are unchanged.

### Block C — Demotion docstrings on `keystore.py` + `api/auth.py`

These two modules survive but are demoted (per ADR-002 D3 "Survives but demoted" table). Update their module docstrings to explicitly state:

- `host/uja_host/keystore.py` → "Demoted. OS keychain wrapper. No longer load-bearing in v0.2.x (Pivot C — Cowork holds the user's auth, not a per-user Anthropic API key). Kept in case a future tool needs a credential store (e.g. headless export mode per ADR-002 §Phasing impact / v0.3.0 reframings). Not part of the default MCP tool surface."
- `host/uja_host/api/auth.py` → "Demoted. API-key write endpoint. Kept for a possible future headless export mode per ADR-002 §Phasing impact. Not registered on the default MCP tool surface in v0.2.x; surfaces a 410 Gone if hit through the legacy FastAPI surface."

Keep behavior unchanged. Existing functions, models, and routes stay intact.

---

## Working principles (verbatim from CLAUDE.md — non-negotiable)

- **Human-in-the-loop.** If you discover ambiguity in the brief or the ADR, ask before improvising.
- **Atomic.** All Phase 22.5 changes go in **one** commit on a feature branch. Reverting Phase 22.5 should be a one-command operation.
- **Deterministic.** No timestamps in committed artifacts. No churn unrelated to the deprecation marking.
- **Evidence-based.** Every claim in the new docstrings should be traceable to ADR-002 D3 (cite the section).

---

## Branch + PR mechanics

- Branch: `phase22.5/deprecation-marking`.
- Commit message follows the project pattern (subject line ≤ 72 chars; body explains what + why; reference ADR-002 D3).
- Open a PR titled "Phase 22.5: deprecation marking per ADR-002 D3" against `main`.
- PR body: bullet list of every file touched + a one-line rationale per file. Link to ADR-002 D3.
- **Do not merge yourself.** The originating Cowork session reviews + merges (preserves the `--no-ff` merge-commit pattern + the human-in-the-loop principle).

If you cannot push to a feature branch on the canonical (network or auth issue), output the patch (`git format-patch main..HEAD --stdout`) at the end of your session so the Cowork session can apply it.

---

## Success criteria

The PR lands when ALL of the following hold:

1. `host/frontend/README.md` exists, ≤60 lines, plain markdown, follows the Block A spec.
2. The three deprecated-module docstrings are present, follow the Block B spec, and the modules' behavior is unchanged (`grep -n "^def \|^async def \|^class \|^router\." host/uja_host/api/chat.py` returns the same line count it does now).
3. The two demotion docstrings are present per Block C.
4. `pytest` passes 36 tests (no regressions; you didn't change behavior).
5. `git log --oneline -1` shows one commit with a clear ADR-002-D3-referencing message.
6. The PR is open and ready for the Cowork session to review.

---

## End-of-session deliverables (in your final message back)

1. The PR URL.
2. A 5-bullet summary of what landed (one per file touched + the README).
3. The exact `pytest` output line count.
4. Any ambiguity you resolved on your own + the rationale (in case the Cowork session disagrees).
5. The commit SHA(s).

No CLAUDE.md / SESSION_LOG update from you — those land in the Cowork session's wrap after the PR merges. Phase 22.5 is annotation-only; the SESSION_LOG entry can be one paragraph.

---

## Out of scope for this session

- The MCP server itself (`host/uja_mcp/`) — Phase 23, Session 11.
- Any test changes — Phase 22.5 doesn't change behavior, so tests don't need updates.
- Deleting any of the deprecated files — ADR-002 D3 explicitly says "deletions are reversible decisions to defer; we'll re-evaluate in 1-2 sessions of v0.2.x work."
- The `export_application` MCP tool — Phase 24.
- Touching v1 canonical or v1 deploy-source.
- Touching v2 deploy-source (Pivot B reframe is a separate session).

---

*End of brief.*
