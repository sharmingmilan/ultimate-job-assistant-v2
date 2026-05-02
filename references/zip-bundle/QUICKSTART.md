# Quickstart — Ultimate Job Assistant

You just unzipped a job-application toolkit that runs inside Claude. This page gets you from zero to your first targeted resume in about 15 minutes.

---

## What you need

- **Claude (any paid plan, including the $17/mo Pro tier)** with **Cowork mode** enabled in Claude Desktop. Cowork mode lets Claude read and write files in a folder you select.
- **A folder on your computer** holding the contents of this zip.
- **Your base resume** as a `.docx` file. If you don't have one, this kit ships a template — see Step 2.

That's it. No backend, no database, no API keys, no cloud accounts. Everything runs locally inside your Claude session.

---

## Setup in five steps

### 1. Move the unzipped folder somewhere stable

Pick a stable location (Documents, iCloud Drive, Dropbox — anywhere you won't accidentally delete it). Rename the folder to something like `Ultimate Job Assistant`.

### 2. Fill in `memory.md`

Open `memory.md` in any text editor. Replace every `[BRACKETED]` value with your real content: name, contact info, top stories, work-style preferences. **This file is the most important input** — Claude reads it every session to understand who you are.

Take ten minutes here. Bad input → bad output.

### 3. Drop in your resume

Save a `.docx` of your resume to:

```
base-resumes/[your-role-type].docx
```

Examples: `base-resumes/data-analyst.docx`, `base-resumes/product-manager.docx`. You can keep multiple — one per role type you target.

**Don't have a resume in the right structure?** A template is bundled at:

```
references/templates/base-resume-template.docx
```

Open it, replace every `[BRACKETED]` value with your real content, save under `base-resumes/`, and you're set.

### 4. Open the folder in Claude Cowork

Launch Claude Desktop. Go to Cowork mode. Select the project folder (the one holding `CLAUDE.md`, `memory.md`, etc.). Claude will read `CLAUDE.md`, `memory.md`, and `tracker.md` automatically.

### 5. Apply to a job

Paste a job description into Claude and say something like:

> "I want to apply to **[Company]** for the **[Role]** position. Here's the JD: [paste it]"

Claude routes through the orchestrator and walks you step-by-step through:

1. **Decoded JD** — explicit + implicit requirements
2. **Company research** — culture, values, interview format (sourced)
3. **Resume targeter** — research, Q&A, tailored bullets, DOCX + PDF
4. **Resume scorer** (optional) — match score before / after
5. **Why this company** — speaking points + optional cover letter
6. **Portfolio piece** (optional) — scoped, sourced, executed
7. **Networking outreach** (optional) — find contacts, draft message
8. **Interview prep PWA** (optional) — a deployable study site for the role
9. **Wrap-up** — tracker + doc-freshness updates

Every step is human-in-the-loop. Nothing is auto-submitted. Reject any output, tell Claude what was wrong, and re-run only that step.

---

## Where things land

| Output | Folder | Filename pattern |
|---|---|---|
| Decoded JD | `decoded-jds/` | `[company]-[role-slug]-[YYYY-MM].md` |
| Targeted resume | `resumes/` | `[company]-[role-slug]-[YYYY-MM].docx` + `.pdf` |
| Score reports | `scores/` | `[convention]-before.md`, `[convention]-after.md` |
| Speaking points | `speaking-points/` | `[convention].md` + `.pdf` |
| Cover letter | `cover-letters/` | `[convention].md` + `.pdf` |
| Interview prep | `interview-prep/[convention]-pwa/` | folder with `index.html` etc. |
| Portfolio piece | `portfolio/[convention]/` | folder per project |
| Outreach drafts | `networking/` | `outreach-[name]-[company].md` |

The naming convention — `[company]-[role-slug]-[YYYY-MM]` — is load-bearing. The skills derive filenames from it automatically.

---

## Going deeper

- **`ONBOARDING.md`** — the longer setup walkthrough with examples, troubleshooting, and customization tips
- **`CLAUDE.md`** — what Claude reads at session startup; explains the project to Claude
- **`skills/orchestrator/SKILL.md`** — the workflow's chain logic
- **`skills/[name]/SKILL.md`** — full spec for each individual skill

You can edit the orchestrator and individual skills. They're plain markdown that Claude reads as the source of truth. Add your own skills, change the workflow order, tweak formatting rules in `memory.md` — the toolkit is yours to bend.

---

## Privacy

- Everything runs locally. No data leaves your machine.
- The `.gitignore` excludes personal-data folders (`base-resumes/`, `research/`, `resumes/`, `scores/`, etc.) by default.
- If you back this up to GitHub, **make the repo private**. Audit `memory.md` and any committed eval fixtures before pushing anywhere public.

---

## Trouble?

- **Claude can't see my files.** The Cowork folder pick must be the project root (the folder holding `CLAUDE.md`), not a parent.
- **Output looks generic.** Spend more time on `memory.md`. Vague stories produce vague bullets.
- **A skill produced something wrong.** Reject it, tell Claude what was off, re-run that step. The orchestrator preserves your prior approvals.
- **Interview-prep skill says "no sourced questions found".** That's intentional — the toolkit refuses to fabricate interview questions. Either accept the empty Real Qs tab or feed Claude questions you found yourself.

That's the whole tour. Happy hunting.
