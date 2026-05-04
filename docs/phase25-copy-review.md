# Phase 25 copy review — visible string drafts + voice checklist

**Source ADR:** ADR-003 D6 (plain-without-clubby voice cluster) + ADR-003 Appendix B (voice examples in practice) + Session 13 lock (8th-grade Flesch-Kincaid).

**Purpose:** every string the user sees in `website/v2/index.html` and `website/v2/app.js` runs through this checklist before merge. Block 1 drafts the strings; Block 2 implements them; pre-merge review re-runs the checklist on what actually shipped.

---

## D6 voice checklist (run per string)

For every visible string:

- [ ] (a) **Reading level** — 8th-grade Flesch-Kincaid OR a literal status / count label like `Submitted` / `12 packages` that has no simpler form.
- [ ] (b) **No aspirational verbs** — banned: dream, transform, unleash, empower, elevate, optimize (in marketing sense).
- [ ] (c) **No insider terms** — banned: utilize, leverage, ecosystem, synergy, enablement, value-add.
- [ ] (d) **No scare words** — banned: game-changer, revolutionary, AI-powered, disruptive, next-generation.
- [ ] (e) **No emoji** (per ADR-002 §D4).
- [ ] (f) **No aspirational claims about outcomes** — banned: "land your dream job", "ace your interview", "stand out from the crowd".

---

## Visible string drafts

Organized by site region. Block 2 lifts these verbatim into the HTML / JS.

### Top-bar

| Element | String | Notes |
|---|---|---|
| Site name | `Ultimate Job Assist` | Same as v1 site. |
| Version badge | `v0.2.3` | Phase 25 ships at this tag. |
| About link label | `About` | Per Appendix A.1. |
| Theme toggle aria-label | `Switch theme` | Per Appendix B.3. |

### Status filter chips (per ADR-003 Appendix A.2)

| Chip | Label | Count format |
|---|---|---|
| All | `All` | Implicit total of all packages. |
| Open | `Open` | `Open (3)` when count > 0. |
| Submitted | `Submitted` | `Submitted (12)`. |
| Interviewing | `Interviewing` | `Interviewing (4)`. |
| Offer | `Offer` | `Offer (1)`. |
| Closed | `Closed` | `Closed (8)`. |
| Rejected | `Rejected` | `Rejected (5)`. |

Chip count format: `<Status> (<count>)`. Plain text. No "items", no "applications", no decorative parens-fonts.

### Card content (per ADR-003 Appendix A.3)

| Element | String pattern | Example |
|---|---|---|
| Company logo placeholder | First letter of company, uppercase | `N` for Netflix |
| Company name | Title Case via prettify | `Netflix` |
| Role | kebab-to-Title-Case via prettify | `Data Analyst` |
| Application month | `MMMM YYYY` from `YYYY-MM` | `April 2026` |
| Status pill | Same label as filter chip | `Submitted` |
| Size | Human-readable bytes | `156 KB`, `1.2 MB` |
| Download link aria-label | `Download <Company> <Role> package` | `Download Netflix Data Analyst package` |

No "→" arrows, no "Click here", no "Get the zip".

### Section headers

| Section | Header | Notes |
|---|---|---|
| Application packages | `Application packages` | No subtitle. |
| Config templates | `Config templates` | No subtitle. |
| About | `About` | No subtitle. |

### Empty states (per ADR-003 R3 + Appendix B.1)

**Application packages section, empty:**

```
No application packages yet.

Run the export tool from your project folder to add one.
```

**Config templates section, empty:**

```
No config templates published yet.
```

**Status filter chip selected but no matches:**

```
No packages match this filter.
```

### Loading state (per Appendix B.4)

```
Loading packages...
```

Used only on the brief moment between page load and first fetch resolution. May not appear in practice since `localStorage` theme bootstrap + cached `index.json` typically resolve within first paint.

### Error state (per Appendix B.5)

```
Couldn't load packages. Reload the page to try again.

If the problem persists, the export tool may need to run in your project folder.
```

Used when `fetch('./exports/index.json')` returns non-200 or parses fail. Console warning logged in addition.

### Footer

| Element | String | Notes |
|---|---|---|
| Brand line | `Ultimate Job Assist · v0.2.3 · Inner-circle build` | Uses middot separator (·) per v1 pattern. |
| Privacy line | `No tracking. No analytics. No SaaS.` | Verbatim from v1 site. |

---

## Strings that did NOT pass review (rejected)

Recording these so future drafts don't re-introduce them.

| Original | Failure mode | Replacement |
|---|---|---|
| `Your job applications, packaged.` | Aspirational claim (b) + tries to re-introduce a hero (D8) | Removed; cards immediately above the fold. |
| `Built with AI for job seekers` | AI branding (d) + scare-word vibe | Removed; no AI mention anywhere. |
| `Get started — download your first package` | Aspirational verb + onboarding-style framing | Removed; site is read-only. |
| `Welcome back, Milan.` | Personalization pretends at multi-user | Removed; no signed-in concept. |
| `12 opportunities tracked` | Aspirational ("opportunities") + clubby ("tracked") | Replaced with `12 packages`. |
| `Your application journey, in one place.` | Aspirational + voice-cluster mismatch | Removed; the site is delivery, not a journey metaphor. |

---

## Pre-merge enforcement

Block 2's PR review (whether by Milan or a sub-agent) runs through this checklist for each visible string. Any new string introduced in Block 2 gets a row added to the table above with a checklist pass-mark.

If a new string fails (a)-(f), do not ship; surface the conflict on the PR and resolve before merge.
