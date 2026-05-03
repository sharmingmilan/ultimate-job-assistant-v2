# host/frontend — Deprecated reference

This directory is preserved as a working reference. It is not part of the
v0.2.x release artifact and is no longer maintained.

## What this is

The chat-style frontend shipped in Phase 17 and Phase 17.5 of the v0.2.0
maintenance release. React 19 + Vite + Tailwind + shadcn/ui. Three primary
tabs (Chat / Materials / Settings) plus a two-step Onboarding flow for the
first-time project-root + API-key setup.

## Why it is preserved

Per ADR-002 D3, this tree is kept as a working reference rather than
deleted. The HITL UX patterns demonstrated in `src/components/app/ChatTab.tsx`
— `PendingChangeSet` and `PendingQuestion` rendering, the `streamTurn` /
`resumeStream` SSE helpers, and the `toolResultByUseId` `useMemo`
correlation between assistant `tool_use` blocks and their results — are the
cleanest extant demonstration of the HITL contract that Phase 17.5 wired up
end-to-end. v0.4.0's structured workflow tracker will need to express the
same contract in a different visual frame, and having a working reference
implementation on disk is cheaper than reconstructing it from
`api/changes.py` + `api/questions.py` alone.

## Status

- Not maintained. No CI, no dependency updates, no security patches.
- Not part of release artifacts. The v0.2.x distribution model registers
  the MCP server (see `host/uja_mcp/`, added in v0.2.1) with Cowork; the
  Vite SPA is not bundled into any user-facing zip.
- Runnable locally for inspection: `npm install && npm run build` from this
  directory. The dev server (`npm run dev`) expects the deprecated FastAPI
  host (`host/uja_host/main.py`) on `127.0.0.1:8000` with a configured
  project root + Anthropic API key, neither of which is required in v0.2.x.

## See also

- `docs/ADR-002-architecture-rethink.md` §D1 — the v0.2.x architecture
  (Pure Cowork + thin MCP server) that supersedes the local-web-app shape
  this frontend was built for.
- `docs/ADR-002-architecture-rethink.md` §D3 — the file-fate categorization
  that places this tree in the "Deprecated, kept as a reference" bucket.
