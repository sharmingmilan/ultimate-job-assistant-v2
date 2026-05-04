# ADR-003 — Visual identity for the v2 site

**Status:** Accepted
**Date:** 2026-05-04 (Session 14)
**Decision-makers:** Milan (product owner), Claude (cowork mode session)
**Branch:** `adr-003/visual-identity`
**Supersedes:** none
**Extends:** ADR-002 §D4 (visual style guardrails)

---

## Context

ADR-002 §D4 set guardrails for the v2 site visual style: slate-950 dark, sky→pink gradient as accent only, no marketing hero, no gradient buttons, no emoji, no AI branding, system font stack, `noindex` + `robots.txt: Disallow /`. Those guardrails told the eventual implementation what it could not do. They did not pick the concrete shapes.

Phase 25 (v2 site rebuild, target v0.2.3) writes the actual HTML / CSS / JS. It needs a locked visual identity to inherit so the implementation does not synthesize design under time pressure during the build.

Phase 24.5 (Session 13) produced `docs/phase24_5-app-space-research.md` — a 7,678-word landscape across 15 reference apps with eight framed-as-questions for ADR-003 to answer. Session 14 (this session) walked the eight questions interactively and locked eight decisions.

The load-bearing user is the returning visitor — Milan, who opens the site for a daily check-in to scan his application portfolio. New visitors (recruiters following a direct zip download link) interact with the site at the file level, not the page level, so the homepage real estate goes to the daily check-in.

---

## Quality bar

Same standard as ADR-001 + ADR-002, applied to v2 site visuals. Concretely:

- **8th-grade reading level** for all visible site copy (Session 13 lock). Internal docs (this ADR, the landscape doc, briefs, SESSION_LOG entries) stay expert-level.
- **Empty / loading / error states** surfaced explicitly. Empty state on first deploy reads as deliberate, not broken (per the Phase 25 brief R3 framing).
- **Accessibility** — WCAG AA contrast in both dark and light variants; theme toggle has a visible label or `aria-label`; status pills carry text labels (color is a complement, not the only signal).
- **Performance** — first paint under 1s; no JS bundle beyond the small renderer + Tailwind via the existing CDN pattern from the v1 site.
- **Determinism** — same `exports/index.json` produces same DOM. No client-side randomness.

The same quality bar that ADR-001 and ADR-002 set. The new surface inherits it.

---

## Decisions

### D1 — Status layout: flat list with optional status filter chips

**Decision:** the v2 site renders application packages as a single flat card list, sorted newest-first by default. A row of status filter chips above the list lets the user scope by status (All, Open, Submitted, Interviewing, Closed, Rejected). The kanban-pipeline column metaphor is rejected.

**Rationale:**

- The site is a delivery hub, not a tracker. Cards exist to be downloaded and sent to recruiters. They do not need to be dragged between stages. The kanban affordance answers a question (where in the funnel is this app?) the user can answer at a glance from a status pill.
- The flat list scales cleanly as applications grow. Pipeline columns force a happy path (Saved → Applied → Interview → Offer) that breaks at unhappy paths (Rejected, Withdrawn, On Hold) — apps end up in vestigial columns or sidebar buckets.
- Hybrid (flat default + filter chips) gives the user the kanban benefit (scope by status) without the kanban cost (visual narrative break at unhappy paths).

**Landscape evidence:**

- Pipeline-as-status is the category default. Huntr (https://huntr.co), Simplify Jobs (https://simplify.jobs), Notion-NotiNova (https://www.notion.com/templates/application-traker-job-internship), Airtable (https://www.airtable.com/templates/simple-applicant-tracker/exp1ozXL39xexSu2s) all default to it. Teal (https://www.tealhq.com) explicitly added a separate Application Status pill on top of column position to escape pipeline-as-status. The fact that the strongest tracker reaches for an escape valve is signal that pipeline-as-status is not the right primitive for this audience.
- Flat status-tag clusters: Pinboard (https://pinboard.in), Stephango (https://stephango.com), Hello.cv (https://hello.cv). These apps treat status as a property of the row, not a position in space — closer to v2's "personal toolkit, files in folders" posture.

**Consequences:**

- Phase 25 implements a single column of cards plus a filter-chip row. No board view, no calendar view, no gallery view (see D4).
- Status filter chips are clickable; each shows a count badge. Multiple chips selectable means the chip set is multi-select with `All` as the reset.
- Default sort: newest-first by `application_month` desc, then by `company` asc — matches the export tool's `_sort_index_exports` invariant from Phase 24's `host/uja_mcp/tools/export.py`.

---

### D2 — Theme: slate-950 dark default + light variant via prefers-color-scheme + explicit toggle

**Decision:** the v2 site defaults to a slate-950 dark theme. It also supports a light theme. The default is determined by the browser's `prefers-color-scheme` media query: dark for `dark`, light for `light`, dark for `no-preference`. An explicit toggle button in the top-bar (sun / moon icon) lets the user override, with the choice persisted in `localStorage` under a single key.

This extends ADR-002 §D4 (which locked dark) by adding a light variant and the toggle. The dark variant remains the default and the canonical visual reference.

**Rationale:**

- Daily check-in surface (D4) means the user opens this site many times. Respecting the user's OS-level theme preference is operational hygiene, not branding.
- The sky→pink gradient renders legibly on both themes. Slate-950 in dark becomes off-white-ish in light; the accent gradient stays the only chrome color in either mode.
- The toggle is a one-time annoyance and a daily benefit; the cost (a few CSS variables plus ~30 lines of JS) is low.

**Landscape evidence:**

- 12 of 12 in-bucket SaaS apps surveyed are light-theme dominant. Only Levels.io (https://levels.io/projects/) is dark, and that is brutalist neon — calm-dark is unoccupied in the surveyed landscape. v2's dark stays distinctive.
- Are.na (https://www.are.na) and Stephango (https://stephango.com) both default light but are read in many contexts; their lack of toggle is a forced choice their users tolerate. v2's user opens the site daily — toggle pays for itself.
- No surveyed app respects `prefers-color-scheme` AND offers an explicit override AND defaults dark. v2 occupies a triple-intersection. Distinctive, but consistent with the calm-dense posture.

**Consequences:**

- Phase 25 owns the light-variant palette pass. The dark palette is canonical (slate-950 background, slate-300 body text, sky→pink accent); the light variant is the inverse (off-white background, slate-800 body text, same sky→pink accent).
- All Phase 25 visual decisions must be specified in CSS variables, not hardcoded values, so the theme switch is a CSS-variable change and nothing more.
- `localStorage` key: `uja-v2-theme` with values `dark`, `light`, or absent (fall back to `prefers-color-scheme`).
- Toggle accessibility: the button has an `aria-label` ("Switch theme") and a visible icon. Keyboard activation toggles.

---

### D3 — Status pill style: mid-saturation (translucent backgrounds + bright text)

**Decision:** status pills use translucent colored backgrounds (~30-40% opacity at the chosen accent color) with full-saturation text in the matching hue. No solid-color fills. No text-only labels. One pill style applied across all statuses; only the hue changes per status.

**Rationale:**

- Saturated solid pills (the Notion / Airtable / Teal pattern) clash with the slate-950 calm-dark aesthetic. Full-saturation backgrounds shout for attention; the daily check-in surface should let the user choose where to look.
- Text-only labels (Pinboard / Stephango cluster) are too sparse for a list-with-filter-chips view. The user needs to scan a list of cards and parse status quickly; the colored pill is the at-a-glance signal.
- Translucent backgrounds scale across themes — the same pill renders correctly on slate-950 (D2 default) and the light variant by adjusting only the opacity layer.

**Landscape evidence:**

- Saturated pills: Notion templates (both official and NotiNova at https://www.notion.com/templates/application-traker-job-internship), Airtable, Teal. All run light backgrounds; saturated pills add structure to a low-density chrome.
- Text-only / faint border: Pinboard (https://pinboard.in), Stephango (https://stephango.com). Both run extremely low density; the user is reading slowly, not scanning.
- Mid-saturation is uncommon as a category convention. The closest landscape neighbor is Linear-style flat-tag UI (referenced by Q1 in the landscape doc but not directly surveyed). v2 invents the pattern for its specific density target.

**Consequences:**

- Phase 25 ships a `<StatusPill status="...">` component (or vanilla equivalent) that maps status → `{bg-color, text-color}` token pairs. Token sets defined in CSS variables for theme-switching.
- Color mapping (proposed; Phase 25 may iterate): Open = sky-400, Submitted = blue-400, Interviewing = amber-400, Offer = emerald-400, Closed = slate-400, Rejected = rose-400. ADR-003 locks the style, not the exact hues.
- WCAG AA contrast: text-on-pill must meet 4.5:1 in both themes. Verify during Phase 25 implementation.

---

### D4 — View shape: single flat card list, designed for daily check-in scanning

**Decision:** the v2 site offers a single primary view of application packages — a flat card list per D1, with status filter chips per D1 and the default sort from D1. No view-switcher (no calendar, no gallery, no kanban). The single view is explicitly designed for daily check-in scanning: status pill (D3) is visible at a glance per card; recent activity is surfaced via newest-first sort plus a `last-updated` timestamp on each card; filter chips let the user scope to "what needs my attention this week" in one click.

**Rationale:**

- The site's job is small. Multi-view is engineering for a problem v2 does not have. Adding view modes (Airtable-style) costs ~500-800 lines of frontend code and surfaces an interaction (mode-switching) that the daily check-in user does not need.
- Daily check-in cascades from D4: every other decision flows from "the user opens this site many times and wants to scan, not browse." The single view is the cleanest expression of that aspiration.
- Reconsider the multi-view decision when applications grow past ~30 OR when an unmet daily-check-in need surfaces (e.g., "I want to see all my Interviewing apps on a calendar by interview date"). Until that signal arrives, single view wins on simplicity.

**Landscape evidence:**

- Every app surveyed except Airtable commits to one primary view. Huntr (kanban), Teal (tabular tracker), Pinboard (linear list), Stephango (chronological writing list), Are.na (channel grid). One-view discipline is the category convention.
- Airtable (https://www.airtable.com/templates/simple-applicant-tracker/exp1ozXL39xexSu2s) is the multi-view exception. The view-switcher is its load-bearing UX, but the template is recruiter-facing — the use case is fundamentally different from job-seeker daily check-in.
- Daily check-in pattern in the landscape: closest analog is Hello.cv (https://hello.cv) — single profile-completion-focused view, no mode-switching. The user opens it for one purpose.

**Consequences:**

- Phase 25 does not implement a view switcher. The frontend has one card-list rendering path; status filter chips plus a sort dropdown are the only knobs.
- The card content is fixed: company logo placeholder + role + application_month + status pill + size_bytes + last-updated. Phase 25 may add a single-line description or notes field if the export schema supports it; ADR-003 does not require it.
- Pagination: defer until applications exceed ~30. ADR-003 marks this as an open question for Phase 25 to handle (or punt) per its own scope discipline.

---

### D5 — Privacy copy: implicit on homepage; About page explains briefly

**Decision:** the homepage does not include a privacy claim, a "no signups, no tracking" banner, a GDPR-style consent surface, or any other explicit privacy messaging. Privacy is communicated by site behavior — there are no signups, no analytics, no consent banners. A separate About page (linked from the top-bar per D8) documents the privacy posture in one short paragraph.

**Rationale:**

- Daily check-in cascade (D4) means homepage real estate goes to the cards. A privacy hero would push the cards below the fold and break daily check-in.
- The site's behavior is the strongest privacy claim. Naming privacy on the homepage when there is nothing to track is belt-and-suspenders — it draws attention to a thing that is not a problem here.
- The About page is the right place for context. New visitors and recruiters land on direct download URLs (no homepage interaction). The few who navigate to "what is this site?" reach About from the top-bar and read the privacy paragraph there.

**Landscape evidence:**

- Hero-positioned privacy: Pinboard (https://pinboard.in) leads with "social bookmarking for introverts" — anti-SaaS positioning as primary claim. Are.na (https://www.are.na/about) leads with "calm internet" mission. Both work because their privacy claim IS the product positioning. v2's positioning is "personal toolkit," not "privacy tool" — privacy is consequence, not differentiator.
- Footer / About-page placement: 12 of 15 surveyed apps. Most SaaS treats privacy as a compliance footer, not a positioning claim.
- Implicit: closest analog is Stephango (https://stephango.com) — site behavior reads as private (no analytics visible, no signup flow surfaced) without any homepage claim. v2 inherits this approach.

**Consequences:**

- Phase 25 writes an About page. Not a "marketing page about privacy" — a one-section page explaining what the site is, who it's for, and that there is no signup, no tracking, files live on the user's computer.
- The About page link in the top-bar is non-decorative. It is the only place context lives. Verify it is reachable via keyboard navigation and clearly labeled.
- No homepage privacy banner. No consent banner. No GDPR-style cookie disclosure. The site has no cookies.

---

### D6 — Voice cluster: plain-without-clubby

**Decision:** v2 site copy uses the "plain-without-clubby" voice cluster surfaced by the Phase 24.5 landscape doc. Plain means direct, declarative, evidence-based, no aspirational language. Without-clubby means no developer-insider humor, no anti-SaaS-as-a-pose, no in-group jokes. The voice addresses the reader as a job-seeker under stress, not as a peer in tech-Twitter.

**Rationale:**

- The 8th-grade reading-level constraint (Session 13 lock) rules out wry-developer voice; insider humor reads as clubby to non-developer audiences.
- The plain-spoken indie voice (Levels.io / Stephango at their most personal) requires a maker-persona to anchor the voice against. v2 does not currently have a public persona — borrowing the indie voice without the persona reads as performative.
- Plain-without-clubby is the bridge: borrow the directness of indie voice, drop the persona-dependent in-group register, ship something a job-seeker under interview stress can read fast.

**Landscape evidence:**

- Plain-spoken indie: Levels.io (https://levels.io/projects/) "List of all my projects ever." Stephango (https://stephango.com) Topics index. Direct, occasionally self-deprecating. Persona-dependent.
- Wry-developer: Pinboard (https://pinboard.in) "Social bookmarking for introverts." Robb Knight (https://rknight.me) homepage tagline. Self-aware humor for technical peers. Incompatible with 8th-grade audience.
- Outcome-confident SaaS: Rezi (https://www.rezi.ai) "Get your resume past the ATS." Defensible-on-evidence but assumes a sales-funnel audience. v2 has no sales funnel.
- Aspirational SaaS: Teal (https://www.tealhq.com) "Land your dream job, faster." Emotional. Conflicts with v2's evidence-first posture and ADR-002 §D4 "no marketing claim" guardrail.
- Plain-without-clubby: closest landscape neighbor is Hello.cv (https://hello.cv) — conversational without insider tone, gentle without aspirational stretch. v2 inherits the register without the chat onboarding mechanic.

**Consequences:**

- Phase 25 site copy review checklist: each visible string passes (a) 8th-grade Flesch-Kincaid OR is a literal label like "Submitted" / "Closed" that has no simpler form, (b) no aspirational verbs (dream, transform, unleash), (c) no insider terms (utilize, leverage, ecosystem), (d) no scare words (game-changer, revolutionary, AI-powered).
- Empty-state copy is the main place voice shows. Phase 25 drafts and runs a copy review pass before merge.
- Sample copy proposals in Appendix B.

---

### D7 — AI branding: none

**Decision:** the v2 site does not foreground "AI" as a value proposition. No "AI-powered," "Built with Claude," "AI-assisted," or similar phrasing in homepage copy, About copy, button labels, or anywhere visible to the user. This decision confirms ADR-002 §D4's "no AI branding" guardrail; the landscape evidence revisited in Phase 24.5 does not change the calculus.

**Rationale:**

- The site's value to the user is what it does (organizes per-application zips for easy delivery to recruiters). The fact that an LLM helps generate the underlying materials is irrelevant to the audience that downloads zips.
- "AI" as a homepage banner triggers buzzword fatigue and lowers trust. The audience that benefits from the site (job-seekers comparing tools) reads "AI-powered" as marketing noise, not signal.
- Aligns with ADR-002 §D4's "no marketing claim" guardrail and the evidence-first posture across the working principles.

**Landscape evidence:**

- AI-foregrounding (6 of 12 in-bucket apps): Teal (https://www.tealhq.com), Rezi (https://www.rezi.ai), Enhancv (https://enhancv.com), Jobscan (https://www.jobscan.co), Simplify (https://simplify.jobs), Notion-NotiNova (https://www.notion.com/templates/application-traker-job-internship). All lead with AI in marketing copy or feature lists.
- AI-quiet apps: Pinboard, Stephango, Hello.cv, Are.na, the indie hubs cluster, Robb Knight. None mention AI even though some clearly use it internally. The pattern: AI is a tool, not a brand.
- No surveyed app gained signal value from foregrounding AI in the personal-toolkit positioning shape. The category that benefits from AI branding is "AI-as-product" (e.g., Rezi's ATS scoring is the product). v2's product is the toolkit, not the AI.

**Consequences:**

- No copy change in Phase 25 from the existing v2 placeholder. The AI restraint propagates to README, About page, and any other future user-facing surface.
- If Phase 25 (or later) wants to surface "powered by Claude" as an attribution, it goes in a footer or a colophon page, never on the homepage and never as a value-prop banner.

---

### D8 — Homepage hierarchy: cards immediately above the fold; thin top-bar only

**Decision:** the v2 site homepage shows application package cards immediately above the fold. Above the cards: a thin top-bar with the site name, an About link, and the theme toggle (D2). Below the top-bar: the status filter chips (D1). Below the chips: the cards. No hero section, no marketing banner, no intro paragraph, no separator decoration. The cards must be visible on first paint at a typical desktop viewport (1440x900) without scrolling.

**Rationale:**

- Daily check-in cascade (D4) is load-bearing. Every byte above the cards is real estate the user pays for on every visit. Anything that is not the cards or the controls that scope the cards (filter chips, theme toggle, About link) does not earn the space.
- The hero section pattern (8 of 15 surveyed apps) optimizes for first-time visitors. v2's primary user is the returning visitor; first-time visitors arrive at direct download URLs, not the homepage.
- ADR-002 §D4's "no marketing hero" guardrail makes the hero option non-viable from the outset; ADR-003 makes the positive choice (cards-immediately) explicit.

**Landscape evidence:**

- Cards-immediately analog: Levels.io (https://levels.io/projects/) — content first, no hero. Stephango (https://stephango.com) — single intro line plus Topics index, then content. The pattern is rare in the SaaS-tracker / AI-tools clusters and common in indie hubs / outliers.
- Hero section default (8 of 15): Teal, Huntr, Simplify, Rezi, Enhancv, Jobscan, both Notion templates, Airtable. Optimizes for first-time visitor conversion. Conflicts with daily-check-in aspiration.
- Brief intro paragraph (gentle middle): no surveyed app uses exactly this pattern; closest is Hello.cv (https://hello.cv) which opens with a chat-style onboarding (essentially an interactive intro). Phase 24.5 user-review themes flag intro-heavy homepages as friction for returning visitors.

**Consequences:**

- Phase 25 implements a top-bar (~48-64px tall) plus a chip row (~40px tall) plus the card grid. Total above-cards real estate: ~100-120px. Cards begin around `y = 120px`.
- The top-bar is sticky-or-not is a Phase 25 implementation question; ADR-003 does not require it.
- The site name in the top-bar may or may not link back to the homepage (it currently is the homepage); Phase 25 decides per usability.
- About page is reached via the top-bar link. No other entry points needed.

---

## Cross-decision interactions

Decisions interact in load-bearing ways. Phase 25 must implement them as a consistent set, not as eight independent points.

- **D4 + D8 reinforce daily check-in.** Single view (D4) and cards-immediately (D8) both follow from the daily-check-in aspiration. Implementing one without the other diminishes the other. Specifically: a single view that renders below a hero defeats D4; a multi-view switcher above cards-immediately defeats D8.
- **D5 + D8 → About page is load-bearing.** Implicit privacy on the homepage (D5) plus no intro paragraph (D8) means the About page is the only place context lives. The About link in the top-bar is non-decorative — it is reachable via keyboard, clearly labeled, and the page itself carries weight (privacy posture, what the site is, who it is for).
- **D2 → light-variant palette work for Phase 25.** The toggle commits Phase 25 to a complete light-variant palette pass. Every CSS color used must be defined as a CSS variable with a dark plus light value. No hardcoded hex values in Phase 25 implementation.
- **D6 → site copy review pattern for Phase 25.** Voice (D6) is enforced by a copy-review pass before merging Phase 25's PR. Run Flesch-Kincaid; flag aspirational verbs; check for insider terms.
- **D1 + D3 + D8 reinforce calm-density.** Flat list (D1) plus mid-saturation pills (D3) plus thin top-bar (D8) compose the calm-dense aesthetic ADR-002 §D4 implied. Saturated pills on a flat list above a thin top-bar would clash; full-saturation pills would feel out of place.

---

## Phasing impact (cross-reference SPEC.md §14)

ADR-003 is the input to Phase 25. SPEC §14's Phase 25 row already names "Canva MCP visual exploration first" — ADR-003 supersedes that (the synthesis happened in Phase 24.5 plus Session 14, no Canva exploration needed). Phase 25 inherits the eight decisions as locked.

New Phase 25 work surfaced by ADR-003:

- **Light-variant palette pass.** All visual decisions specified in CSS variables; light-variant values defined alongside dark. ~1 hour during Phase 25.
- **Theme toggle UI.** Sun / moon icon button plus `localStorage` read / write plus `prefers-color-scheme` media query plus transition CSS. ~30-50 lines JS, ~20 lines CSS.
- **Status pill component.** Status → `{bg-color, text-color}` mapping; one pill style across statuses. Defined as CSS classes or inline style, depending on Phase 25's framework choice.
- **Status filter chip component.** Multi-select chip set with count badges and an `All` reset; chip click filters the card list (DOM update only, no fetch).
- **About page.** New static `about.html` (or anchor on `index.html` per the Phase 25 brief, which currently allows either). Plain-without-clubby copy; one short paragraph on privacy posture.
- **Copy review pass.** Pre-merge step in Phase 25's PR review: run each visible string against the D6 voice checklist.

ADR-003 does NOT specify implementation framework. The Phase 25 brief currently locks Tailwind via the `@tailwindcss/browser@4` CDN script (matches v1 site pattern) — ADR-003 inherits that choice without changing it.

---

## Alternatives considered (top-level)

Each decision section above enumerates per-decision alternatives. At the top level, the alternatives we considered for the synthesis as a whole were:

- **Defer synthesis to Phase 25 implementation.** Rejected. Synthesizing eight independent visual decisions while implementing them produces inconsistent decisions (the implementation pressure tends to make the easy choice, not the right one) and creates rework when the consequences of one decision contradict an already-implemented other decision. ADR-003 locks the design before Phase 25 starts so Phase 25 inherits a consistent set.
- **Adopt SaaS-tracker conventions wholesale.** Rejected. SaaS-tracker conventions (kanban columns, marketing hero, gradient buttons, AI branding, light theme dominant) conflict with ADR-002 §D4 guardrails and v2's positioning shape. Adopting them would re-cover ground ADR-002 already locked.
- **Adopt indie-hub conventions wholesale.** Rejected. Indie-hub voice and visual conventions (brutalist neon for Levels.io, austere serif for Stephango) depend on a maker-persona v2 does not have. Borrowing the surface without the persona reads as performative.
- **Skip the synthesis; ship what looks good in Phase 25.** Rejected at planning time (Session 13 explicitly rejected this in favor of evidence-based synthesis). The Phase 24.5 landscape doc plus Session 14 synthesis is the substitute.

---

## Consequences (top-level)

- **Positive.** Phase 25 starts with a locked design. No design-during-implementation drift. The eight decisions form a consistent set; consequences propagate cleanly.
- **Positive.** Daily check-in surface aspiration is preserved at the architecture layer. Phase 25 cannot implement away the calm-dense returning-visitor optimization without re-litigating ADR-003.
- **Positive.** The About page concept solidifies. Privacy posture has a designated home that is not the homepage; voice has a designated showcase.
- **Negative.** Light-variant adds work to Phase 25. ~1-2 hours of palette work that the dark-only original plan did not budget. Acceptable trade for daily check-in respect.
- **Negative.** About page copy needs careful drafting in plain-without-clubby voice. The "natural place to say the thing" is removed from the homepage; the About page must carry it without becoming a marketing surface.
- **Negative.** Multi-view future-flexibility is reduced. Adding a calendar / gallery / kanban view post-launch requires breaking D4. Acceptable trade for current scope discipline; revisit in a follow-up ADR if the signal arrives.

---

## Open questions deferred from this ADR

- **Specific light-variant palette.** The dark variant is canonical (slate-950 background, slate-300 body text, sky→pink accent). Light variant inverts this; exact values (off-white background hex, text colors, accent gradient stops) are a Phase 25 design pass.
- **Specific About page copy.** Appendix B includes voice examples. The full About page copy is Phase 25 implementation; ADR-003 specifies the voice, not the words.
- **Pagination beyond ~30 application packages.** Defer until applications cross the threshold. Phase 25 does not implement pagination.
- **Cowork-artifact tracker UI (post-v0.2.3).** Per the Session 13 → 14 handoff doc, the workflow tracker UI is parked for post-v0.2.3 ADR territory. ADR-003 does not address the tracker.
- **Top-bar sticky behavior.** Phase 25 may or may not make the top-bar sticky when scrolling. ADR-003 does not require it.
- **Card click-through interaction.** Whether clicking a card opens a download immediately, opens a detail page, or expands inline. Phase 25 implementation question.

---

## Appendix A — Concrete proposals for Phase 25 to inherit-or-adjust

Phase 25 is not bound by these. They are starting points, not specifications.

### A.1 Top-bar shape

```
[ Site name ]                          [ About ]   [ theme toggle ]
```

- Site name: text only, sky→pink gradient accent on the name. May be a link back to homepage.
- About: text link.
- Toggle: icon-only button with `aria-label="Switch theme"`. Sun for "switch to light" affordance when in dark; moon for "switch to dark" affordance when in light.
- Total height: 48-64px.

### A.2 Status filter chip set

```
[ All ]  [ Open ]  [ Submitted ]  [ Interviewing ]  [ Offer ]  [ Closed ]  [ Rejected ]
```

- Each chip shows the count of matching application packages: e.g., `Submitted (4)`.
- Multi-select: clicking `Submitted` filters; clicking `Submitted` again unselects; clicking `All` resets.
- Active chip uses the mid-saturation pill style (D3) at full opacity; inactive chips use a faint slate background.

### A.3 Card content fields

Each card shows:

- Company logo placeholder (a colored circle with the company initial, until favicons land in a follow-up).
- Company name (Title Case via the prettify helper from the Phase 25 brief R1).
- Role (Title Case from kebab-case slug).
- Application month (e.g., `April 2026`, derived from `application_month: "2026-04"`).
- Status pill (mid-saturation, D3).
- Size (e.g., `156 KB`, derived from `size_bytes`).
- Download link (the zip).

No screenshots, no inline preview, no interactive expansion. The card exists to scan and click-through to download.

### A.4 About page intro draft (plain-without-clubby)

> This is a personal job-application toolkit. The site lists application packages — one per company role — that you can download as a zip and send to recruiters.
>
> No signup, no tracking, no analytics. Files live on your computer. The site is read-only; the actual work happens in your Ultimate Job Assistant project folder, where you generate the materials and run the export tool to produce the zips you see here.
>
> Built and maintained by one person.

Phase 25 may rewrite. The voice is the lock.

---

## Appendix B — Voice examples (plain-without-clubby in practice)

### B.1 Empty state

```
No application packages yet.

Run the export tool from your project folder to add one.
```

Why this works: declarative; no aspirational language; gives the user the next concrete action.

### B.2 Filter chip count

```
12 packages
```

Not: "12 apps in your search journey." Not: "12 opportunities."

### B.3 Theme toggle alt text

```
Switch theme
```

Not: "Try our beautiful new dark mode." Not: "Toggle theme experience."

### B.4 Loading state

```
Loading packages...
```

Not: "Hang tight, we're getting your packages ready!"

### B.5 Error state

```
Couldn't load packages. Reload the page to try again.

If the problem persists, the export tool may need to run in your project folder.
```

Declarative; specific next action; surfaces the underlying mechanism without jargon.

---

*End of ADR-003.*
