# Phase 23 live smoke checklist — Cowork ⇄ uja_mcp server

**Purpose.** Verify that the v0.2.1 MCP server (Phase 23) registers
cleanly with Cowork, exposes the ADR-002 D1 tool surface, and round-
trips one tool from each category. This is the last block in the
session-11 brief and is intentionally driven by the user (Milan)
because it requires a real Cowork session — the Dispatch agent can't
register an MCP server in another process's runtime.

Run this AFTER the Phase 23 PR merges to `main` and the `v0.2.1` tag
is cut. Total time: ~10 minutes.

---

## Prereqs

- A clean checkout of `main` at the `v0.2.1` tag.
- Python 3.11+ on PATH.
- Cowork (Claude desktop) installed and signed in.
- A project folder you don't mind exercising (the smoke proposes one
  test file under `notes/`; nothing else is touched). Easiest: a tmp
  folder you can `rm -rf` after.

---

## Setup

1. **Run the launcher to create the venv + emit the registration
   snippet.** From the repo root:

   ```bash
   bash start-uja-mcp.sh /path/to/your/uja/project
   ```

   Expected output (last block):

   - `[uja-mcp] using python3.X (Python 3.X.Y)`
   - `[uja-mcp] installing dependencies (pip; quiet)...` (silent on
     subsequent runs)
   - A boxed Cowork MCP-config snippet with absolute paths to the venv
     python + the host dir + your project root.

2. **Register the MCP server with Cowork.**

   Open Cowork's MCP settings (Settings → Developer → Edit Config in
   Claude Desktop, or the equivalent in Cowork). Paste the
   `mcpServers.uja` block from the launcher output into the file.
   Save. Restart Cowork if the UI prompts.

3. **Verify Cowork sees the server.** In Cowork's MCP settings, the
   `uja` server should appear with a green "connected" indicator
   (exact UI may vary). If it shows red, click into the diagnostics —
   the most common causes are: wrong venv path, missing `mcp`
   package install (re-run the launcher), or a stale background
   server process from an earlier attempt (Activity Monitor → kill
   stray `python -m uja_mcp.server` PIDs).

---

## Smoke checks

Run each prompt below in a Cowork chat. Pass = the indicated tool is
called and returns a sane payload. Fail = error in the MCP transport
or the tool returns the wrong shape.

### 1. tools/list — does Cowork see all 12 tools?

> _Prompt:_ "List the MCP tools the `uja` server exposes."

✅ Expected: Cowork lists 12 tools — read_file, write_file,
edit_file, list_files, read_workspace_metadata, list_skills,
read_skill, propose_changes, approve_changes, reject_changes,
ask_user, answer_question.

❌ If fewer than 12: server didn't register cleanly. Check
`tail -f ~/Library/Logs/Claude/mcp-server-uja.log` (or platform
equivalent) for stderr from the server process.

### 2. read_workspace_metadata — does the server see the right project?

> _Prompt:_ "Use the uja MCP server to read the workspace metadata.
> What's the project root and the current git branch?"

✅ Expected: Cowork calls `read_workspace_metadata`, returns
`{project_root: "/path/you/configured", git_branch: "main", ...}`.
The path matches what you passed to the launcher.

❌ If `project_root: null` or wrong: UJA_PROJECT_ROOT didn't reach
the server. Re-check the env block in the Cowork config snippet.

### 3. read_file — file tool happy path

Pre-create a file in the project root:

```bash
echo "# Smoke test" > /path/to/your/uja/project/SMOKE.md
```

> _Prompt:_ "Read the file SMOKE.md in the project root using the uja
> MCP server."

✅ Expected: Cowork calls `read_file`, returns
`{content: "# Smoke test\n", path: "SMOKE.md", ...}`.

### 4. ask_user — HITL outbound

> _Prompt:_ "Use the uja MCP server's ask_user tool to ask me what my
> favorite color is. Pause and wait for me to answer."

✅ Expected: Cowork calls `ask_user`, returns
`{question_id: "<uuid>", status: "pending", ...}`. Cowork shows the
question (or surfaces it as a tool result; the exact UX depends on
Cowork's HITL rendering) and pauses.

### 5. answer_question — HITL inbound

In a follow-up turn (or via the Cowork HITL UI if exposed):

> _Prompt:_ "Use answer_question with the question_id from the
> previous turn and the answer 'periwinkle'."

✅ Expected: Cowork calls `answer_question`, returns
`{question_id: ..., status: "answered"}`.

You can verify the row landed in SQLite:

```bash
sqlite3 /path/to/your/uja/project/.uja/state.db \
  "SELECT id, question, answer, status FROM pending_questions ORDER BY created_at DESC LIMIT 1"
```

### 6. propose_changes + approve_changes — the full HITL contract

> _Prompt:_ "Use propose_changes to suggest creating a file at
> notes/hello-from-mcp.md with content '# Hello from MCP'."

✅ Expected: Cowork calls `propose_changes`, returns
`{change_set_id: ..., status: "pending", files: ["notes/hello-from-mcp.md"]}`.
Disk is unchanged.

> _Follow-up prompt:_ "Now use approve_changes with that
> change_set_id."

✅ Expected: Cowork calls `approve_changes`, returns
`{status: "applied", paths_written: [{path: "notes/hello-from-mcp.md",
action: "created"}], count: 1}`.

The file should now exist:

```bash
cat /path/to/your/uja/project/notes/hello-from-mcp.md
# # Hello from MCP
```

---

## Cleanup

Optional: remove the test artifacts.

```bash
cd /path/to/your/uja/project
rm -f SMOKE.md
rm -rf notes/
sqlite3 .uja/state.db "DELETE FROM pending_questions; DELETE FROM pending_changes;"
```

---

## Reporting

If any check above fails, capture:

- The Cowork stderr log for the `uja` server (path varies by OS).
- The exact error text from the failed tool call.
- The line in this checklist that failed.

Open an issue (or comment on the v0.2.1 tag PR) with that bundle. The
Phase 24 brief inherits any architectural surprises surfaced here.
