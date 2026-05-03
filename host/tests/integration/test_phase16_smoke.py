"""Phase 16 live smoke test — Netflix regression through the web app.

This test is INTENTIONALLY skipped by default. It boots the host and
makes a real /api/chat call against Anthropic's API to verify the full
agent loop:

  user → /api/chat → Claude → run_skill('orchestrator') → SKILL.md content
       → Claude's subsequent turns follow the orchestrator
       → outputs land via write_file inside the project sandbox

Acceptance: structurally diff outputs against the v0.1.0 Netflix snapshots.

To run:
    export UJA_RUN_LIVE_TESTS=1
    export UJA_PROJECT_ROOT=/path/to/Ultimate\\ Job\\ Assistant
    # Plus: API key in OS keychain via host's keystore.set_api_key
    cd host && python -m pytest tests/integration/test_phase16_smoke.py -v -s
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


pytestmark = pytest.mark.skipif(
    os.environ.get("UJA_RUN_LIVE_TESTS") != "1",
    reason="Set UJA_RUN_LIVE_TESTS=1 to run the live Phase 16 regression.",
)


def test_run_skill_orchestrator_through_chat_endpoint(tmp_path):
    """Boot host + POST /api/chat → orchestrator skill loads.

    Stub for the Phase 16 acceptance gate. Implementation needs:
      1. A test fixture that mirrors the v0.1.0 Netflix folder
         layout (decoded-jds/netflix-data-analyst-2026-04.md, base resume,
         research/netflix.md, etc).
      2. UJA_PROJECT_ROOT pointed at it.
      3. An Anthropic API key set via uja_host.keystore.set_api_key.
      4. A fastapi.testclient TestClient on the create_app() instance.
      5. POST /api/chat with a message like "Run the orchestrator on the
         Netflix Data Analyst role I added under decoded-jds/."
      6. SSE stream consumed; assert run_skill('orchestrator') was called;
         assert subsequent file writes match the v0.1.0 snapshot
         structurally (file presence, format compliance — not byte-for-
         byte, since the model's output drifts run-to-run).

    Milan runs this with the host booted + his API key. Output diffs go
    against skills/interview-prep/evals/netflix-regression.md as the
    structural baseline.
    """
    pytest.skip("Phase 16 acceptance gate — implement when running locally.")


def test_propose_changes_then_approve_landing_on_disk(tmp_path):
    """End-to-end: model proposes a change → user approves → file lands.

    Same shape as the orchestrator test but exercises propose_changes +
    /api/changes/<id>/approve (Phase 17 endpoint, not yet implemented).
    """
    pytest.skip("Needs Phase 17 /api/changes endpoint to verify approval.")


def test_ask_user_pauses_then_resumes(tmp_path):
    """End-to-end: model calls ask_user → loop pauses → user posts answer
    → next chat turn resumes with the answer in context."""
    pytest.skip("Needs Phase 17 /api/questions endpoint to post answer.")
