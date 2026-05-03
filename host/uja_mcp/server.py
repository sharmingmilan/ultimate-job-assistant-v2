"""Ultimate Job Assistant — MCP server entrypoint (Phase 23, v0.2.1).

Per ADR-002 D1 the v0.2.x runtime is a JSON-RPC-over-stdio MCP server.
This module instantiates a FastMCP instance, registers the tool surface
defined in `host/uja_mcp/tools/`, and runs the stdio loop.

Launched by:

  - `python -m uja_mcp.server` (developer + test invocation)
  - `start-uja-mcp.sh` / `start-uja-mcp.bat` (user-facing launcher; sets
    up the venv and prints the Cowork registration snippet).
  - Cowork's MCP runtime (registers `python -m uja_mcp.server` as a
    stdio command — see `references/cowork-mcp-config-snippet.json`).

Project-root contract: read from the `UJA_PROJECT_ROOT` environment
variable if set (and persisted to `~/.uja/config.json` on startup so
subsequent launches don't need the env var); otherwise read from
`~/.uja/config.json` directly. If neither resolves, the server still
starts — tools that need a root will raise a ToolError that FastMCP
surfaces as a structured error so the agent can prompt for setup.

Logging goes to stderr (stdio is reserved for the JSON-RPC protocol).
Log level is configurable via `UJA_MCP_LOG_LEVEL` (default INFO).

Tool surface (ADR-002 D1):

  Files:    read_file, write_file, edit_file, list_files, read_workspace_metadata
  Skills:   list_skills, read_skill
  HITL:     propose_changes, approve_changes, reject_changes,
            ask_user, answer_question

`export_application` is Phase 24 (target v0.2.2); not registered here.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from uja_host import __version__, config as host_config
from uja_mcp.tools import files, hitl, skills

log = logging.getLogger("uja_mcp")


SERVER_NAME = "uja_mcp"


def _configure_logging() -> None:
    """Send logs to stderr — stdio is owned by the MCP protocol."""
    level_name = os.environ.get("UJA_MCP_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        stream=sys.stderr,
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def _resolve_project_root() -> Optional[str]:
    """Honor UJA_PROJECT_ROOT if set; persist it for subsequent launches.

    Returns the resolved path on success, None if no root is configured
    or the env var pointed somewhere invalid (logged at warning level).
    Never raises — a missing root is a soft state; tools surface the
    error individually when invoked.
    """
    env_root = os.environ.get("UJA_PROJECT_ROOT")
    if env_root:
        try:
            cfg = host_config.set_project_root(env_root)
            return cfg.project_root
        except ValueError as e:
            log.warning("UJA_PROJECT_ROOT is set but invalid: %s", e)
            # fall through to the persisted config
    cfg = host_config.load_config()
    return cfg.project_root


def build_server() -> FastMCP:
    """Create the FastMCP instance with the full tool surface registered.

    Factored out so tests can build their own server (e.g. for
    `tools/list` and `tools/call` protocol checks) without touching
    process state.
    """
    mcp = FastMCP(SERVER_NAME)

    # ----- Files -----
    mcp.add_tool(
        files.read_file,
        name="read_file",
        annotations=ToolAnnotations(
            title="Read File",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    mcp.add_tool(
        files.write_file,
        name="write_file",
        annotations=ToolAnnotations(
            title="Write File",
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    mcp.add_tool(
        files.edit_file,
        name="edit_file",
        annotations=ToolAnnotations(
            title="Edit File",
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    mcp.add_tool(
        files.list_files,
        name="list_files",
        annotations=ToolAnnotations(
            title="List Files",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    mcp.add_tool(
        files.read_workspace_metadata,
        name="read_workspace_metadata",
        annotations=ToolAnnotations(
            title="Read Workspace Metadata",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )

    # ----- Skills -----
    mcp.add_tool(
        skills.list_skills,
        name="list_skills",
        annotations=ToolAnnotations(
            title="List Skills",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    mcp.add_tool(
        skills.read_skill,
        name="read_skill",
        annotations=ToolAnnotations(
            title="Read Skill",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )

    # ----- HITL -----
    mcp.add_tool(
        hitl.propose_changes,
        name="propose_changes",
        annotations=ToolAnnotations(
            title="Propose Changes",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    mcp.add_tool(
        hitl.approve_changes,
        name="approve_changes",
        annotations=ToolAnnotations(
            title="Approve Change-Set",
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    mcp.add_tool(
        hitl.reject_changes,
        name="reject_changes",
        annotations=ToolAnnotations(
            title="Reject Change-Set",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    mcp.add_tool(
        hitl.ask_user,
        name="ask_user",
        annotations=ToolAnnotations(
            title="Ask User",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    mcp.add_tool(
        hitl.answer_question,
        name="answer_question",
        annotations=ToolAnnotations(
            title="Answer Pending Question",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )

    return mcp


def main() -> None:
    """Run the MCP server over stdio."""
    _configure_logging()
    log.info("uja_mcp v%s starting (transport=stdio)", __version__)

    root = _resolve_project_root()
    if root is None:
        log.warning(
            "no project root configured; tools that need a root will return "
            "a structured error until UJA_PROJECT_ROOT is set or "
            "~/.uja/config.json is written."
        )
    else:
        log.info("project root: %s", root)

    mcp = build_server()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
