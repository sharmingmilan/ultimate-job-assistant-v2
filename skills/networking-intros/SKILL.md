---
name: networking-intros
description: "Networking skill that finds relevant contacts at a target company and drafts personalized outreach messages. FUTURE ENHANCEMENT — not yet built. Placeholder spec only."
---

# Networking & Warm Intros

**Status: Future Enhancement — Not Yet Built**

This skill will find relevant contacts at a target company and draft personalized first outreach messages. Narrow scope for v1: contact discovery + first message only.

## Planned v1 Scope

- Search for relevant contacts at the target company (by role, team, shared background)
- Present contact options for user to confirm
- Draft a personalized first outreach message per confirmed contact
- Save contacts to `networking/contacts.md` and messages to `networking/outreach/`

## Planned Future Enhancements

- Full networking coaching arc: timing outreach relative to application, follow-up cadence, handling responses
- Different approaches by connection level (2nd-degree LinkedIn, cold message, re-engaging old contact)
- Integration with the orchestrator workflow

## Why Deferred

The user's current priority is the core application workflow (decode → score → target → narrative). Networking is loosely coupled and can be added later without changing the existing skill chain.
