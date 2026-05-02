---
name: resume-targeter
description: "Deep-research resume targeting skill that researches a company's culture, values, and interview process, then conducts an adaptive Q&A with the user to craft tailored resume bullet points and a final resume document. Use this skill whenever the user wants to: tailor or target a resume for a specific job or company, prepare application materials for a job posting, build resume bullet points matched to a company's values, customize their resume for a role, or optimize their resume for a specific position. Also trigger when the user shares a job description or job URL and wants help applying. This skill is about building strong, specific, evidence-based resumes — not generic resume templates."
---

# Resume Targeter

A research-driven, human-in-the-loop skill for building targeted resumes that align with a specific company's culture, values, and role requirements.

## Why This Skill Exists

Generic resumes get filtered out. The best resumes speak the company's language, mirror its values, and demonstrate relevant impact with specifics. This skill does the homework — researching the company and role deeply — then guides the user through a structured Q&A to extract their strongest, most relevant experiences before generating tailored bullet points and a final resume.

## Core Principles

1. **No fabrication.** Every claim about a company's culture, values, or interview process must come from web research with credible sources. If you can't verify something, don't include it. When in doubt, tell the user what you found and what you couldn't confirm.

2. **Human-in-the-loop at every stage.** Never auto-generate the final resume without the user reviewing and approving the bullet points and proposed changes first. The user knows their experience — your job is to draw out the right stories and frame them effectively.

3. **Specific over vague.** Bullet points must include concrete details: numbers, tools, outcomes, scope. "Improved data pipeline efficiency" is weak. "Redesigned ETL pipeline processing 2M+ daily records, reducing runtime from 4 hours to 45 minutes using partitioned SQL queries" is strong.

4. **Credible sources only.** Prefer official company pages (careers, culture memos, investor relations), reputable news outlets, and established interview prep sites. Flag when a source might be outdated or unverified.

## Workflow

The skill runs in five phases. Each phase has a clear deliverable and requires user input before moving on.

### Phase 1: Gather Inputs

Collect two things from the user:

- **Job description** — Accept any format: a URL to the posting, pasted text, or an uploaded file (PDF, DOCX, screenshot). If a URL, fetch it. If it can't be fetched, search for the job title + company to find the listing elsewhere.
- **Existing resume** — The user must upload their current resume. This is required because the final output preserves their original formatting and structure. Accepted formats: PDF, DOCX, or plain text.

Read both carefully. Extract and note:
- Job title, team/department, location
- Explicit responsibilities and duties
- Required vs. preferred qualifications
- Technical skills mentioned (languages, tools, frameworks)
- Soft skills or traits emphasized
- Salary range if listed

From the resume, note:
- Current structure and section order
- Formatting style (fonts aren't critical, but section layout, bullet style, and hierarchy matter)
- Existing experience, skills, and education
- Gaps relative to the job description

### Phase 2: Deep Company & Role Research

Research the company across three dimensions. Use WebSearch and WebFetch. Conduct multiple searches to build a complete picture — don't rely on a single query.

#### 2a. Culture & Values
Search for:
- The company's official culture page or culture memo
- Core values and what they mean in practice
- Leadership principles or operating philosophies
- Recent culture updates or changes
- Employee reviews on culture (Glassdoor, Blind, etc. — treat as directional, not authoritative)

#### 2b. Interview Process
Search for:
- Interview stages and format for this role type (or similar roles)
- What interviewers look for (technical skills, behavioral traits, culture fit signals)
- Common interview questions for this role at this company
- How behavioral interviews are structured (STAR method expectations, etc.)
- Timeline and decision-making process

#### 2c. Role-Specific Context
Search for:
- What the team or department does within the company
- Recent news about the company relevant to this role (product launches, strategic shifts, expansions)
- The broader industry context that makes this role important

#### Research Brief Deliverable
After researching, compile a research brief and save it at the **company level** (`research/[company].md`), shared across all roles at that company. The brief has two clearly separated sections:

```
# [Company Name] — Research Brief
# Last updated: YYYY-MM-DD

---

## Section 1: Company Research (reusable across roles)

### Company Overview
[Mission, size, stage, key stats with inline source citations]

### Company Culture & Values
[Core cultural signals, watch items, with inline source citations]

### Interview Process & What They Look For
[Stages, what they screen for, with inline source citations]

### Sources
[Numbered list of all URLs consulted]

---

## Section 2: Role-Specific Research

### [Job Title] (YYYY-MM)

#### Role & Team Context
[Team function, why this role matters now, with inline source citations]

#### Key Themes for Resume Targeting
[3-6 bullet points identifying the most important themes to hit in the resume, synthesized from the research]
```

When applying to a second role at the same company, append a new dated subsection under Section 2. Do not overwrite previous role sections. If company-level info has changed, update Section 1 with a dated annotation.

Present the research brief to the user. Ask: "Does this match your understanding of the company? Anything you'd add or correct?" Wait for confirmation before proceeding.

### Phase 3: Adaptive Q&A

This is the most important phase. You're interviewing the user to surface their best, most relevant experiences. The questions should be informed by:
- The job description requirements
- The company's values and what they screen for
- Gaps between the user's current resume and the role
- The interview format (so bullets also serve as interview prep)

#### Round Structure

**Round 1 — Core Experience Mapping**
Ask 3-5 questions that map the user's experience to the role's primary responsibilities. Focus on:
- Technical skills the role requires (with examples of use at scale)
- Cross-functional collaboration and stakeholder management
- Both fast-turnaround and strategic/long-term work

**Round 2 — Company Values Alignment**
Ask 3-5 questions that surface experiences mapping to the company's specific values. For each value, craft a question that would pull out a relevant story. For example, if the company values "courage" and "candor," ask about a time the user pushed back on a flawed assumption or delivered difficult feedback.

**Subsequent Rounds (if needed)**
Continue asking if:
- Key job requirements still have no supporting experience surfaced
- Answers were thin on specifics (numbers, tools, outcomes)
- There are company values with no corresponding story yet

Stop when:
- Every major job requirement has at least one strong supporting experience
- Every key company value has a corresponding story or example
- The user's answers include enough concrete detail to write specific bullets

After each round, briefly summarize what you've captured and what gaps remain, so the user can see progress and knows what you still need.

### Phase 4: Bullet Point Generation & Change Review

#### 4a. Generate Tailored Bullet Points
Using the research and Q&A answers, draft resume bullet points. Each bullet should:

- Start with a strong action verb
- Include specific, quantified impact where possible (%, $, time saved, records processed, users served)
- Use language that mirrors the company's values and the job description's terminology
- Be truthful — only use information the user provided

Organize bullets by the resume sections in the user's existing resume (e.g., by role/company).

Present the bullets to the user and ask for feedback. Iterate until they approve.

#### 4b. Propose Resume Changes
Once bullets are approved, show a clear summary of proposed changes to the existing resume:

```
## Proposed Changes to Your Resume

### [Job/Company Section 1]
- REPLACE: "Old bullet text here"
  → WITH: "New targeted bullet text here"
- ADD: "New bullet that didn't exist before"
- KEEP: "Existing bullet that's already strong"

### Skills Section
- ADD: [skill from job description the user confirmed they have]

### Summary/Objective (if applicable)
- REPLACE: "Old summary"
  → WITH: "New summary tailored to role"
```

Wait for the user to review and approve each change. They may want to keep some original bullets, modify your suggestions, or skip certain changes. Respect their judgment.

### Phase 5: Final Resume Generation

Once all changes are approved:

1. Read the docx skill (at `/mnt/.claude/skills/docx/SKILL.md`) for best practices on document creation
2. Read the pdf skill (at `/mnt/.claude/skills/pdf/SKILL.md`) for PDF generation guidance
3. Recreate the resume incorporating all approved changes, preserving the user's original structure and formatting as closely as possible
4. **Verification step (mandatory):** Before generating the PDF, inspect the DOCX XML to verify all formatting rules are met:
   - Contact line: grep for `https://` and `http://` in the contact paragraph's `<w:t>` elements — none should exist in display text
   - Contact line: confirm all contact info is in a single `<w:p>` paragraph
   - Page count: convert to PDF and verify it does not exceed 2 pages. If it does, tighten bullets before proceeding.
   - Dashes: grep for em dashes (—) and en dashes (–) in bullet text — none should exist
5. Generate both DOCX and PDF versions
6. Save the research brief alongside the resume files

Deliver files using the naming convention `[company]-[role-slug]-[YYYY-MM].[ext]`:
- `resumes/[company]-[role-slug]-[YYYY-MM].docx`
- `resumes/[company]-[role-slug]-[YYYY-MM].pdf`
- `research/[company].md` (created or updated during Phase 2)

After delivering, ask: "Would you like me to adjust anything in the final documents?"

## Resume Formatting Rules (Mandatory)

These rules apply to every resume output. They were established through iteration and must be followed exactly.

1. **No dashes as punctuation.** No hyphens, en dashes, or em dashes used as sentence punctuation in bullets, summaries, or any resume text. Restructure the sentence or use commas instead.
2. **Contact line on one line.** Strip `https://` and `http://` prefixes from all URLs in the contact line display text (the hyperlink target can keep the full URL). E.g., display text must be `github.com/user` not `https://github.com/user`. After generating the final DOCX, verify the contact paragraph XML contains no `https://` or `http://` in any `<w:t>` element within the contact line paragraph.
3. **No rogue spacers between bullets.** Within a company section, all bullets must be evenly spaced with no empty paragraphs between them.
4. **One spacer line between company sections.** Insert one empty spacer paragraph before each company header table (except the first company after the EXPERIENCE header).
5. **One spacer line before SKILLS.** The SKILLS section header must have an empty spacer paragraph above it.
6. **Skills formatting.** "Skills:" prefix is bold; the skill list text is not bold.
7. **Preserve base resume layout.** Use the base resume's table-based company headers (company | date row, title | location row). Do not flatten to inline text.
8. **No fabrication.** All bullet content must come from the user's base resume text or verified stories in memory.md. No invented claims, inflated numbers, or tools/skills the user didn't mention.

## Important Reminders

- If web research fails to find information about a company's culture or interview process, be transparent. Say what you couldn't find and ask the user if they have any insider knowledge or resources to share.
- Don't rush through the Q&A. The quality of the resume depends entirely on the quality of the stories and details you extract. It's better to ask one more round of questions than to generate vague bullets.
- Treat the user's existing resume with respect. Explain why you're suggesting changes, not just what to change.
- The research brief serves double duty: it informs the resume AND helps the user prepare for interviews. Make it genuinely useful.
