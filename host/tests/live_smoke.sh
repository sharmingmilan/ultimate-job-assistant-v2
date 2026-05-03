#!/usr/bin/env bash
# Live Phase 15 smoke test against the real Anthropic API.
#
# Requires:
#   ANTHROPIC_API_KEY in env
#   curl + jq on PATH
#   Python 3.11+ (start-uja.sh handles venv)
#
# What it does:
#   1. Picks a tmp project root
#   2. Launches the host (background)
#   3. PUT /api/config/project-root, PUT /api/auth/key
#   4. POST /api/chat asking the agent to list files + write HELLO.txt
#   5. Asserts HELLO.txt landed and conversation persisted

set -euo pipefail

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "ERROR: set ANTHROPIC_API_KEY before running this script." >&2
  exit 2
fi

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
TMP_PROJECT=$(mktemp -d -t uja-live-XXXX)
echo "[live] project root: $TMP_PROJECT"
echo "Hello world" > "$TMP_PROJECT/README.md"

LOG="$TMP_PROJECT/host.log"
PORT=18765

cd "$ROOT/host"
python3 -m uja_host.main --bind 127.0.0.1 --port $PORT --no-browser > "$LOG" 2>&1 &
HOST_PID=$!
trap 'kill $HOST_PID 2>/dev/null || true' EXIT

# Wait for /api/health
for i in $(seq 1 20); do
  if curl -sf "http://127.0.0.1:$PORT/api/health" > /dev/null; then
    break
  fi
  sleep 0.25
done

echo "[live] PUT /api/config/project-root"
curl -sf -X PUT "http://127.0.0.1:$PORT/api/config/project-root" \
  -H "content-type: application/json" \
  -d "{\"project_root\":\"$TMP_PROJECT\"}" | jq .

echo "[live] PUT /api/auth/key (test_connection=true)"
curl -sf -X PUT "http://127.0.0.1:$PORT/api/auth/key" \
  -H "content-type: application/json" \
  -d "{\"api_key\":\"$ANTHROPIC_API_KEY\",\"test_connection\":true}" | jq .

echo "[live] POST /api/chat"
RESP=$(curl -sf -N -X POST "http://127.0.0.1:$PORT/api/chat" \
  -H "content-type: application/json" \
  -d '{"message":"List the files in the project root, then write a file called HELLO.txt with content: Hello UJA from live test."}')
echo "$RESP"

CONV=$(echo "$RESP" | grep -A1 'event: conversation' | grep '^data: ' | head -1 | sed 's/^data: //' | jq -r .conversation_id)
echo "[live] conversation_id: $CONV"

if [ ! -f "$TMP_PROJECT/HELLO.txt" ]; then
  echo "FAIL: HELLO.txt was not created" >&2
  exit 1
fi
echo "[live] HELLO.txt created. Content:"
cat "$TMP_PROJECT/HELLO.txt"
echo

echo "[live] kill + restart host, fetch conversation"
kill $HOST_PID
wait $HOST_PID 2>/dev/null || true
sleep 0.5

python3 -m uja_host.main --bind 127.0.0.1 --port $PORT --no-browser > "$LOG.2" 2>&1 &
HOST_PID=$!
for i in $(seq 1 20); do
  if curl -sf "http://127.0.0.1:$PORT/api/health" > /dev/null; then break; fi
  sleep 0.25
done

curl -sf "http://127.0.0.1:$PORT/api/conversations/$CONV/messages" | jq '.count, .messages[0].role'

echo "[live] PASS"
