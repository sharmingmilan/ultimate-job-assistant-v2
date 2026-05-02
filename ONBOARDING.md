# ONBOARDING.md — Ultimate Job Assistant

**Status:** Public-facing. This is the doc someone clones (or copies into a sanitized public companion repo) to set up their own personalized version of Ultimate Job Assistant.

**Last updated:** 2026-05-02

**Audience:** A new user who wants to use this toolkit for their own job search. You will replace every reference to the original author with your own profile, plug in your own base resume, and customize the workflow to your career situation.

**Time to set up:** ~30–45 minutes (excluding the time it takes you to write your own `memory.md`, which is the most valuable input).

---

## What you're getting

Ultimate Job Assistant is a personal job-application toolkit that runs inside Claude (Cowork mode). It chains specialized skills together — JD decoding, resume targeting, scoring, "why this company" speaking points, portfolio coaching, networking outreach, and (new) interview-prep PWA generation — and produces a complete application package per role you target.

Everything is human-in-the-loop. Nothing is auto-submitted. No data leaves your machine unless you push your own repo to GitHub.

---

## Prerequisites

- **Claude Desktop with Cowork mode** (or a compatible Claude environment with file tool access)
- **A folder you control** on your Mac/PC where the project lives
- **Your base resume** (DOCX preferred)
- **Optional:** a GitHub account if you want to back up the project as a private repo
- **Optional:** Netlify or Vercel free account if you want to host the interview-prep PWAs

---

## Setup walkthrough

### Step 1 — Get the project

```bash
# If you have access to the public companion repo:
git clone <public-repo-url> "Ultimate Job Assistant"
cd "Ultimate Job Assistant"

# Or unzip a release archive into a folder of your choice.
```

The folder structure should look like:

```
Ultimate Job Assistant/
├── CLAUDE.md, SPEC.md, ROADMAP.md, README.md, ONBOARDING.md  (you are here)
├── DESIGN_DOC.md, SESSION_LOG.md, memory.md, tracker.md
├── skills/
│   ├── orchestrator/, decoded-jd/, resume-targeter/, resume-scorer/,
│   ├── why-this-company/, portfolio-coach/, networking-intros/, interview-prep/
├── references/, base-resumes/, research/, decoded-jds/, resumes/,
├── scores/, speaking-points/, cover-letters/, interview-prep/, portfolio/, networking/
└── .gitignore, .github/workflows/ci.yml
```

### Step 2 — Personalize `memory.md`

This is the most important file. It is Claude's primary source for understanding your work style, key stories, and resume preferences. Open `memory.md` and replace every section that references the original author with your own:

- **Identity & background** — your name, current city, contact preferences (if any)
- **Career history at a glance** — companies, roles, dates, scope
- **Key stories** — 3–6 anchor stories you'd tell in behavioral interviews, in STAR format
- **Resume preferences** — formatting rules you stand by (e.g., no em-dashes, two-page max, contact line on a single line)
- **What you want next** — target role types, industries, company-size preferences
- **What's off-limits** — companies, industries, work types you've decided against

Take your time on this file. Ten thoughtful minutes here saves hours of bad output later.

### Step 3 — Drop in your base resume

```
base-resumes/[your-role-type].docx
```

Examples: `base-resumes/data-analyst.docx`, `base-resumes/product-manager.docx`. You can have multiple base resumes for different role types.

If you also want the resume-targeter eval to run against a sanitized version of your resume, also place a redacted copy at:

```
skills/resume-targeter/evals/files/data_analyst_base.docx
```

(Or rename to match your role type. The eval just needs *a* resume to test against.)

### Step 4 — Start a session in Claude (Cowork mode)

Open Claude Desktop, switch to Cowork mode, and select the `Ultimate Job Assistant` folder. Then say:

> "I want to apply to [Company] for the [Role] position. Here's the JD: [paste or link]"

Claude reads `CLAUDE.md` to orient itself, then routes through the orchestrator, which walks you through each step (JD decode → company research → resume targeting → scoring → speaking points → optional cover letter → optional portfolio → optional networking → optional interview-prep PWA → wrap-up).

### Step 5 — (Optional) Initialize your own private git repo

```bash
cd "Ultimate Job Assistant"
git init -b main
git config user.email "you@example.com"
git config user.name "Your Name"
git add -A
git commit -m "Initial: my Ultimate Job Assistant"
```

Then create a **private** repo on GitHub and push:

```bash
git remote add origin git@github.com:youruser/ultimate-job-assistant.git
git push -u origin main
```

> **Important:** Keep the repo **private**. Even with `.gitignore` excluding personal data folders, your `memory.md` and any committed evaluation fixtures may carry information about you that you don't want public. Never publish a personal copy of this repo without auditing every file. The original author's project follows a two-tier model: private repo holds the personal copy permanently; only this `ONBOARDING.md` and a sanitized companion repo are ever public.

### Step 6 — (Optional) Hook up Netlify for the interview-prep PWAs

When the `interview-prep` skill outputs a folder like `interview-prep/[company]-[role-slug]-[YYYY-MM]-pwa/`, you can deploy it for free in 30 seconds:

1. Sign up at [netlify.com](https://www.netlify.com) (free)
2. Open [Netlify Drop](https://app.netlify.com/drop)
3. Drag the folder onto the page
4. Get a `https://...netlify.app` URL
5. Add to your iPhone home screen via Safari → Share → Add to Home Screen

That's it. No backend, no database, no monthly cost.

---

## What's safe to share publicly

Yes:

- This `ONBOARDING.md`
- `SPEC.md`, `ROADMAP.md`, `README.md`, `DESIGN_DOC.md` (after a sanitization pass — strip company-specific anecdotes from `DESIGN_DOC.md` before publishing)
- All files under `skills/*/` **except** any evaluation fixture that contains your real resume
- `references/templates/`, `references/scripts/`, `references/patterns/` (generic methodology)
- The `interview-prep` PWA template (which is generic by design)

No:

- `memory.md` (personal voice and stories)
- `base-resumes/`
- `research/[company].md` (your notes on real companies you've researched)
- `resumes/`, `scores/`, `speaking-points/`, `cover-letters/`
- `interview-prep/[company]-[role]-...-pwa/` (per-application output may contain company specifics)
- `portfolio/`, `networking/`, `applications/`, `archive/`
- Any docx in `skills/*/evals/files/` if it carries your real PII

The provided `.gitignore` excludes the personal-data folders by default. Audit before pushing anywhere public.

---

## Customization tips

**Add your own skill.** Create `skills/your-skill/SKILL.md` with a YAML frontmatter (`name`, `description`) and the body following the same pattern as the existing skills. Wire it into `skills/orchestrator/SKILL.md` if it should run as part of the workflow, or invoke it standalone.

**Change the workflow order.** Edit `skills/orchestrator/SKILL.md` to re-order, add, or remove steps. The orchestrator is just a markdown spec — Claude reads it as the source of truth.

**Tweak the resume formatting rules.** The canonical formatting rules live in `memory.md` and `references/patterns/formatting-rules.md`. All skills defer to those files.

**Use a different LLM provider for the PWA generation.** Not currently supported — the toolkit assumes Claude as the runtime. You'd need to port skill prompts to your preferred model.

---

## Troubleshooting

**Claude can't find a file.** Check that the Cowork folder pick is the project root, not a parent directory. Paths in skill specs are relative to the project root.

**The PWA template won't render.** Ensure CDN access is allowed (jsDelivr is the default). The build script will tell you if a CDN script failed to load. The PWA also runs offline once the service worker is registered, so the second load doesn't need network.

**A skill produced a bad output.** Reject the output, tell Claude what was wrong, and re-run. The orchestrator preserves your prior approvals — only the rejected step re-runs.

**The interview-prep skill found "no sourced questions" for my company.** That's intentional — it refuses to fabricate questions. Either accept the empty Real Qs tab, or feed the skill a manually compiled list of questions you found in places it couldn't search.

---

## Where to read next

- **`SPEC.md`** — exactly what was built, why, and the acceptance criteria
- **`ROADMAP.md`** — what's planned beyond v0.1.0 (SaaS pivot, code execution, spaced repetition, cross-application analytics)
- **`CLAUDE.md`** — the file Claude reads at session start; tells Claude how to be productive in this project

---

## Credits

The pedagogy in `skills/interview-prep/` is derived from established cognitive-science research (worked examples → fading → retrieval, plus interleaving and spacing). Citations live in `skills/interview-prep/references/pedagogy.md` and render in the footer of every generated PWA.

The toolkit's core skills (resume targeter, scorer, why-this-company, portfolio coach, networking, orchestrator) were originally developed in a project called `Job Assist`. Ultimate Job Assistant is a fork that adds the interview-prep capability and version-controls the whole thing.
