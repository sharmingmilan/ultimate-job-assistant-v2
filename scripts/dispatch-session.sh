#!/usr/bin/env bash
# scripts/dispatch-session.sh
#
# Emit a `claude://` deep link that opens Claude Desktop / Cowork with an
# orchestrator-style prompt prefilled. The prompt is compact: it points at
# the on-disk session brief (docs/session-N-brief.md), tells the agent to
# read its orientation files and execute the brief autonomously.
#
# Usage:
#   bash scripts/dispatch-session.sh <session-number>
#   bash scripts/dispatch-session.sh 10
#   bash scripts/dispatch-session.sh 11
#
# Behavior:
#   - Reads docs/session-<N>-brief.md (errors if missing).
#   - Builds the orchestrator-style prompt.
#   - URL-encodes it.
#   - Concatenates with the claude:// deep-link scheme.
#   - On macOS: pipes to `pbcopy` (so the URL is on your clipboard).
#   - Always prints the URL to stdout for portability + verification.
#   - Optionally opens the link directly when --open is passed.
#
# Why brief-on-disk + thin-prompt-from-script:
#   - The brief is version-controlled, reviewable in PRs, and survives
#     across surfaces (Dispatch / Code / desktop / web).
#   - The launcher prompt is small + generic + reusable for any session.
#   - The Dispatch session has full repo access via its worktree and reads
#     the brief from there. No context has to round-trip through the URL.
#
# See ADR-002 §D1 + CLAUDE.md "Dispatch session pattern" for context.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ----- arg parsing -----
SESSION_NUM=""
OPEN_LINK=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --open)
            OPEN_LINK=1
            shift
            ;;
        --help|-h)
            sed -n '2,30p' "$0"
            exit 0
            ;;
        *)
            if [[ -z "${SESSION_NUM}" ]]; then
                SESSION_NUM="$1"
            else
                echo "ERROR: unexpected argument: $1" >&2
                exit 2
            fi
            shift
            ;;
    esac
done

if [[ -z "${SESSION_NUM}" ]]; then
    echo "ERROR: session number required." >&2
    echo "Usage: bash scripts/dispatch-session.sh <session-number> [--open]" >&2
    exit 2
fi

# ----- locate the brief -----
BRIEF_RELPATH="docs/session-${SESSION_NUM}-brief.md"
BRIEF_PATH="${REPO_ROOT}/${BRIEF_RELPATH}"

if [[ ! -f "${BRIEF_PATH}" ]]; then
    echo "ERROR: brief not found: ${BRIEF_RELPATH}" >&2
    echo "Available briefs:" >&2
    ls -1 "${REPO_ROOT}/docs/" 2>/dev/null | grep -E '^session-[0-9]+-brief\.md$' | sed 's/^/  /' >&2
    exit 2
fi

# ----- detect repo metadata for the prompt -----
REPO_OWNER="sharmingmilan"
REPO_NAME="ultimate-job-assistant-v2"
REPO_FULL="${REPO_OWNER}/${REPO_NAME}"

# ----- build the orchestrator-style prompt -----
# The prompt is intentionally compact. The brief carries substance.
read -r -d '' PROMPT <<EOF || true
Open a Claude Code session against the ${REPO_FULL} repo on the latest main and execute Session ${SESSION_NUM} of the Ultimate Job Assistant project.

You are an autonomous Session ${SESSION_NUM} implementation agent. You are not waiting for the originating Cowork session to approve every micro-decision. You are the planner, executor, evaluator, and quality gate. The brief tells you exactly what done looks like; you decide how to get there atomically and deterministically.

Step 1 (orientation, in order, before any code):
  1. CLAUDE.md — project structure, working principles, credential handling pattern.
  2. SPEC.md §14 — committed phase plan.
  3. docs/ADR-002-architecture-rethink.md — the v0.2.x architecture.
  4. SESSION_LOG.md — most recent entries for predecessor context.
  5. docs/session-${SESSION_NUM}-brief.md — THIS SESSION's brief; the deliverable, blocks, success criteria, end-of-session deliverables.
  6. Any additional files the brief enumerates in its own orientation list.

Step 2: Execute the brief.
  - Atomic commits per logical change.
  - Feature branches; do not push or merge to main yourself — open PRs and let the originating Cowork session review.
  - Working principles from CLAUDE.md (HITL / Atomic / Deterministic / Evidence-based) are non-negotiable.
  - If the brief is genuinely ambiguous, surface and ask before improvising.
  - If the brief and an orientation file disagree, the orientation file wins; flag the conflict in your end-of-session report.

Step 3: End-of-session report (your final message back).
  Per the brief's "End-of-session deliverables" section, plus PR URLs and commit SHAs. Do not write SESSION_LOG entries or update CLAUDE.md status — those belong to the originating Cowork session's wrap.

Out of scope for this session:
  Per the brief's "Out of scope" section. Do not touch v1 canonical, v1 deploy-source, v2 deploy-source, or any phase outside Session ${SESSION_NUM}'s target.
EOF

# ----- URL-encode + emit -----
ENCODED_PROMPT=$(python3 -c '
import sys, urllib.parse
sys.stdout.write(urllib.parse.quote(sys.stdin.read()))
' <<< "${PROMPT}")

URL="claude://claude.ai/new?q=${ENCODED_PROMPT}"

# ----- output -----
echo "============================================================"
echo "Session ${SESSION_NUM} dispatch link ready."
echo "Brief: ${BRIEF_RELPATH} ($(wc -l < "${BRIEF_PATH}" | tr -d ' ') lines)"
echo "Prompt size: $(echo -n "${PROMPT}" | wc -c | tr -d ' ') chars (raw), $(echo -n "${URL}" | wc -c | tr -d ' ') chars (URL)"
echo "============================================================"
echo
echo "${URL}"
echo

# Pipe to clipboard on macOS for convenience.
if command -v pbcopy >/dev/null 2>&1; then
    printf '%s' "${URL}" | pbcopy
    echo "(URL copied to clipboard via pbcopy.)"
fi

# Optionally open the link directly.
if [[ "${OPEN_LINK}" -eq 1 ]]; then
    if command -v open >/dev/null 2>&1; then
        open "${URL}"
        echo "(Opened via macOS 'open'.)"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "${URL}"
        echo "(Opened via xdg-open.)"
    else
        echo "WARN: --open requested but no 'open' or 'xdg-open' found." >&2
    fi
fi
