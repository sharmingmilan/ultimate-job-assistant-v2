---
name: orchestrator
description: "Workflow orchestrator that chains all Job Assist skills together into a guided application workflow. Use this skill whenever the user wants to: start a new job application, apply to a role, begin the application process, kick off the full workflow, or says something like 'I want to apply to [company]' or 'here's a JD I'm interested in.' The orchestrator walks through every step in order, asking at each decision point. It manages folder creation, skill handoffs, file routing, and progress tracking. Also trigger when the user says 'where did I leave off' or 'what's next' for an in-progress application."
---

# Orchestrator

The workflow engine that chains all Job Assist skills into a guided application process. You say "I want to apply to Stripe" and it walks you through every step from JD decoding to outreach, asking at each decision point so you stay in control without having to remember what comes next.

## Why This Skill Exists

The individual skills are powerful but the workflow has dependencies, decision points, and file routing that's easy to lose track of. The orchestrator handles the choreography so you can focus on the content. It knows what's been done, what's next, and what files to read/write at each step.

## Core Principles

1. **Guided, not automatic.** The orchestrator drives the sequence but never runs a skill without your confirmation. Every decision point gets an explicit ask.

2. **Context-aware.** If you're picking up a partially completed application, the orchestrator reads existing files to figure out where you left off and proposes the next step.

3. **Graceful skipping.** Any optional skill can be skipped without breaking the chain. The orchestrator adjusts downstream steps accordingly (e.g., if you skip scoring before targeting, it won't auto-score after either).

4. **Single source of progress.** The central `tracker.md` is the progress log. The orchestrator proposes updates after each skill completes (never auto-updates).

## Workflow Sequence

The orchestrator walks through skills in this order. Required steps are always run. Optional steps get an explicit ask.

```
Step 1: Setup & Folder Creation          [Required]
Step 2: Decoded JD                        [Required]
Step 3: Resume Score (before)             [Optional — ask]
Step 4: Resume Targeter                   [Required]
Step 5: Resume Score (after)              [Auto if Step 3 was yes, otherwise ask]
Step 6: Why This Company (speaking pts)   [Required]
Step 7: Cover Letter                      [Optional — ask]
Step 8: Portfolio Project                 [Optional — ask]
Step 9: Networking & Warm Intros          [Optional — ask]
Step 9.5: Interview Prep PWA              [Optional — ask]
Step 10: Wrap-up & Doc Freshness          [Required]
```

### Step 1: Setup & Folder Creation

**Trigger:** User provides a job description (URL, pasted text, or file) and optionally names the company.

**Actions:**
1. Identify company name and role title from the JD
2. Set context variables for the naming convention: `[company]`, `[role-slug]`, `[YYYY-MM]`
   - These derive all output filenames: `[company]-[role-slug]-[YYYY-MM].[ext]`
3. Check if `research/[company].md` already exists
   - **New company:** Will create research file during resume-targeter Phase 2
   - **Repeat company:** Note that existing company research will be used as foundation
4. Confirm the base resume to use (check `base-resumes/` for options)
5. Read `memory.md` for user context

**Announce:**
> "Starting application for [Role] at [Company]. I'll walk you through each step. Here's the plan:
> 1. Decode the JD
> 2. Optionally score your base resume
> 3. Target your resume
> 4. Score the targeted version
> 5. Build speaking points (and optionally a cover letter)
> 6. Optionally build a portfolio piece
> 7. Optionally find contacts for outreach
> 8. Optionally generate an interview-prep study site (PWA)
>
> Let's start with decoding the JD."

### Step 2: Decoded JD

**Skill:** decoded-jd (Deep Mode)

**Actions:**
1. Run decoded-jd in Deep Mode (this is a serious application, not a quick check)
2. Save output to `decoded-jds/[company]-[role-slug]-[YYYY-MM].md`
3. Present summary in chat, get approval

**On completion, announce:**
> "JD is decoded. Next: want me to score your base resume against this JD before we start targeting? This gives us a baseline to measure improvement."

### Step 3: Resume Score (Before) — Optional

**Skill:** resume-scorer

**Decision point:**
> "Want me to score your base resume before targeting? (Yes = I'll auto-score after targeting too, so you see the improvement)"

- **Yes:** Run resume-scorer on the base resume. Save as `score-before.md`. Set flag: `auto_score_after = true`
- **No:** Skip. Set flag: `auto_score_after = false`

**On completion (if run), announce:**
> "Base resume scores [X%] against this JD. Biggest gaps: [summary]. Let's target your resume now — I'll score again after so you can see the delta."

### Step 4: Resume Targeter

**Skill:** resume-targeter

**Actions:**
1. Resume-targeter reads `decoded-jds/[company]-[role-slug]-[YYYY-MM].md` as foundation for Phase 2 research
2. For repeat companies: reads existing `research/[company].md` and does supplementary research per the repeat-company protocol in CLAUDE.md
3. Runs full workflow: research → Q&A → bullet generation → change review → final DOCX + PDF
4. Saves research to `research/[company].md`, resume to `resumes/[company]-[role-slug]-[YYYY-MM].docx + .pdf`

**On completion, announce:**
- If `auto_score_after = true`: "Resume is targeted. Let me score it now to see how much we improved."
- If `auto_score_after = false`: "Resume is targeted. Want me to score the final version?"

### Step 5: Resume Score (After) — Conditional

**Skill:** resume-scorer

**Behavior depends on Step 3:**
- If Step 3 was **Yes**: Auto-run scorer on the targeted resume. Save as `score-after.md`. Present before/after delta.
- If Step 3 was **No**: Ask: "Want me to score the targeted resume?" If yes, score and save as `score-after.md` (no delta since there's no before-score).

**On completion, announce:**
> "Score: [before] → [after] (+[delta]). [Summary of improvements and remaining gaps]. Next: let me build your speaking points for 'why this company.'"

### Step 6: Why This Company (Speaking Points)

**Skill:** why-this-company

**Actions:**
1. Run why-this-company using decoded-jd, research-brief, memory.md, and the targeted resume
2. Generate speaking points (always)
3. Save to `speaking-points/[company]-[role-slug]-[YYYY-MM].md + .pdf`

**On completion, ask:**
> "Speaking points are ready. Want me to draft a cover letter from these points?"

### Step 7: Cover Letter — Optional

**Skill:** why-this-company (cover letter phase)

**Decision point:**
> "Want a cover letter?"

- **Yes:** Generate cover letter in markdown, present in chat. Save as `cover-letters/[company]-[role-slug]-[YYYY-MM].md + .pdf`.
- **No:** Skip.

**On completion, announce:**
> "Next: want to build a portfolio piece for this application? This is optional — it's a bigger time investment but can close gaps the resume can't."

### Step 8: Portfolio Project — Optional

**Skill:** portfolio-coach

**Decision point:**
> "Want to build a portfolio piece? The scorer identified [gap] as something a project could demonstrate. Estimated time: [X hours]."

If no scorer ran, frame it generally:
> "Want to build a portfolio piece to strengthen this application?"

- **Yes:** Run portfolio-coach full workflow (scope → data → plan → execute → package → optional LinkedIn post)
- **No:** Skip.

**Note:** This is the longest step. The orchestrator should confirm the user has time before starting.

### Step 9: Networking & Warm Intros — Optional

**Skill:** networking-intros

**Decision point:**
> "Want me to find contacts at [Company] and draft an outreach message?"

- **Yes:** Run networking-intros. Save contacts to `networking/contacts.md` and outreach drafts to `networking/outreach/`.
- **No:** Skip.

### Step 9.5: Interview Prep PWA — Optional

**Skill:** interview-prep

**Decision point:**
> "Want me to build a study site for the [Company] [role] interview? It pulls from the decoded JD and the company research, plus searches the web for real reported questions. It outputs a single-file PWA you can drag onto Netlify and install on your phone. Takes about 5-10 minutes to generate. Most useful when you have a real interview scheduled within the next 1-2 weeks."

- **Yes:** Run interview-prep. The skill walks through six phases (A through F) with a checkpoint per phase. Final output:
  - `interview-prep/[company]-[role-slug]-[YYYY-MM]-format.md` -- inferred interview format and topic list
  - `interview-prep/[company]-[role-slug]-[YYYY-MM]-content.json` -- topic content + sourced real-question entries
  - `interview-prep/[company]-[role-slug]-[YYYY-MM]-pwa/` -- deployable folder (drag onto Netlify Drop)
- **No:** Skip.

**On completion, announce:**
> "Interview prep PWA built at `interview-prep/[convention]-pwa/`. Drag the folder onto https://app.netlify.com/drop to deploy. Then add to your iPhone home screen via Safari Share -> Add to Home Screen."

**Notes:**
- This step requires `decoded-jds/[convention].md` and `research/[company].md`. If either is missing, the skill stops and tells the user which earlier step to run first.
- The skill never fabricates interview questions. If web research returns fewer than three credible sourced questions, the Real Questions tab renders an honest empty state. See `skills/interview-prep/references/source-attribution-rules.md`.
- The output `[convention]-pwa/` folder is git-ignored by default (per `.gitignore`).

### Step 10: Wrap-up & Doc Freshness

**Actions:**
1. Propose an update to `tracker.md` with:
   - Status for each skill column (checkmark, score, or "skipped")
   - Key decisions in the Notes column
   - Never auto-update tracker; always ask the user first
2. Propose doc freshness updates per the protocol in CLAUDE.md:
   - SESSION_LOG.md
   - CLAUDE.md (if any structural changes were made)
   - Any other files that need updating
3. Present a summary of everything produced with file locations:

> "Application complete for [Role] at [Company]. Here's what we produced:
> - Decoded JD: `decoded-jds/[convention].md` ✓
> - Resume score: [X%] → [Y%] in `scores/` ✓
> - Targeted resume: `resumes/[convention].docx + .pdf` ✓
> - Speaking points: `speaking-points/[convention].md + .pdf` ✓
> - Cover letter: `cover-letters/[convention].md + .pdf` ✓ / skipped
> - Portfolio: `portfolio/[convention]/` ✓ / skipped
> - Networking: `networking/` ✓ / skipped
> - Interview prep PWA: `interview-prep/[convention]-pwa/` ✓ / skipped"

## Resuming In-Progress Applications

When the user says "where did I leave off" or returns to a partially completed application:

1. Read `tracker.md` to find the application row and check skill completion status
2. Scan output folders for existing files matching the company/role convention
3. Determine the last completed step
4. Announce:

> "You left off at [Step X] for [Role] at [Company]. [Summary of what's done]. Next step would be [Step X+1]. Want to continue?"

## Repeat Company Handling

When the user starts a new application at a company that already has a research file:

1. Detect existing `research/[company].md`
2. Announce: "You've applied to [Company] before ([previous role]). I'll use the existing company research as a foundation and add supplementary research for this new role."
3. Follow the repeat-company research protocol from CLAUDE.md
4. Add new row to `tracker.md` for the new role

## Error Handling

- If a skill fails (web search blocked, file not found, etc.), announce the issue and offer options: retry, skip this step, or stop and pick up later
- If the user wants to jump ahead or go back, allow it. The guided walkthrough is a default sequence, not a locked path.
- If the user says "just do the resume" or signals they want a subset of the workflow, respect that and skip to the relevant steps

## Progress Tracking

The central `tracker.md` serves as the progress log. After each skill completes, propose updating the application's row in the tracker table. Each skill has its own column (Decoded JD, Score Before, Resume, Score After, Speaking Pts, Cover Letter, Portfolio, Networking). Mark with checkmarks, scores, or "skipped" as appropriate.

**Never auto-update tracker status.** Always ask the user before marking steps complete.

## Relationship to Other Skills

The orchestrator is the only skill that calls other skills. Every other skill can run independently, but the orchestrator provides the guided sequence and manages handoffs.

**Calls:** decoded-jd → resume-scorer → resume-targeter → resume-scorer → why-this-company → portfolio-coach → networking-intros

**Manages:** naming convention context, file routing to output-type folders, progress tracking (tracker.md), doc freshness

## Important Reminders

- The orchestrator is a guide, not a gatekeeper. If the user wants to skip, reorder, or stop, respect that immediately.
- Always read `tracker.md` before starting any work on an existing application. Don't re-run skills that have already been completed unless the user asks.
- The guided walkthrough should feel conversational, not bureaucratic. Keep announcements concise. Don't over-explain the process.
- When announcing scores, lead with the insight ("your biggest gap is X") not the number. The number supports the insight, not the other way around.
- Doc freshness happens at the END, not during the workflow. Don't interrupt the flow to update markdown files.
