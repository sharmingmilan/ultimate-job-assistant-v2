"""MCP tool facades.

Each module in this package wraps a slice of `host/uja_host/`:

  files.py  — read_file / write_file / edit_file / list_files /
              read_workspace_metadata. Wraps host/uja_host/tools/file_tools.py.
  skills.py — list_skills / read_skill. Wraps host/uja_host/tools/skill_registry.py.
              (The Phase 16 `run_skill` primitive is split into the two MCP-
              idiomatic tools per ADR-002 D1.)
  hitl.py   — propose_changes / approve_changes / reject_changes / ask_user /
              answer_question. Wraps host/uja_host/tools/skill_tools.py +
              host/uja_host/api/changes.py + host/uja_host/api/questions.py.
  export.py — export_application. Walks per-output-type folders, writes a
              deterministic zip to website/v2/exports/, updates
              exports/index.json. ADR-002 D4. Net-new in Phase 24; no
              FastAPI predecessor.

Functions are pure Python (no MCP framework imports) so tests can call
them directly. server.py registers each one with FastMCP via add_tool().
"""
