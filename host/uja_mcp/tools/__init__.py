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

Functions are pure Python (no MCP framework imports) so tests can call
them directly. server.py registers each one with FastMCP via add_tool().

Note: `export_application` is Phase 24 (target v0.2.2); not implemented
here. The placeholder lives in tools/export.py once Phase 24 lands.
"""
