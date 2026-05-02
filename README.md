# Ultimate Job Assistant

A modular, research-driven personal job-application toolkit. Chains specialized skills together as an agentic workflow, then ships a deployable interview-prep study site for the role you're targeting.

This is a fork of [Job Assist](../Job%20Assist/) with one major addition: the **`interview-prep`** skill, which generates a single-file installable Progressive Web App for any technical interview based on the same evidence-based pedagogy used in the [Netflix Interview Prep](../Netflix%20Interview%20Prep/) project.

---

## What it does

For a given job posting, the toolkit:

1. **Decodes the JD** — explicit + implicit requirements, with confidence tags
2. **Researches the company** — culture, values, recent news, interview format
3. **Targets your resume** — research-driven, human-in-the-loop bullet rewriting
4. **Scores the result** — before / after match against the JD, with evidence
5. **Builds your "why this company" pitch** — speaking points and optional cover letter
6. **Coaches a portfolio piece** (optional) — scopes, sources data, walks through execution
7. **Drafts networking outreach** (optional) — finds warm-intro paths, writes the message
8. **Generates an interview-prep PWA** (optional, **new in v0.1**) — a deployable study site with worked examples, faded scaffolds, free-recall problems, and a sourced "Real Qs" tab
9. **Wraps up** — updates tracker, proposes doc-freshness updates

Every step has human-in-the-loop approval. Nothing fabricated. Every claim cited.

---

## What's new vs. Job Assist

| Item | Job Assist | Ultimate Job Assistant |
|---|---|---|
| Orchestrator + 7 skills | ✅ | ✅ (unchanged) |
| Folder conventions | ✅ | ✅ (extended for PWA outputs) |
| Interview prep | ad-hoc PDFs | new skill — generates a study PWA per role |
| Version control | manual | git + GitHub Actions CI |
| Documentation | CLAUDE.md + DESIGN_DOC.md | + SPEC.md (canonical) + ROADMAP.md (future enhancements) |

---

## Quick start

```bash
# Inside Claude (Cowork mode, with this folder mounted):
"I want to apply to [company] [role]" → orchestrator picks up

# Or invoke the new skill directly:
"build me an interview prep PWA for the Netflix Data Analyst role"
```

The orchestrator walks you through every step. The new `interview-prep` skill outputs a folder you can drag onto [Netlify Drop](https://app.netlify.com/drop) to get a public URL in ~30 seconds. Cost: $0.

---

## Layout

```
Ultimate Job Assistant/
├── SPEC.md             ← single source of truth for the build (read first)
├── CLAUDE.md           ← session startup context
├── ROADMAP.md          ← future enhancements (incl. SaaS pivot)
├── DESIGN_DOC.md       ← detailed skill specs and design decisions
├── SESSION_LOG.md      ← append-only session history
├── memory.md           ← Milan's preferences and key stories
├── tracker.md          ← central application tracker
│
├── skills/
│   ├── orchestrator/         ← chains the workflow
│   ├── decoded-jd/
│   ├── resume-targeter/
│   ├── resume-scorer/
│   ├── why-this-company/
│   ├── portfolio-coach/
│   ├── networking-intros/
│   └── interview-prep/       ← NEW
│
├── interview-prep/           ← per-application PWA outputs land here
├── decoded-jds/, research/, resumes/, scores/, ...
└── .github/workflows/ci.yml  ← lint + smoke test
```

---

## Status

**Version:** v0.1.0 shipped (2026-05-02). v0.1.1 in active build.

**v0.1.0** delivered the eight skills, the interview-prep PWA template, the regression test, the public-facing website, and the git + CI/CD plumbing. Site is live, search-invisible, hosted on GitHub Pages.

**v0.1.1** (in progress) reshapes the distribution model:
- Both GitHub repos go private (the deploy-source repo currently named `ultimate-job-assistant-public` keeps its name but flips to private)
- Hosting moves to Netlify (free tier, reads private GitHub repos via OAuth)
- The website's primary action becomes downloading a zip of the latest sanitized state
- Auto-sync via GitHub Action on every push to the canonical private repo
- Custom domain wired in once Milan buys one

See [SPEC.md](SPEC.md) §13 for the current decision set and §14 for the v0.1.1 phase list. [ROADMAP.md](ROADMAP.md) covers the longer-term tracks beyond v0.1.1.

---

## License

Personal project. Both repos private going forward. The website hosts a downloadable zip of the latest sanitized state; that zip is the public artifact, not the GitHub repo itself.

---

> **Note**: This is a personal toolkit. The website hosts a downloadable zip of the sanitized state for anyone with the URL. Search engines are blocked via `robots.txt` and `noindex`. If you found this and want to fork or adapt it for your own job search, please reach out first so we can chat about your use case.
