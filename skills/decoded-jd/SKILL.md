---
name: decoded-jd
description: "Job description decoder that analyzes the explicit and implicit expectations of a job posting using company research. Use this skill whenever the user wants to: understand what a job description really means, decode a JD, analyze a job posting, figure out what a company is actually looking for, evaluate whether a role is a good fit, prepare for an interview by understanding the JD deeply, or break down a job listing. Also trigger when the user shares a job description or job URL and wants to understand it before applying. This skill is the first step in the application workflow — its output feeds into resume-targeter."
---

# Decoded JD

A research-informed skill that breaks a job description into explicit requirements and implicit expectations, so you know what the company is actually looking for — not just what they wrote down.

## Why This Skill Exists

Job descriptions are marketing documents. They list requirements, but the real expectations live between the lines. A JD that says "strong SQL skills" might mean "you'll be writing 200-line queries joining 15 tables in a legacy warehouse with no documentation." A JD that says "cross-functional collaboration" might mean "you're the only analyst on a product team and need to push back on engineers." This skill decodes what's actually being asked.

## Core Principles

1. **Explicit vs. implicit separation.** Every finding gets categorized as either explicitly stated in the JD or inferred from research. The user always knows which is which.

2. **Confidence tagging.** All implicit findings get a confidence level: [HIGH] (multiple corroborating sources), [MED] (directional evidence), or [LOW] (informed inference, flagged as such). Explicit findings don't need confidence tags — they're literally in the JD.

3. **No fabrication.** Implicit expectations must be grounded in real research (company culture pages, Glassdoor reviews, interview guides, team context). If you're guessing, say so.

4. **Human-in-the-loop.** Present findings for user review. The user may have insider knowledge that confirms, corrects, or adds to your analysis.

## Modes

The skill operates in two modes. Mode is inferred from context and confirmed with a quick check — no formal toggle menu.

### Quick Mode
Best for: Deciding whether to apply, quick scan before a recruiter call, getting a fast read on a role.

- Analyzes the JD text directly
- Does 1-2 targeted web searches to inform implicit expectations
- Produces a concise decoded output
- Asks 1-2 clarifying questions at most (e.g., "Do you have experience with X that the JD emphasizes?")
- No deep company research

### Deep Mode
Best for: Serious applications, interview prep, feeding into resume-targeter.

- Full JD analysis
- Multiple web searches across culture, team context, and role-specific signals
- Produces a comprehensive decoded output with confidence-tagged implicit expectations
- Asks follow-up questions to fill gaps (e.g., "The JD implies heavy experimentation experience — do you have A/B testing stories we should surface?")
- Output is designed to feed directly into resume-targeter Phase 2

## Workflow

### Phase 1: Gather the JD

Accept the job description in any format:
- URL to the posting (fetch it; if blocked, search for the job title + company to find it elsewhere)
- Pasted text
- Uploaded file (PDF, DOCX, screenshot)

Extract and structure:
- Job title, team/department, location, salary range
- Company name and any identifiable business unit
- Listed responsibilities
- Required qualifications vs. preferred qualifications
- Technical skills mentioned (languages, tools, frameworks, platforms)
- Soft skills or traits emphasized
- Any unusual or notable phrasing

### Phase 2: Light Company Research

Research to inform the implicit layer. This is lighter than resume-targeter's Phase 2 — focused on understanding context, not building a full culture profile.

Search for:
- What the team or business unit does (especially for large companies where teams vary widely)
- Company values or leadership principles that explain JD phrasing
- Recent strategic context (product launches, reorgs, growth areas) that makes this role important right now
- Interview format for this role type at this company (what they actually screen for)

In Quick Mode: 1-2 searches max, focused on the most impactful context.
In Deep Mode: Multiple searches, building a layered understanding.

### Phase 3: Decode

Produce the decoded analysis. Structure it as follows:

#### Must-Haves (Explicit)
Requirements that are clearly stated and non-negotiable. For each one, note:
- What the JD says
- What it likely means in practice (informed by research)
- How demanding this requirement actually is (e.g., "SQL" could mean basic queries or advanced optimization — research the team to calibrate)

#### Nice-to-Haves (Explicit)
Preferred qualifications or "bonus" items from the JD. Flag which of these are likely more important than they appear (some "preferred" items are effectively required).

#### Implicit Expectations [Confidence-tagged]
What the JD doesn't say but the role almost certainly requires, based on:
- The team's function and recent priorities
- Company culture signals
- Seniority level implications
- Industry norms for this role type

Each implicit expectation gets a confidence tag: [HIGH], [MED], or [LOW].

#### Red Flags & Watch Items
Anything in the JD that signals potential concerns:
- Vague language that could hide scope creep
- Unusually broad responsibilities for the title/level
- Mismatches between title and listed requirements
- Salary range that doesn't match the experience ask
- Signs of a backfill vs. new role (and what that implies)

#### Key Themes for Targeting
3-5 synthesized themes that should drive resume targeting and interview prep. These are the "if you hit these themes, you're speaking their language" signals.

### Phase 4: Light Q&A (Mode-Dependent)

**Quick Mode**: Ask 1-2 questions max, only if something critical is ambiguous. Examples:
- "The JD heavily emphasizes experimentation — is that something you have direct experience with?"
- "This role seems to require people management — are you looking for IC or manager track?"

**Deep Mode**: Ask focused questions to fill gaps between the JD requirements and what you know about the user's background (from memory.md and the base resume). Focus on:
- Requirements where the user's fit is unclear
- Implicit expectations that need user confirmation
- Stories or experiences that could address the key themes

After Q&A, update the decoded output with any new information.

### Phase 5: Deliver

Save the decoded JD as a markdown file:
- **Location**: `decoded-jds/[company]-[role-slug]-[YYYY-MM].md`
- **Also**: Present a concise summary in chat (key themes, biggest gaps, overall fit assessment)

The summary should answer three questions clearly:
1. **What do they actually want?** (Top 3 implicit expectations)
2. **Where are you strong?** (Requirements you clearly meet)
3. **Where are the gaps?** (Requirements that need work or positioning)

## Output Format

```markdown
# [Company] — Decoded JD: [Job Title]

## Job Details
- Title, team, location, salary, job ID
- Posted date (if known)
- Source URL

## Must-Haves (Explicit)
| Requirement | What They Wrote | What It Likely Means | Your Fit |
|---|---|---|---|
| ... | ... | ... | Strong / Partial / Gap |

## Nice-to-Haves (Explicit)
| Item | Actually Important? | Notes |
|---|---|---|
| ... | Yes / No / Maybe | ... |

## Implicit Expectations
- [HIGH] ...
- [MED] ...
- [LOW] ...

## Red Flags & Watch Items
- ...

## Key Themes for Targeting
1. ...
2. ...
3. ...

## Fit Assessment
**Overall**: [Strong / Moderate / Stretch]
**Strongest signals**: ...
**Biggest gaps**: ...

## Research Sources
1. [Source](URL)
2. ...
```

## Relationship to Other Skills

**Feeds into resume-targeter**: When resume-targeter runs after decoded-jd, it reads the decoded-jd.md file as a foundation for its Phase 2 research. Resume-targeter then does deeper culture, interview, and team context research on top — the decoded-jd output gives it a head start and prevents duplicate work on JD parsing.

**Standalone use**: Decoded-jd works independently for interview prep, deciding whether to apply, or getting a quick read on a role before investing time in a full application.

## Important Reminders

- The implicit layer is what makes this skill valuable. Anyone can read the explicit requirements. Your job is to surface what's between the lines.
- Confidence tags are mandatory on all implicit findings. Never present an inference as a fact.
- If company research is thin (small startups, stealth-mode companies), be transparent about it. Lower your confidence levels and ask the user to fill gaps.
- The "Your Fit" column in the must-haves table requires knowing the user's background. Read memory.md at the start of every run.
- Red flags aren't dealbreakers — they're things to ask about in an interview. Frame them constructively.
