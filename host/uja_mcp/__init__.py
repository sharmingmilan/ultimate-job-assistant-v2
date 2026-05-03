"""Ultimate Job Assistant — local MCP server (v0.2.x).

Per ADR-002 D1 the v0.2.x runtime is a JSON-RPC-over-stdio MCP server
that Cowork (Claude desktop) registers as a local tool surface. The
agent loop lives in Cowork; this package is the thin tool layer that
wraps the surviving Phase 15-17.5 modules in `host/uja_host/`.

Entry point: `python -m uja_mcp.server` (see server.py).

Tool surface lives in `host/uja_mcp/tools/` and is registered with
FastMCP in server.py. Each tool function is a thin facade over a
function in `host/uja_host/`; logic stays there, the MCP boundary is
here.
"""

from uja_host import __version__ as _host_version

__version__ = _host_version
