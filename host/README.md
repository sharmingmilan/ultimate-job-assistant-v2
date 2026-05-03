# Ultimate Job Assistant — Host (v0.2.0)

Local FastAPI backend that serves the v0.2.0 web app.
Runs at `127.0.0.1` on a random ephemeral port. Bring your own Anthropic API key.

See `docs/ADR-001-v0.2.0-architecture.md` for the architectural decisions this implements.

## Quick start (developer)

```bash
cd host
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uja_host.main --project-root /path/to/your/Ultimate\ Job\ Assistant
```

End users should run `start-uja.sh` from the repo root instead.

## Layout

```
host/
├── requirements.txt
├── README.md
├── uja_host/
│   ├── __init__.py
│   ├── main.py            # FastAPI app + uvicorn entrypoint
│   ├── config.py          # ~/.uja/config.json + project_root
│   ├── db.py              # SQLite schema + repo functions
│   ├── sandbox.py         # path-validation helper
│   ├── keystore.py        # OS keychain wrapper (anthropic_api_key)
│   ├── tools/
│   │   ├── __init__.py    # ANTHROPIC_TOOL_DEFS + TOOL_REGISTRY
│   │   ├── file_tools.py  # read/write/edit/list/metadata
│   │   └── skill_stubs.py # run_skill, propose_changes, ask_user (Phase 16)
│   └── api/
│       ├── __init__.py
│       ├── config.py      # /api/config
│       ├── auth.py        # /api/auth/key
│       ├── chat.py        # /api/chat (SSE)
│       └── conversations.py # /api/conversations
└── tests/
```

## Phase 15 scope

- File tools fully wired (read_file, write_file, edit_file, list_files, read_workspace_metadata).
- Skill tools (run_skill, propose_changes, ask_user) return structured "not_implemented" — Phase 16.
- /api/chat round-trips through Claude with the tool catalog.
- SQLite persistence at `<project-root>/.uja/state.db`.
- API key in OS keychain (`com.ultimatejobassistant.uja` / `anthropic_api_key`).

Anything beyond this (skill registry, frontend, distribution polish) is in Phase 16+.
