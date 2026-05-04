# Phase 25 About page draft

**Source ADR:** ADR-003 D5 (implicit privacy on homepage; About page documents the privacy posture in one short paragraph) + ADR-003 D6 (plain-without-clubby voice cluster) + ADR-003 Appendix A.4 (starting draft).

**Voice constraints:**
- 8th-grade Flesch-Kincaid reading level for every visible string (Session 13 lock).
- No aspirational verbs (dream, transform, unleash).
- No insider terms (utilize, leverage, ecosystem).
- No scare words (game-changer, revolutionary, AI-powered).
- No emoji.
- Direct, declarative, evidence-based.

**Length:** one short page or single anchor section on `index.html`. Block 2 picks the shape per usability. Either way, the content below is the visible copy.

---

## Draft (to be reviewed at Block 1 HITL gate)

> # About
>
> This is a personal job-application toolkit. The site lists application packages — one per company role — that you can download as a zip and send to recruiters.
>
> Each package contains the full set of materials for one application: the decoded job description, the targeted resume in Word and PDF, the match score reports, the speaking points for an interview, the cover letter if there is one, and any portfolio or networking files generated for the role.
>
> No signup, no tracking, no analytics. Files live on your computer. The site is read-only; the actual work happens in your Ultimate Job Assistant project folder, where you generate the materials and run the export tool to produce the zips you see here.
>
> Built and maintained by one person.

---

## Voice review notes

Run each visible string through the D6 voice checklist:

- [x] No aspirational verbs. Every verb is mechanical: `lists`, `download`, `send`, `contains`, `generate`, `run`, `produce`.
- [x] No insider terms. "Application package" is plain (not "candidate dossier" or "applicant artifact"). "Read-only" is technical but maps cleanly onto an 8th-grade understanding ("can't be edited from here").
- [x] No scare words. "AI" does not appear. "Powered by" does not appear.
- [x] No emoji.
- [x] Reading level: short sentences, common verbs, concrete nouns. Estimated Flesch-Kincaid grade level ≈ 8.

---

## Variations considered (and rejected)

- **Marketing-style hero phrasing** ("Your job applications, packaged.") — rejected per ADR-002 §D4 "no marketing claim" and ADR-003 D8 "no hero".
- **Privacy-first hero** ("Privacy by design. No tracking. No ads.") — rejected per ADR-003 D5: privacy is communicated by site behavior, not a banner. About page mentions it briefly; homepage does not.
- **Maker-narrative voice** ("Hi, I'm Milan. I built this for myself...") — rejected per ADR-003 D6: requires a public maker persona v2 does not have. Plain-without-clubby drops the persona register.
- **Verbose explainer** ("This site is the front-end for the Ultimate Job Assistant project, which is a Claude-based skill suite that...") — rejected per D6 (insider terms) and the 8th-grade reading-level lock.

---

## Resolved at HITL gate (Session 15)

**Decision:** add a `Source code` link in the page footer pointing at the canonical repo (https://github.com/sharmingmilan/ultimate-job-assistant-v2). Forkers find the repo; daily-check-in user ignores it.

**No link to v1 site.** The v0.1.x audience and v0.2.3 audience overlap minimally; the link would add chrome to the calm footer for marginal benefit.

The link goes in the footer, not in the About body text. The About paragraph stays unchanged from the draft above.
