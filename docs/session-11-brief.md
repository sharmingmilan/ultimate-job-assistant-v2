# Session 11 brief — Phase 23 (MCP server scaffold, target v0.2.1)

**Target:** stand up `host/uja_mcp/server.py` (a JSON-RPC-over-stdio MCP server) exposing the ADR-002 D1 tool surface. Re-point the existing 36-test suite at MCP tool functions. Ship a launcher + Cowork-config snippet. Tag `v0.2.1` end of session.

**Estimated time:** 3-4 hours. Substantial but bounded — same shape as Phases 15 / 16 / 17 in their respective sessions (Sessions 5 / 6 / 7).

**Surface:** intended for a Claude Code Dispatch session launched via `bash scripts/dispatch-session.sh 11`. Equally executable from a regular Cowork session.

**Prerequisite:** Session 10 (Phase 22.5 deprecation marking) must have shipped first. The deprecation docstrings are reference points the new MCP modules will link back to.

---

## You are an autonomous Phase 23 implementation agent

You are not waiting for the originating Cowork session to approve every micro-decision. You are the planner, executor, evaluator, and quality gate. Drive Phase 23 to a tagged `v0.2.1` release.

If something genuinely blocks you (ambiguous spec, MCP SDK behavior that conflicts with the brief, test that won't port cleanly), surface it and ask. Do not improvise around the ADR; do improvise around incidental issues.

---

## Orientation — read in this order before any code

1. **`CLAUDE.md`** — project structure, working principles, credential handling pattern, doc freshness protocol. The "Working Principles" section is non-negotiable.
2. **`SPEC.md` §14** — committed phase plan. You are implementing **Phase 23**. Phase 24 (export pipeline) is the next session; do not start Phase 24 work in this session.
3. **`docs/ADR-002-architecture-rethink.md`** — the architecture you are implementing.
   - **§D1** for the tool surface table (what tools register, where each one comes from).
   - **§D3** for the file layout (Survives / Demoted / Deprecated / Net-new tables).
   - **§Phasing impact** for v0.3.0 status (parked; do not start Tauri work).
4. **`SESSION_LOG.md` Sessions 9 + 10 entries** — Session 9 = ADR-002 ship + v0.2.0 tag; Session 10 = Phase 22.5 deprecation marking.
5. **`mcp-builder` skill** (Anthropic-authored, in your installed skills) — this is **load-bearing**. Read its SKILL.md before writing any server code. It is the authoritative source on MCP server patterns in Python (FastMCP recommended; alternative is the MCP SDK low-level API). Use whatever idiom the skill recommends.
6. **The surviving modules the new MCP tools wrap** (read each before writing the facade):
   - `host/uja_host/sandbox.py` (`resolve_within_root`, `SandboxViolation`)
   - `host/uja_host/db.py` (full schema; you'll touch `pending_changes` + `pending_questions`)
   - `host/uja_host/config.py` (project root + `~/.uja/config.json`)
   - `host/uja_host/tools/file_tools.py` (read/write/edit/list/metadata)
   - `host/uja_host/tools/skill_tools.py` (`propose_changes`, `ask_user`)
   - `host/uja_host/tools/skill_registry.py` (`list_skills`, `get_skill`)
   - `host/uja_host/api/changes.py` (HITL approve/reject logic — re-export as MCP tools)
   - `host/uja_host/api/questions.py` (HITL answer logic — re-export as MCP tool)
7. **The current test suite** to understand what to port:
   - `host/tests/test_phase15_acceptance.py`
   - `host/tests/test_phase16_skill_registry.py`
   - `host/tests/test_phase17_5.py`
   - `host/tests/integration/test_phase16_smoke.py`

You may skip `host/uja_host/api/chat.py` and `host/uja_host/api/conversations.py` — they're deprecated (Phase 22.5 marked them).

---

## Deliverable — Block-by-Block

### Block 1 — Pin `mcp` SDK + create the package skeleton

- Add `mcp` to `host/requirements.txt` with a pinned version (per the `mcp-builder` skill's recommendation; pin to a specific minor).
- `host/uja_mcp/__init__.py` (package marker, version constant matching `host/uja_host/__init__.py`).
- `host/uja_mcp/tools/__init__.py` (subpackage marker).
- Atomic commit on branch `phase23/mcp-server`.

### Block 2 — Tool facades

For each MCP tool in the ADR-002 D1 table, write a thin facade in `host/uja_mcp/tools/`:

- **`host/uja_mcp/tools/files.py`** — `read_file`, `write_file`, `edit_file`, `list_files`, `read_workspace_metadata`. Each wraps the same-named function from `host/uja_host/tools/file_tools.py` with MCP type signatures + the SDK's `@tool` decorator.
- **`host/uja_mcp/tools/skills.py`** — `list_skills`, `read_skill`. Wraps `host/uja_host/tools/skill_registry.py` (`list_skills` + `get_skill`). Note: `run_skill` from Phase 16 is split into these two per ADR-002 D1's MCP-idiomatic tool shape.
- **`host/uja_mcp/tools/hitl.py`** — `propose_changes`, `approve_changes`, `reject_changes`, `ask_user`, `answer_question`. Pulls from `host/uja_host/tools/skill_tools.py` (the `propose_changes` + `ask_user` persistence) and from `host/uja_host/api/changes.py` + `host/uja_host/api/questions.py` (the approve/reject/answer business logic — extract pure functions if the current code is route-shaped; the FastAPI route handlers can stay as-is in the deprecated tree).

Each facade gets a 4-6 line module docstring explaining what it wraps + why this layer exists (ADR-002 D1 — MCP boundary; logic stays in `host/uja_host/`).

Each tool function:
- Resolves the project root via `host_config.get_project_root()` exactly as the FastAPI handlers do today.
- Raises `ToolError` for bad inputs (the dispatcher converts to `is_error=True`); the MCP SDK should already plumb this correctly — verify against the `mcp-builder` skill.
- Returns the same shapes the FastAPI endpoints return today (so the test fixtures port unchanged).

Atomic commit per file (or one commit if you prefer; both are fine — atomic = "logical change", not "file-per-commit").

**Important — `export_application` is Phase 24, NOT Phase 23.** Do not implement it. Leave a placeholder note in `tools/__init__.py` comments if helpful.

### Block 3 — `host/uja_mcp/server.py` (the entry point)

- JSON-RPC over stdio. Use whatever entrypoint pattern the `mcp-builder` skill prescribes (likely `mcp.server.stdio.stdio_server()` for the SDK or `FastMCP().run()` for FastMCP).
- Register every tool from the three facade modules.
- A `__main__` block that lets `python -m uja_mcp.server` work.
- Log to stderr (stdio is reserved for the protocol). Log level configurable via `UJA_MCP_LOG_LEVEL` env var; default INFO.
- Module docstring at top: what this is, who launches it (the start scripts; Cowork's MCP config), the project-root contract (read from `~/.uja/config.json` or `UJA_PROJECT_ROOT` env var), the tool surface (link to ADR-002 D1).

Atomic commit.

### Block 4 — Test re-targeting + new MCP-protocol tests

- Re-point `test_phase15_acceptance.py` + `test_phase16_skill_registry.py` + `test_phase17_5.py` at the MCP tool functions instead of `TestClient` routes. Keep the same fixture pattern (monkeypatched `host_config.get_project_root` + `tmp_path`-rooted SQLite). The assertions should mostly survive verbatim — what changes is the call site, not the contract.
- Add `host/tests/test_mcp_server.py`: protocol-level tests covering the MCP `initialize` handshake, the `tools/list` response shape, a happy-path `tools/call` for one file tool + one HITL tool, and the error-shape contract (`is_error: true` for invalid args).
- Acceptance gate: `pytest -q` reports **36 or more passing tests, 0 failed** (was 36/36 pre-Phase-23; new MCP-protocol tests bump the count).
- Atomic commit.

### Block 5 — Launcher + Cowork-config snippet

- `start-uja-mcp.sh` (bash, macOS/Linux):
  - Verify Python 3.11+. If missing, print a friendly error and exit 1.
  - If `host/.venv-mcp/` doesn't exist, create it via `python3 -m venv` and `pip install -r host/requirements.txt`.
  - Print: the exact `python -m uja_mcp.server` command + the `cowork-mcp-config-snippet.json` content with the project root path filled in.
  - Do NOT auto-launch the server (the user needs to register it in Cowork's MCP config; the script is informational).
- `start-uja-mcp.bat` (Windows equivalent).
- `references/cowork-mcp-config-snippet.json` (template; the launcher fills in the project root). Format follows whatever Cowork's MCP-server registration shape is — check the `mcp-builder` skill or the Anthropic docs if unsure.

Atomic commit.

### Block 6 — Live Cowork session smoke test (the user runs this)

- Wait — this block depends on the originating user (Milan) running the launcher and registering the MCP server in Cowork.
- Your responsibility: write the smoke-test prompt the user pastes into Cowork to verify the registration. Place it in `host/tests/live_smoke_phase23.md` (markdown checklist — register MCP, test tools/list, test one read_file, test one ask_user, test one propose_changes + approve_changes round-trip).
- Atomic commit.

### Block 7 — Tag v0.2.1

- After all PRs merge to `main`, tag `v0.2.1` against the merge commit:
  - Annotated tag: `v0.2.1 — Phase 23 MCP server scaffold (host/uja_mcp/, JSON-RPC over stdio, ADR-002 D1 tool surface)`.
  - Release message lists the new tools, the test count delta, and points at `docs/session-11-brief.md` for context.
- Push the tag.

---

## Working principles (verbatim from CLAUDE.md — non-negotiable)

- **Human-in-the-loop.** Block 6 is genuinely blocked on the user; surface that and wait. Anywhere else, decide and ship.
- **Atomic.** One logical change per commit. Each Block above maps to one or two commits, not five.
- **Deterministic.** Pinned `mcp` version. No timestamps in artifacts. Tests use fixed fixtures.
- **Evidence-based.** Every code-shape decision should trace to either ADR-002 §D1/§D3 or the `mcp-builder` skill's SKILL.md.

---

## Branch + PR mechanics

- One feature branch per Block (or per logical group of Blocks): `phase23/mcp-scaffold`, `phase23/test-retarget`, `phase23/launcher`, `phase23/live-smoke`. Or one umbrella branch `phase23/mcp-server` with multiple atomic commits, then one PR. Either is fine; the choice is yours based on which is easier to review.
- PR titles: `Phase 23: <Block summary>`.
- PR body per PR: bullet list of files touched + a one-line rationale + acceptance-gate confirmation (`pytest` output line count, MCP server starts cleanly).
- **Do not merge yourself.** The originating Cowork session reviews + merges with `--no-ff`.
- **Do not tag yourself.** The Cowork session cuts the `v0.2.1` tag after the final PR merges (preserves the human-in-the-loop principle for releases).

If you cannot push to feature branches (network or auth issue), output `git format-patch main..HEAD --stdout` for each branch at end of session.

---

## Success criteria

`v0.2.1` ships when ALL of the following hold:

1. `host/uja_mcp/{__init__.py, server.py, tools/{__init__.py, files.py, skills.py, hitl.py}}` all exist and follow the Block 2-3 specs.
2. `mcp` is pinned in `host/requirements.txt`.
3. `python -m uja_mcp.server` launches cleanly (exits cleanly on Ctrl-C or stdin close).
4. `pytest -q` reports 36+ passing tests, 0 failed.
5. `start-uja-mcp.sh` runs cleanly on a fresh checkout (test on macOS); prints the registration snippet.
6. `references/cowork-mcp-config-snippet.json` exists with the right shape for Cowork's MCP-server registration.
7. `host/tests/live_smoke_phase23.md` exists with the user-facing smoke checklist.
8. ADR-002 D1's tool surface is fully covered (12 tools registered; `export_application` deferred to Phase 24 with a comment).
9. The deprecated tree (`host/uja_host/api/chat.py`, `conversations.py`, `host/frontend/`) is unchanged from Session 10.
10. PRs are open + ready for review; tag is cut by the originating Cowork session after merge.

---

## End-of-session deliverables (in your final message back)

1. PR URLs (one per branch).
2. Block-by-block summary of what landed, with commit SHAs.
3. The `pytest -q` output line count + the test file that grew (`test_mcp_server.py`).
4. Confirmation `python -m uja_mcp.server` boots cleanly (output the first few stderr log lines).
5. The `start-uja-mcp.sh` printed registration snippet (paste verbatim so the user can copy it).
6. Any ambiguity you resolved on your own + the rationale.
7. A note flagging Phase 24 as the next session's work + any architectural surprises that should inform Phase 24's brief.

---

## Out of scope for this session

- `export_application` (Phase 24).
- The v2 site rebuild (Phase 25).
- The v0.4.0 workflow tracker artifact (Track 7).
- Deleting any deprecated files.
- Touching v1 canonical or v1 deploy-source.
- Touching v2 deploy-source.
- ADR-003 (the v0.3.0 reframe).
- Any Tauri work.

---

*End of brief.*
