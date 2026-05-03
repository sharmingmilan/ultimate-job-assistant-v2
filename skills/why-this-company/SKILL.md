---
name: why-this-company
description: "Narrative skill that connects the user's career arc to a company's mission, producing speaking points for interviews and optionally a cover letter. Use this skill whenever the user wants to: prepare for a 'why this company' interview question, draft a cover letter, articulate why they're a good fit for a specific company, prepare talking points for a recruiter call, connect their background to a company's mission, or craft a compelling narrative for an application. Also trigger when the user says 'why do I want to work here' or 'help me explain my interest in this role.' This skill runs after resume-targeter and produces narrative outputs — it does not edit the resume directly."
---

# Why This Company

A narrative skill that connects the dots between your career arc and the company's mission. Produces speaking points you can glance at before a call and optionally a cover letter — both grounded in real research, not generic enthusiasm.

## Why This Skill Exists

"Why do you want to work here?" is the most common interview question and the one most people answer badly. Generic answers ("I admire your mission") get filtered out. Strong answers connect specific moments in your career to specific things the company is doing right now. This skill does that work — finding the real threads between where you've been and where they're going.

## Core Principles

1. **Specific connections, not flattery.** Every speaking point must connect a concrete part of your background to a concrete part of what the company is doing. "I love [Company]" is weak. "My regression analysis on product bundling at [Past Employer] showed me how content and product interact, and now [Company]'s streaming team is building exactly the kind of experimentation infrastructure that makes that insight actionable" is strong.

2. **User's voice, not a script.** The outputs are cheat sheets, not scripts. The user glances at notes and talks candidly during the interview. The tone should be neutral and professional — give them the raw material and let them adapt it to their own voice.

3. **Grounded in research.** Every claim about the company must come from verified research (decoded-jd, research-brief, or new searches). No making up what a company values or is working on.

4. **Human-in-the-loop.** Present the narrative for review. The user knows their own story better than any analysis — they'll catch when a connection feels forced or when a stronger thread exists.

## Prerequisites

**Reads from:**
- `decoded-jds/[company]-[role-slug]-[YYYY-MM].md` — for the role's explicit and implicit requirements, key themes
- `research/[company].md` — for company culture, values, team context, strategic direction
- `memory.md` — for the user's key stories, career arc, and communication preferences
- The targeted resume in `resumes/` (if resume-targeter has already run) — to ensure narrative alignment

If decoded-jd or research file don't exist yet, the skill can do its own light research, but it works best when earlier skills have already built the foundation.

## Workflow

### Phase 1: Map the Narrative Threads

Before asking the user anything, do the analytical work:

1. **Review the career arc** — Read memory.md and the resume. Identify the trajectory: what has the user built over time? What's the through-line across their roles?

2. **Review the company** — Read the decoded JD and `research/[company].md`. Identify: What is this company doing right now that matters? What are their stated priorities? What cultural values do they screen for?

3. **Find the connections** — Map specific career moments to specific company priorities. Look for:
   - Direct experience overlaps (e.g., worked at the same company before, worked in the same industry)
   - Skill-to-need matches (e.g., built experimentation frameworks and they're investing in experimentation)
   - Value alignment moments (e.g., pushed back on bad data at a past employer and the target company values data integrity)
   - Growth narratives (e.g., started in one area, grew into another, and this role is the natural next step)
   - Timing stories (e.g., why now? what makes this the right moment for both sides?)

4. **Identify the strongest 5-7 threads** — Not every connection is worth mentioning. Rank by: specificity (concrete > abstract), relevance to the role (not just the company), and storytelling potential (can the user naturally talk about this?).

### Phase 2: Light Q&A

Ask 2-3 focused questions to fill gaps in the narrative. Examples:

- "Your career arc shows X trajectory — is that how you see it, or would you frame your growth differently?"
- "The research shows the company is investing heavily in Y — do you have a genuine interest in that area, or is it more of a nice-to-have for you?"
- "Is there a personal connection to this company or industry that isn't on your resume?"

The goal is to make the narrative authentic, not manufactured. If the user doesn't have a compelling "why," it's better to know that now.

### Phase 3: Generate Speaking Points

Produce 5-7 speaking points. Each one should be:

- **One sentence** — short enough to glance at before a call
- **A specific connection** — links your background to their priorities
- **Adaptable** — gives the user a hook they can expand on naturally

Format:

```markdown
# [Company] — Speaking Points: [Job Title]

## Your Story in 30 Seconds
[1-2 sentence elevator pitch connecting your arc to this role]

## Speaking Points

1. **[Thread label]**: [One-sentence connection]
   - *Your proof*: [Brief reference to the relevant experience]
   - *Their priority*: [Brief reference to the company context]

2. ...

## If They Ask "Why Are You Leaving Your Current Role?"
[1-2 sentence framing — honest, forward-looking, not negative about current employer]

## If They Ask "Why Now?"
[1-2 sentence timing narrative]
```

Present the speaking points in chat. Ask: "Do these feel authentic to you? Anything feel forced or anything I'm missing?"

### Phase 4: Optional Cover Letter

After speaking points are approved, ask:
> "Want me to draft a cover letter from these points?"

If **YES**:
- Draft a cover letter in markdown, presented in chat
- Keep it to 3-4 paragraphs max
- Tone: professional, not overly formal or enthusiastic
- Structure:
  1. Opening: Why this role caught your attention (specific, not generic)
  2. Body: 2-3 of the strongest narrative threads, expanded with concrete examples
  3. Closing: What you'd bring and why the timing is right
- **Signature block**: End every cover letter with the user's preferred sign-off from memory.md (default: "Sincerely,\n[First name]"). This is a personal preference that persists across applications.
- No flattery, no clichés ("I'm passionate about..."), no restating the entire resume
- Save as both `cover-letters/[company]-[role-slug]-[YYYY-MM].md` and `cover-letters/[company]-[role-slug]-[YYYY-MM].pdf`. The PDF should be clean and professional: 1-inch margins, contact header (name, email, LinkedIn, GitHub), date, greeting, body paragraphs, and signature. Use reportlab to generate.

If **NO**: Move on. No pressure.

### Phase 5: Narrative Insights Handoff

After generating the narrative outputs, review them against the resume and flag any narrative-level insights that the resume-scorer should incorporate. These are framing improvements that only become visible after connecting the career arc to the company.

Examples of narrative insights:
- "The resume summary doesn't mention streaming or entertainment, even though the entire why-this-company narrative centers on returning to the entertainment industry"
- "The return-to-company story is a major strength but isn't reflected anywhere in the resume"
- "The resume emphasizes operational reliability but the narrative is about innovation — these should align"

Save these insights as a section in the speaking points file:

```markdown
## Narrative Insights for Resume Scoring
[Flagged for resume-scorer to incorporate into its suggestions]

- ...
- ...
```

The skill does NOT suggest specific resume edits or loop back to resume-targeter. It flags the insights and hands them off. Resume-scorer picks them up and includes them in its unified suggestions.

## Output Files

All files use the naming convention `[company]-[role-slug]-[YYYY-MM].[ext]`:

- `speaking-points/[convention].md` — Always generated. Includes narrative insights section at the bottom.
- `speaking-points/[convention].pdf` — Always generated alongside the .md. A clean, printable PDF version of the speaking points (excluding the narrative insights section, which is internal). Use reportlab to generate. The PDF is what the user glances at before a call.
- `cover-letters/[convention].md` — Only if the user opts in.
- `cover-letters/[convention].pdf` — Only if the user opts in. Generated alongside the .md.

All files are also presented in chat with a concise summary.

## Relationship to Other Skills

**Depends on:** decoded-jd (in `decoded-jds/`) and research file (in `research/`) for company context and role requirements. Works best after resume-targeter has run so the narrative can align with the targeted resume.

**Feeds into:** resume-scorer via narrative insights. The scorer incorporates these framing-level suggestions into its unified recommendations.

**Standalone use:** Can run independently for interview prep or recruiter call preparation, even without a targeted resume. Just needs enough context about the company and role.

## Formatting Rules

All outputs from this skill (speaking points, cover letters, PDFs) must follow the same formatting rules as resume outputs:

1. **No dashes as punctuation.** No hyphens, en dashes, or em dashes used as sentence punctuation. Restructure the sentence, use commas, semicolons, or periods instead.
2. **No fabrication.** All claims about the company or the user's experience must come from verified research or memory.md.

## Important Reminders

- The speaking points are a cheat sheet, not a script. Keep them scannable, one sentence each, not paragraphs.
- If the user doesn't have a compelling "why this company," don't force one. It's better to surface that honestly than to manufacture enthusiasm. Sometimes the answer is "this is a strong role match and the compensation is right" — that's fine.
- The cover letter should never restate the resume. It tells the story the resume can't: why here, why now, what connects your past to their future.
- Avoid clichés: "passionate about," "excited to contribute," "unique opportunity." Use concrete language.
- The narrative insights section is for the scorer, not for the user to act on directly. Frame them as observations, not directives.
