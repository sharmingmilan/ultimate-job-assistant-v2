#!/usr/bin/env bash
# Ultimate Job Assistant — local web host launcher (macOS / Linux)
#
# Creates a Python venv on first run, installs deps, then launches the
# FastAPI host bound to 127.0.0.1 on a random ephemeral port.
#
# Requires Python 3.11+.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
HOST_DIR="$SCRIPT_DIR/host"
VENV_DIR="$HOST_DIR/.venv"

cd "$HOST_DIR"

# Detect Python 3.11+
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

echo "[uja] using $PY ($("$PY" --version))"

# venv bootstrap
if [ ! -d "$VENV_DIR" ]; then
  echo "[uja] creating venv at $VENV_DIR ..."
  "$PY" -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Install / update deps
echo "[uja] installing dependencies (pip)..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Hand off to the host module
echo "[uja] launching host..."
exec python -m uja_host.main "$@"
