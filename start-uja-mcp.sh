#!/usr/bin/env bash
# Ultimate Job Assistant — MCP server bootstrap (macOS / Linux).
#
# Per ADR-002 D1, the v0.2.x runtime is a JSON-RPC-over-stdio MCP
# server. This script does NOT launch the server itself — Cowork's
# MCP runtime handles process lifecycle. It just:
#
#   1. Verifies Python 3.11+ is on PATH.
#   2. Creates host/.venv-mcp/ on first run and installs deps.
#   3. Prints the exact stdio command + a Cowork MCP-config snippet
#      (with PROJECT_ROOT prefilled) for the user to paste into
#      Cowork's MCP server registration.
#
# Optional first arg: project-root path. If omitted, the snippet shows
# the current working directory as a placeholder. UJA_PROJECT_ROOT can
# also be set in the env and the server will pick it up at startup.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
HOST_DIR="$SCRIPT_DIR/host"
VENV_DIR="$HOST_DIR/.venv-mcp"

PROJECT_ROOT_ARG="${1:-}"
if [ -n "$PROJECT_ROOT_ARG" ]; then
  PROJECT_ROOT="$(cd -- "$PROJECT_ROOT_ARG" &> /dev/null && pwd)"
elif [ -n "${UJA_PROJECT_ROOT:-}" ]; then
  PROJECT_ROOT="$UJA_PROJECT_ROOT"
else
  PROJECT_ROOT="<set this to your Ultimate Job Assistant folder>"
fi

# --- Python 3.11+ detection ---------------------------------------------
PY=""
for cand in python3.13 python3.12 python3.11 python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then
    ver="$("$cand" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "")"
    if [ -n "$ver" ]; then
      major="${ver%%.*}"
      minor="${ver##*.}"
      if [ "$major" -gt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -ge 11 ]; }; then
        PY="$cand"
        break
      fi
    fi
  fi
done

if [ -z "$PY" ]; then
  echo "ERROR: Python 3.11 or newer is required but was not found on your PATH." >&2
  echo "       Install Python 3.11+ from https://www.python.org/downloads/ and re-run." >&2
  exit 1
fi

echo "[uja-mcp] using $PY ($("$PY" --version))"

# --- venv bootstrap -----------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
  echo "[uja-mcp] creating venv at $VENV_DIR ..."
  "$PY" -m venv "$VENV_DIR"
fi

VENV_PY="$VENV_DIR/bin/python"

echo "[uja-mcp] installing dependencies (pip; quiet)..."
"$VENV_PY" -m pip install --quiet --upgrade pip
"$VENV_PY" -m pip install --quiet -r "$HOST_DIR/requirements.txt"

# --- Print registration snippet -----------------------------------------
echo
echo "================================================================"
echo "  Ultimate Job Assistant — MCP server ready to register"
echo "================================================================"
echo
echo "Stdio command (Cowork registers this; do NOT run it directly):"
echo
echo "    cd $HOST_DIR && $VENV_PY -m uja_mcp.server"
echo
echo "Cowork MCP-config snippet (paste under \"mcpServers\"):"
echo
cat <<JSON
{
  "mcpServers": {
    "uja": {
      "command": "$VENV_PY",
      "args": ["-m", "uja_mcp.server"],
      "cwd": "$HOST_DIR",
      "env": {
        "UJA_PROJECT_ROOT": "$PROJECT_ROOT",
        "UJA_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
JSON
echo
echo "Notes:"
echo "  * UJA_PROJECT_ROOT is read once at server startup and persisted to"
echo "    ~/.uja/config.json so subsequent launches work without the env var."
echo "  * Server logs go to stderr; level is configurable via UJA_MCP_LOG_LEVEL"
echo "    (DEBUG / INFO / WARNING / ERROR)."
echo "  * Template: references/cowork-mcp-config-snippet.json"
echo "================================================================"
