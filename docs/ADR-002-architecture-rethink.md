# ADR-002 — v0.2.0+ architecture rethink (post-Pivots A/B/C)

**Status:** Accepted
**Date:** 2026-05-03 (Session 9)
**Decision-makers:** Milan (product owner), Claude (cowork mode session)
**Branch:** `adr/v0.2.0-rethink`
**Supersedes (in part):** ADR-001 §D1, §D2, §D3, §D6, §D8, §D10
**Preserves (without change):** ADR-001 §D4, §D5, §D7, §D9

---

## Context

Three strategic pivots locked in Session 8 (2026-05-03; see `SESSION_LOG.md` Session 8 entry and `ROADMAP.md` Decision log) reshape what v0.2.0+ should be. The original v0.2.0 plan from ADR-001 — a self-hosted local web app where the user runs UJA in a browser against their own Anthropic API key — was paused mid-flight after Phase 17.5 shipped. ADR-002 records the decisions that resolve the pause.

The three pivots, briefly:

- **Pivot A (chat-style UI is the wrong metaphor).** Discovered live in Session 8 testing: the chat tab works end-to-end, but a free-flowing chat is the wrong shape for orchestrated multi-step work. Agent loops mid-stream are visually overwhelming, HITL approve cards are decoupled from the workflow state they modify, and there's no "where am I in the process" surface. v0.4.0 will be a Sims-style structured workflow tracker. Chat becomes a sidecar.

- **Pivot B (v2 site reframes from marketing landing to exportable-package delivery hub).** The v2 Netlify site stops being about distributing the local web app. It becomes a static delivery layer for completed exportable application packages — one zip per company-role, sendable to recruiters, archivable, shareable. URL-only access (search-invisible, per the v1 pattern). "Exportable" is the load-bearing word: these zips exist to leave the site.

- **Pivot C (the local web app + per-user Anthropic API key is being deprecated).** The Cowork audience already has Claude desktop access via subscription. Asking that audience to also paste a paid Anthropic key into a separate local app is friction with no payoff. The workflow stays in Cowork; local infrastructure exists for tooling (file ops, sandbox, persistence) — not for running the agent loop.

Reusable infrastructure that survives all three pivots and gets carried forward (already shipped, 36 passing tests):

- FastAPI backend skeleton (`host/uja_host/`)
- Sandbox helper + `resolve_within_root` (`sandbox.py`)
- File API (`api/files.py`)
- Persistence layer (`db.py` schema v2, append-only)
- OS keychain wrapper (`keystore.py`) — semi-orphaned per Pivot C; kept for the moment, fate revisited in D3
- `propose_changes` and `ask_user` primitives (`tools/skill_tools.py`)
- HITL endpoints (`api/changes.py`, `api/questions.py`)
- Skills-as-Tools registry (`tools/skill_registry.py`)
- Test fixtures pattern (TestClient + monkeypatched config + tmp_path-rooted SQLite)

ADR-002 answers four questions, one per Decision below. Each question maps to the brief enumerated in `SPEC.md` §14 "v0.2.0 plan PAUSED" block.

---

## Quality bar

ADR-001's quality bar still applies — same standard, different surfaces. v0.2.x ships polished, not as MVP. Concretely, post-rethink that means:

- The MCP server (D1) ships with empty / loading / error states surfaced through MCP responses (clear `is_error: true` payloads with actionable messages, not opaque tracebacks). MCP clients render whatever they render; the server's job is to give them honest material.
- Documentation gets the same treatment as code: every connector, every tool, every export step gets a one-paragraph "what / why / when" so a forker can wire it up without reading source.
- The v2 site (D4) gets a deliberate visual pass — Canva MCP exploration before building, not after. Match the v0.4.0 workflow-tracker aesthetic.
- The export pipeline (D4) is deterministic: same inputs → identical zip bytes (modulo ZIP timestamps, which are zeroed). Re-runnable. Re-shareable.

Same quality bar that ADR-001 set; new surfaces inherit it.

---

## Decisions

### D1 — Architecture: Pure Cowork + thin MCP server

**Decision:** The "agent-loop-in-host" pattern is retired. The new runtime is:

- **Agent loop:** lives in Cowork (Claude desktop). The user already has Claude access via subscription; we don't reinstantiate it.
- **Project folder:** stays as a plain directory on the user's filesystem. Same shape as today (`skills/`, `references/`, `decoded-jds/`, `resumes/`, `scores/`, `speaking-points/`, `cover-letters/`, `interview-prep/`, `portfolio/`, `networking/`, `archive/`, `memory.md`, `tracker.md`).
- **Local thin MCP server:** a small Python process the user launches once per project. It exposes a focused tool surface to Cowork via the Model Context Protocol — sandbox-bounded file ops, the `propose_changes` and `ask_user` primitives shipped in Phase 16, the export pipeline from D4, and the workspace metadata read. No HTTP frontend. No SSE chat stream. No SPA static-files mount. No per-user Anthropic API key.
- **Workflow UI (v0.4.0):** rendered as Cowork artifacts — interactive HTML the workflow tracker emits that calls back into the same MCP server through `window.cowork.callMcpTool(name, args)`. Per the system prompt's Artifacts section, this is the supported pattern for "live, persisted HTML views" and is exactly the shape v0.4.0 needs.

**Why this beats the alternatives:**

- (a) "Local host as MCP server with native UI" — keeps an HTTP backend for the workflow tracker. Strictly more moving parts than (c) for no clear benefit, since Cowork artifacts can render the same UI with less infrastructure.
- (b) "Thin host serving HTML artifacts to Cowork" — middle path; the static-server piece is unnecessary if the artifact is shipped through Cowork's artifact pipeline directly. The MCP server still needs to exist for tooling either way, so (b) collapses to (c) plus a vestigial static server.
- (c) **chosen.** Smallest moving-parts profile. Leans into Pivot C cleanly. The MCP server is the only persistent local process; everything else is either a static directory (the project folder) or rendered on demand by Cowork.

**Tool surface (initial):**

| MCP tool | Purpose | Survives from |
|---|---|---|
| `read_file(path)` | Read a file under the project root | `tools/file_tools.py` |
| `write_file(path, content)` | Create or overwrite a file under the project root | `tools/file_tools.py` |
| `edit_file(path, find, replace)` | In-place edit (string replacement, fail if not unique) | `tools/file_tools.py` |
| `list_files(path, glob?)` | Directory listing with optional glob | `tools/file_tools.py` |
| `read_workspace_metadata()` | Returns project root path, git branch, schema version | `tools/file_tools.py` |
| `list_skills()` | Return `skills/[name]/SKILL.md` catalog | `tools/skill_registry.py` |
| `read_skill(name)` | Return SKILL.md content for one skill | `tools/skill_registry.py` |
| `propose_changes(changes, summary?)` | Persist a pending change-set (no disk writes; awaits approval) | `tools/skill_tools.py` |
| `approve_changes(change_set_id)` | Apply a previously proposed change-set through the sandbox | `api/changes.py` (re-exposed) |
| `reject_changes(change_set_id)` | Mark a change-set rejected | `api/changes.py` (re-exposed) |
| `ask_user(question, options?)` | Persist a pending question | `tools/skill_tools.py` |
| `answer_question(question_id, answer)` | Record an answer + synthesize a user message | `api/questions.py` (re-exposed) |
| `export_application(company_role)` | Bundle a per-application zip into `website/v2/exports/` (D4) | net-new |

The `run_skill` primitive from Phase 16 is replaced by the explicit pair `list_skills` / `read_skill` because the MCP idiom prefers small composable tools over a single overloaded one. Cowork picks a skill, reads its SKILL.md, and follows the instructions in subsequent turns — same Skills-as-Tools contract as ADR-001 D1, just with a sharper tool boundary.

**What survives from Phase 15-17.5:** sandbox helper, file API logic (re-shaped from FastAPI handlers into MCP tool functions), `propose_changes`/`ask_user` persistence and HITL endpoints (re-shaped the same way), SQLite schema v2, skill registry, the entire test suite (re-pointed at the MCP tool functions instead of TestClient routes — same fixtures, same assertions).

**What's deprecated:** the agent loop in `api/chat.py`, the chat tab in `host/frontend/src/components/app/ChatTab.tsx`, the per-user Anthropic API key flow in `api/auth.py` and `keystore.py`, the SPA bundle and StaticFiles mount in `main.py`, the conversations surface in `api/conversations.py`. Detailed file-by-file disposition in D3.

**What's net-new:**
- A Python MCP server entry point (`host/uja_mcp/server.py`) using `mcp` Python SDK (`pip install mcp` per the `mcp-builder` skill's guidance).
- An `export_application` tool that walks per-application outputs and emits a structured zip (D4).
- The v0.4.0 workflow tracker artifact (out of scope for this ADR; Track 7 covers it).

**Distribution model:** the same curated zip pattern from `scripts/sync_to_public.py`, but the launcher shrinks. Instead of "start a FastAPI server, open browser, paste API key" the recipe becomes "register the local MCP server with Cowork." Concretely, the zip includes:

- `start-uja-mcp.sh` / `start-uja-mcp.bat` — wrapper that ensures Python 3.11+, creates a virtualenv if missing, installs deps, prints the MCP stdio command for the user to paste into Cowork's MCP config.
- A `cowork-mcp-config-snippet.json` that the user can copy verbatim into the Cowork MCP settings (with the project-root path filled in by the launcher).

No `127.0.0.1` server. No browser. No port conflicts. No auto-open. The user's only first-time action is "register this MCP and pick the project folder."

**Pivot B fit (zip delivery hub):** the MCP server owns the export pipeline. When the workflow tracker (v0.4.0) finishes a per-application stage chain, Cowork calls `export_application(company_role)`; the server walks `decoded-jds/`, `resumes/`, `scores/`, `speaking-points/`, `cover-letters/`, `portfolio/`, `networking/` for that company-role, validates a manifest, writes the zip to `website/v2/exports/`. Auto-sync (per existing GitHub Actions pattern) pushes the deploy-source repo; Netlify rebuilds. See D4 for the zip's internal structure and the site's index.

**v0.4.0 fit (workflow UI):** the tracker is a Cowork artifact. It calls `list_files`, `read_file`, `read_skill`, `ask_user`, `propose_changes`, `approve_changes`, `export_application` through `window.cowork.callMcpTool`. The "where am I in the process" surface that chat couldn't give us comes from the artifact rendering its own structured stage view, not from the LLM narrating progress in prose.

**Implementation implications:**

- Net-new dependency: `mcp` (Python SDK). Pinned in `host/requirements.txt` once added.
- The MCP server is a `python -m uja_mcp.server` invocation that speaks JSON-RPC over stdio. No HTTP, no port, no CORS.
- The 36 existing tests are mostly preserved by re-targeting them at the MCP tool functions (the FastAPI route handlers were already thin wrappers over `tools/`/`db.py`/`sandbox.py`). Net change is small; adding MCP-specific protocol tests is the new work.
- v0.3.0 (Tauri) reconsidered — see "Phasing impact" below. Cowork is itself the desktop app; wrapping a non-existent web app in Tauri is moot.
- The OS-keychain wrapper from ADR-001 D8 is no longer load-bearing for an Anthropic key (Cowork holds the user's auth). It's kept for the moment in case future tools need a credential store (e.g. an LLM-API-key escape hatch for users who want to run the export pipeline headlessly), but it stops being a v0.2.0+ requirement. D3 marks it "kept, demoted."

---

### D2 — v0.2.0 ship shape: maintenance release

**Decision:** Tag `v0.2.0` against the current `main` (`e1ece32` post-Session 8 wrap, or whatever HEAD is when the tag is cut). The tag captures the Phase 15-17.5 work as a reachable artifact. Release notes will state plainly:

- v0.2.0 ships the FastAPI host + chat-style frontend + HITL endpoints + 36 passing tests.
- The chat-style UX is deprecated. v0.2.x picks up the Pure Cowork + thin MCP architecture from D1.
- New work targets v0.2.x and v0.4.0; v0.2.0 is the bookmark for "we shipped Phase 17.5."

**Why (a) over (b) and (c):**

- (b) "v0.2.0 = the new architecture from D1" — would require deleting the chat tab + agent-loop-in-host before tagging. That throws away most of Phase 17 + 17.5 just-shipped frontend work as un-tagged history. The frontend code's value as a reference (D3) survives; its value as a release artifact does not survive an unship.
- (c) "Skip v0.2.0; jump to v0.3.0" — avoids the orphaned-tag awkwardness of (a) but loses the recognition that Sessions 5-8 produced something worth tagging. Session-by-session continuity in `SESSION_LOG.md` is a load-bearing project artifact; tag-by-tag continuity should match it.
- (a) **chosen.** The git history already tells the truth (Sessions 5-8 happened; Phase 17.5 shipped). The tag matches the history. Subsequent v0.2.x tags then capture the rethink, and the through-line is honest.

**Tag mechanics:**

- Tag created on `main` post-merge of the ADR-002 branch (so the tagged commit includes ADR-002 + the SPEC §14 + ROADMAP updates).
- Annotated tag: `git tag -a v0.2.0 -m "v0.2.0 — Phase 15-17.5 (FastAPI host + HITL endpoints; chat-style UX deprecated, see ADR-002)"`.
- Push to canonical: `git push origin v0.2.0`.
- The deploy-source repo is unaffected (Pivot B reframes the site separately; the v0.2.0 tag does not trigger a site change).

**Trade-offs:**

- Pro: clean history, reachable artifact, honest release narrative.
- Pro: no "throw away just-shipped code before tagging" awkwardness.
- Con: a forker who reads "v0.2.0" first may try to use the chat UX without realizing it's deprecated. Mitigated by the release notes prominently linking to ADR-002, and by the deprecation note landing in `CLAUDE.md` "Current Status & What's Next".
- Con: the v0.2.0 → v0.2.1 jump is a larger architectural shift than typical patch versions. We accept this — the rethink is genuinely a v0.2.x scope (same major surface area, different runtime), not a v0.3.0 (per-OS native binaries).

**Implementation implications:**

- Tag cut at the end of Session 9 (after this ADR + the SPEC/ROADMAP updates merge).
- v0.2.1 starts the D1 work — initial scope is "stand up `uja_mcp/server.py` with the file tools + skill registry tools + HITL tools registered; wire one Cowork test session against it."

---

### D3 — Repository layout post-rethink

**Decision:** Categorize every host file by fate. Three buckets: **Survives** (carries forward into v0.2.x without significant change), **Deprecated** (kept as a reference but not maintained), **Net-new** (added in v0.2.x). The chat-tab frontend follows option "keep as deprecated reference" from the Q3 clarification.

#### Survives (carries forward into v0.2.x)

| Path | Role in v0.2.x |
|---|---|
| `host/uja_host/sandbox.py` | Path sandbox; the MCP server uses it unchanged. |
| `host/uja_host/db.py` | SQLite schema v2; the MCP server uses it unchanged. Conversation/message tables stay (they back `ask_user` answer history); pending_changes/pending_questions stay (they back the HITL primitives). |
| `host/uja_host/config.py` | Project-root config + `~/.uja/config.json`. The MCP server reads it the same way. |
| `host/uja_host/api/files.py` | Logic survives; re-shaped from FastAPI route handlers into MCP tool functions in `host/uja_mcp/tools/files.py`. |
| `host/uja_host/api/changes.py` | Logic survives; re-shaped into MCP tools `approve_changes` / `reject_changes`. |
| `host/uja_host/api/questions.py` | Logic survives; re-shaped into the MCP tool `answer_question`. |
| `host/uja_host/api/config.py` | Project-root setter; preserved as an MCP tool for first-time setup. |
| `host/uja_host/tools/file_tools.py` | The actual `read_file`/`write_file`/`edit_file`/`list_files` implementations. Become the bodies of MCP tools 1:1. |
| `host/uja_host/tools/skill_tools.py` | `propose_changes` + `ask_user` persistence logic survives. `run_skill` is split into `list_skills` + `read_skill` per D1's MCP-idiomatic tool shape. |
| `host/uja_host/tools/skill_registry.py` | Discovery of `skills/[name]/SKILL.md`. The MCP server uses it unchanged. |
| `host/uja_host/tools/__init__.py` | The dispatcher pattern survives, retargeted at MCP tool registration. |
| `host/tests/test_phase15_acceptance.py` | Sandbox + config tests; survive as-is. |
| `host/tests/test_phase16_skill_registry.py` | Skill registry tests; survive as-is. |
| `host/tests/test_phase17_5.py` | HITL tests; survive once re-pointed at MCP tool functions instead of TestClient routes. |
| `host/tests/integration/` | Integration smoke skeletons; survive. |
| `host/tests/live_smoke.sh` | Survives; updated to register the MCP server with Cowork instead of curl-ing the FastAPI host. |

#### Survives but demoted

| Path | Notes |
|---|---|
| `host/uja_host/keystore.py` | OS keychain wrapper. No longer load-bearing for an Anthropic API key (Pivot C). Kept in case a future tool needs a credential store. Documented in its module docstring as "demoted; not a v0.2.x requirement." |
| `host/uja_host/api/auth.py` | API-key write endpoint. Kept in case a power-user wants headless export (e.g. CI-style application bundling), gated behind an explicit flag. Removed from the default MCP tool registration; surfaces a 410 Gone if hit through the legacy FastAPI surface in v0.2.x. |

#### Deprecated, kept as a reference

| Path | Disposition |
|---|---|
| `host/uja_host/main.py` | The FastAPI app + uvicorn entrypoint. Stays in repo; not invoked by the MCP runtime. A new `host/uja_host/main.py` docstring header marks it deprecated and points at `host/uja_mcp/server.py`. |
| `host/uja_host/api/chat.py` | The agent loop. Stays as a working reference for SSE streaming + Anthropic message-loop reducer logic if we ever want it back. Module docstring marks it deprecated. |
| `host/uja_host/api/conversations.py` | The conversation history surface. Same disposition. |
| `host/frontend/` (entire tree) | Per Q3 answer: keep as deprecated reference. The HITL UX patterns in `ChatTab.tsx` (`PendingChangeSet`, `PendingQuestion`, `streamTurn` / `resumeStream` helpers, the `toolResultByUseId` useMemo correlation) are the cleanest extant demonstration of the HITL contract; v0.4.0's workflow tracker will need the same patterns in a different visual frame. A new `host/frontend/README.md` marks the directory deprecated and explains its preserved purpose. |

#### Net-new in v0.2.x

| Path | Purpose |
|---|---|
| `host/uja_mcp/__init__.py` | Package marker. |
| `host/uja_mcp/server.py` | MCP server entry point. JSON-RPC over stdio. Registers the tool surface from D1. |
| `host/uja_mcp/tools/files.py` | MCP tool wrappers for `read_file`/`write_file`/`edit_file`/`list_files`/`read_workspace_metadata`. Thin facades over `host/uja_host/tools/file_tools.py`. |
| `host/uja_mcp/tools/skills.py` | MCP tool wrappers for `list_skills`/`read_skill`. |
| `host/uja_mcp/tools/hitl.py` | MCP tool wrappers for `propose_changes`/`approve_changes`/`reject_changes`/`ask_user`/`answer_question`. |
| `host/uja_mcp/tools/export.py` | The `export_application` tool implementation (D4). |
| `host/tests/test_mcp_server.py` | MCP-protocol-level tests (initialize handshake, tool list, tool call, error shapes). |
| `host/tests/test_export_application.py` | Tests for the D4 export pipeline (manifest validation, deterministic zip bytes, sandbox-bounded). |
| `start-uja-mcp.sh` / `start-uja-mcp.bat` | New launcher per D1 distribution model. Replaces `start-uja.sh` / `start-uja.bat`. |
| `references/cowork-mcp-config-snippet.json` | Template the launcher fills in. |

#### Files explicitly slated for deletion in a follow-up session (not this ADR)

None. Everything either survives, gets demoted, or stays as a reference. Deletions are reversible decisions to defer; we'll re-evaluate in 1-2 sessions of v0.2.x work whether the deprecated tree is earning its keep.

**Implementation implications:**

- The follow-up session that starts D1 implementation creates `host/uja_mcp/` as a sibling to `host/uja_host/`. Both packages coexist; the MCP server imports from `uja_host` for everything that survives.
- `host/requirements.txt` adds `mcp` (Python SDK). FastAPI/uvicorn/anthropic stay pinned (deprecated tree still imports them).
- `host/frontend/` does not get rebuilt as part of normal CI in v0.2.x. The Vite build remains runnable for anyone who wants to inspect the deprecated UI; it's not part of the release artifact.

---

### D4 — v2 site reframe: exportable application packages

**Decision:** The v2 Netlify site (currently a placeholder at `website/v2/index.html`) is rebuilt as a static delivery hub for **exportable** per-application zips plus config templates. No marketing copy. No "download the local web app" CTA. URL-only access (search-invisible, per the v1 `noindex` + `robots.txt` pattern).

#### What the site serves

Three sections, each on its own page (or anchor; the v1 single-page pattern works fine):

1. **Application packages.** One card per per-company-role exportable zip. Each card shows: company, role, application date, status badge (Open / Submitted / Interviewing / Closed), zip filename, size, download link. Cards sort newest-first by default. No previews, no marketing copy.

2. **Config templates.** The bracketed-placeholder versions a forker downloads to bootstrap their own UJA project: `memory.md.template`, `tracker.md.template`, base resume DOCX template, README pointing at the canonical project folder structure. One card per template; same shape as the application-package cards.

3. **About.** A short page explaining what the site is and what it isn't. URL-only access expectation. Link to the v1 site for v0.1.x users. Link to the canonical (private) repo's README for forkers who already have access.

#### Zip structure (the contract that lets the site stay dumb)

A per-application zip is a deterministic artifact. Internal layout:

```
<company>-<role-slug>-<YYYY-MM>.zip
└── <company>-<role-slug>-<YYYY-MM>/
    ├── manifest.json          ← machine-readable index (versioned schema)
    ├── README.md              ← human-readable index
    ├── decoded-jd/
    │   └── <company>-<role-slug>-<YYYY-MM>.md
    ├── resume/
    │   ├── <company>-<role-slug>-<YYYY-MM>.docx
    │   └── <company>-<role-slug>-<YYYY-MM>.pdf
    ├── scores/
    │   ├── <company>-<role-slug>-<YYYY-MM>-before.md
    │   └── <company>-<role-slug>-<YYYY-MM>-after.md   (if applicable)
    ├── speaking-points/
    │   ├── <company>-<role-slug>-<YYYY-MM>.md
    │   └── <company>-<role-slug>-<YYYY-MM>.pdf
    ├── cover-letter/          (if applicable)
    │   ├── <company>-<role-slug>-<YYYY-MM>.md
    │   └── <company>-<role-slug>-<YYYY-MM>.pdf
    ├── portfolio/             (if applicable)
    │   └── <project-slug>/    (one subfolder per project)
    └── networking/            (if applicable)
        └── outreach.md
```

`manifest.json` schema (v1):

```json
{
  "schema_version": 1,
  "company": "netflix",
  "role_slug": "data-analyst",
  "application_month": "2026-04",
  "generated_at": "2026-05-03T12:34:56Z",
  "files": [
    {"path": "decoded-jd/netflix-data-analyst-2026-04.md", "kind": "decoded_jd", "size": 12345},
    {"path": "resume/netflix-data-analyst-2026-04.docx", "kind": "resume_docx", "size": 28910},
    ...
  ],
  "status": "submitted"
}
```

Why both `manifest.json` and `README.md`: the manifest lets the site (and any other consumer) parse the zip's contents without unzipping the whole thing; the README lets a recruiter who downloads it skim the package without parsing JSON.

**Determinism contract:** the zip is built with sorted file ordering, fixed compression level, and zeroed timestamps (epoch 0 in the ZIP local file headers). Re-running `export_application` against the same on-disk state produces byte-identical output. This makes the zip reviewable in git diffs (against the deploy-source repo) and lets downstream consumers cache by hash.

#### Where the zip gets built

Per the Q4 answer: **Cowork emits the zip as a workflow step.** Concretely, when the v0.4.0 workflow tracker hits an "export" stage for an application, Cowork calls `export_application(company_role)` (the MCP tool from D1). The MCP server:

1. Resolves the company-role slug against the project folder.
2. Walks the per-output-type folders (`decoded-jds/`, `resumes/`, `scores/`, etc.) for files matching the slug.
3. Validates that the minimum-viable set is present (decoded JD + resume; scores/speaking-points/cover-letter/portfolio/networking are optional). Fails loud with a `is_error: true` MCP response if not.
4. Writes the zip to `website/v2/exports/<company>-<role-slug>-<YYYY-MM>.zip`.
5. Updates `website/v2/exports/index.json` (the site's data source).
6. Returns the manifest + zip path to Cowork.

The user (or the workflow) then commits + pushes; the existing `auto-sync-to-public.yml` Action mirrors to deploy-source; Netlify rebuilds. No new pipeline; we ride the v0.1.x sync infrastructure.

#### How the site indexes itself

Static `index.html` + a small JS that fetches `exports/index.json` and `templates/index.json` and renders the cards. Same pattern the v1 site uses for the HEAD-fetch zip-size display, just with more rows. JSON files are committed to the deploy-source repo; no Netlify Edge Functions needed; no build step beyond Netlify's default static publish.

`exports/index.json` schema (v1):

```json
{
  "schema_version": 1,
  "exports": [
    {
      "filename": "netflix-data-analyst-2026-04.zip",
      "company": "Netflix",
      "role": "Data Analyst",
      "application_month": "2026-04",
      "status": "submitted",
      "size_bytes": 154321,
      "generated_at": "2026-05-03T12:34:56Z",
      "manifest_path": "netflix-data-analyst-2026-04.zip#manifest.json"
    },
    ...
  ]
}
```

Maintained by the `export_application` MCP tool. Append-only on success.

#### Visual style

Canva MCP exploration before building, not after. The aesthetic should match v0.4.0's structured-workflow tracker — clean, structured, slightly playful (per Pivot A's Sims-style direction), inner-circle voice (no marketing claims). Specific spike work tracked under ROADMAP Track 8.

**Concrete style guardrails:**

- No hero section with a marketing claim. The page opens with the application-package list.
- No gradient buttons. No emoji. No "AI" branding anywhere.
- System font stack (continues the v2 placeholder's convention, which avoids the Inter-as-AI-tell from the web-artifacts-builder skill).
- Palette: sky → pink gradient as accent only (matches the v2 logo + the deprecated frontend's brand-gradient class).
- Search-invisible: keep the existing `<meta name="robots" content="noindex,nofollow">` and `robots.txt: Disallow /`.

#### Trade-offs considered

- "Live preview of each application's resume in-browser" — rejected. Adds PDF.js / mammoth bundles to the public site for an audience (Milan, prospective recruiters who get the URL) that has the actual files at their fingertips already. Unzip-and-open is the right interaction.
- "Per-application static page generated at build time" — rejected for now. JSON-driven cards work; per-application pages add complexity for marginal benefit. Reconsider if applications grow past ~30 entries.
- "Site is git-driven entirely; no JSON manifest" — rejected. Without the manifest, the site can't show file-count or status badges without reading the zip on the client; the JSON is cheap and decisive.

**Implementation implications:**

- `website/v2/index.html` is rewritten end-to-end. The placeholder (see current state in `website/v2/index.html`) is retired.
- `website/v2/exports/` directory created in the deploy-source repo. Initial state: empty array in `index.json`; first real export lands in v0.2.x.
- `scripts/sync_to_public_v2.py` updated to allowlist `website/v2/exports/` so the auto-sync mirrors zips to deploy-source.
- Netlify build settings unchanged (still static publish from `website/v2/`).
- Custom domain (the original Phase 13 v0.1.1 deferred item) becomes more relevant — a memorable URL is the access credential. Re-raise with Milan when v0.2.x lands.

---

## Phasing impact (cross-reference SPEC.md §14)

ADR-002 reshapes the v0.2.0+ phase plan as follows. The full updated plan lands in `SPEC.md` §14 as part of this ADR's commit chain.

- **Phase 17.5** — already shipped; Session 8. Counts toward v0.2.0.
- **Phase 18-21** — were "distribution / testing / docs / merge gate" for the chat-style architecture. **Retired.** Replaced by the v0.2.0 tag (D2) cut against current `main`.
- **Phase 22** — was "tag v0.2.0." **Becomes Phase 22** still — tag cut against current `main`, end of Session 9.
- **Phase 23** — net-new. **MCP server scaffold** (v0.2.1 target). Stand up `host/uja_mcp/server.py`, register the file + skill + HITL tools, wire one live Cowork session against it, port the test suite.
- **Phase 24** — net-new. **Export pipeline** (v0.2.2 target). Implement `export_application`, the zip determinism contract, `exports/index.json` maintenance.
- **Phase 25** — net-new. **v2 site rebuild** (v0.2.3 target). Per D4. Static cards + JSON-driven index. Canva MCP visual exploration first, then build.
- **Phase 26** — net-new. **v0.4.0 workflow tracker artifact** (v0.4.0 target). Out of scope for this ADR; covered in ROADMAP Track 7.

#### v0.3.0 reconsidered

ADR-001 §14 committed v0.3.0 to a Tauri double-click app that wraps the local-host architecture. With D1 (Pure Cowork + thin MCP) chosen, **the v0.3.0 plan no longer makes sense as written.** Cowork is itself the desktop app; the local MCP server is invoked through Cowork's MCP runtime, not through a Tauri webview pointing at a FastAPI process. There is no "web app" left to wrap.

**Decision on v0.3.0 scope:** parked. Re-evaluate after Phase 23-25 lands. Plausible reframings:

- v0.3.0 = a polished installer for the MCP server (one-click `pip install` + Cowork MCP-config registration), with code signing for the launcher binary.
- v0.3.0 = a headless export-only mode for users who want to bundle applications without going through Cowork (CI-style, would require resurrecting the API-key path from "demoted" → "supported behind a flag").
- v0.3.0 = skipped; jump to v0.4.0 (workflow tracker) directly.

ADR-003 will likely be the place this gets resolved, after we have v0.2.x running. **Do not start any Tauri work** in the meantime.

---

## Alternatives considered (top-level)

The four Decisions above each enumerate alternatives in detail. At the top level, the alternatives we considered for the rethink as a whole were:

- **Stay the course.** Ship v0.2.0 as originally planned (Phases 18-21). Rejected: Pivot C makes the per-user Anthropic key flow inappropriate for the audience; Pivot A makes the chat tab the wrong primary surface; Pivot B reframes the site away from "download the local web app" entirely. Three of four user-facing assumptions in ADR-001 changed; finishing the original plan would ship a product nobody wants.
- **Throw out everything; start over from a blank repo at v1.0.0.** Rejected. The Phase 15-17.5 infrastructure (sandbox, file API, persistence, HITL primitives, test fixtures) is genuinely reusable and was hard-won. Starting over would discard ~36 passing tests' worth of behavioral specification.
- **Pivot the local app to a different LLM provider (e.g. Ollama-only) to remove the API-key friction.** Rejected. Doesn't address Pivot A (chat metaphor still wrong). Doesn't address Pivot B (site reframe still needed). Solves a friction that Cowork already solves better.

---

## Consequences (top-level)

- **Positive.** Smaller surface area to maintain. The per-user-credential class of bugs goes away (no API keys to leak, expire, or rate-limit). The workflow UI gets to be designed for its job (structured workflow tracking) rather than retrofitted into a chat metaphor. The site stops pretending to sell something and starts being useful.

- **Positive.** The reusable infrastructure shipped in Phases 15-17.5 carries forward almost unchanged into the MCP server. The 36-test suite is the spec for that behavior.

- **Negative.** The Phase 17 + 17.5 frontend is mothballed. Roughly two sessions of work becomes a deprecated reference rather than a shipping surface. We accept this trade — the work served its purpose (proved out the HITL contract end-to-end and surfaced the Pivot A insight live).

- **Negative.** The new architecture depends on Cowork as a runtime. If Cowork's MCP support changes shape, or if Anthropic's product strategy moves the desktop client, the v0.2.x stack has to follow. Mitigation: the MCP protocol is open; in the worst case the MCP server can be invoked from any other MCP-aware client.

- **Negative.** v0.3.0 is now uncertain. We trade ADR-001's clarity ("v0.3.0 = Tauri") for "v0.3.0 = TBD after we see how v0.2.x feels." Acceptable; ADR-003 will resolve it from a position of more knowledge.

---

## Open questions deferred from this ADR

- **Workflow tracker state model.** Where does per-application stage state live? `tracker.md` extension, a new SQLite table, both? Deferred to ROADMAP Track 7's Canva MCP design spike.
- **Export status field source-of-truth.** The zip's `manifest.json.status` and the site's `index.json` both carry `status`. Where does the user actually edit it? Probably `tracker.md`, with the export step reading from there. Deferred to Phase 24.
- **Multi-project support.** A user with multiple project folders runs multiple MCP server instances today. Cowork's MCP UX may make this seamless or painful; we'll see in Phase 23. Defer the per-project-routing question until then.
- **Gallery of past applications on the site.** Beyond a flat list of zips, would a "see what a Netflix Data Analyst application looks like" preview-page help recruiters and forkers? Plausible v0.2.4+. Out of scope here.
- **Code signing for the launcher.** Per the v0.3.0 reframing options above. Out of scope until v0.3.0 is re-defined.

---

*End of ADR-002.*
