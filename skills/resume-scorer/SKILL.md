---
name: resume-scorer
description: "Resume scoring skill that evaluates how well a resume matches a job description using a transparent, blended percentage breakdown across keyword coverage, qualification match, and values alignment. Use this skill whenever the user wants to: score a resume against a JD, check how well their resume fits a role, compare before/after resume versions, evaluate resume strength, get a match percentage, identify gaps between their resume and a job posting, or understand what's missing. Requires decoded-jd to have run first — the decoded JD provides the implicit expectations and values alignment layer that makes the score meaningful. This skill produces specific, actionable suggestions that hand off to resume-targeter and other skills."
---

# Resume-Job Match Scorer

A transparent scoring skill that evaluates how well a resume matches a job description, producing a blended percentage with a detailed breakdown so you know exactly where you're strong and where the gaps are.

## Why This Skill Exists

Applying to jobs without knowing your fit level is like submitting a test without checking your answers. This skill gives you an honest, structured assessment before you hit "apply" — and after you've targeted your resume, it shows you exactly how much better you got. The score isn't a gatekeeper — it's a diagnostic tool that tells you where to focus effort.

## Core Principles

1. **Transparent scoring.** Every percentage comes with an explanation. No black box. The user should understand exactly why they scored what they scored and what would change the number.

2. **Blended, not simplistic.** Keyword matching alone is misleading. The score blends three dimensions: keyword coverage (do you mention what they mention?), qualification match (do you actually meet the requirements?), and values alignment (does your resume speak their language?).

3. **Actionable output.** The score is only useful if it tells you what to do. Every gap gets a specific suggestion — concrete enough to hand off to resume-targeter or another skill.

4. **Honest, not encouraging.** If the fit is a stretch, say so. The user trusts this tool because it doesn't inflate scores or soften gaps.

## Prerequisites

**Requires decoded-jd.** This skill reads the `decoded-jd.md` file for the role, which provides:
- Explicit must-haves and nice-to-haves
- Implicit expectations with confidence tags
- Key themes for targeting
- Values alignment signals

Without decoded-jd, the values alignment dimension has no foundation and the qualification match misses implicit requirements. If decoded-jd hasn't been run, the skill should stop and say: "I need a decoded JD to score accurately. Want me to run decoded-jd first?"

**Also reads:**
- The user's resume (base or targeted version, depending on when in the workflow)
- `memory.md` for background context on the user's actual experience (some skills/stories may not be on the resume but are relevant to fit assessment)

## Scoring Methodology

### Three Dimensions

#### 1. Keyword Coverage (Weight: 30%)

Measures whether the resume contains the terms, tools, and concepts the JD explicitly mentions.

**How it works:**
- Extract all technical skills, tools, frameworks, methodologies, and domain terms from the JD
- Check each against the resume (exact match and reasonable synonyms — e.g., "A/B testing" matches "experimentation")
- Score = (matched keywords / total JD keywords) * 100

**What it catches:** Missing tool names, missing methodology references, terminology gaps.

**What it misses:** Whether you actually have depth in those tools (that's qualification match) or whether your framing resonates with the company (that's values alignment).

#### 2. Qualification Match (Weight: 40%)

Measures whether the resume demonstrates you meet the stated and implicit requirements.

**How it works:**
- Pull all must-haves from decoded-jd (explicit) and implicit expectations tagged [HIGH] or [MED]
- For each, assess the resume: Strong (clear evidence), Partial (related but not direct), or Gap (not addressed)
- Score = weighted sum: Strong = 100%, Partial = 50%, Gap = 0%
- Must-haves weighted 2x vs. nice-to-haves

**What it catches:** Experience gaps, seniority mismatches, missing proof of specific competencies.

**What it misses:** Whether you're framing your experience in a way that resonates (that's values alignment).

#### 3. Values Alignment (Weight: 30%)

Measures whether the resume speaks the company's language and mirrors its cultural priorities.

**How it works:**
- Pull key themes from decoded-jd and company values/cultural signals
- Assess whether the resume's framing, word choices, and story selection reflect those themes
- Score each theme: Aligned (resume clearly speaks to this), Partial (touches on it but not strongly), Absent (not reflected)
- Score = weighted sum: Aligned = 100%, Partial = 50%, Absent = 0%

**What it catches:** Framing mismatches (your resume emphasizes operational reliability but they want innovation), missing cultural signals (they value data storytelling but your bullets are tool-lists), tone misalignment.

**What it misses:** This is the most subjective dimension. Confidence depends heavily on decoded-jd research quality.

### Overall Score

Overall = (Keyword * 0.30) + (Qualification * 0.40) + (Values * 0.30)

**Score interpretation:**
- **85-100%**: Strong match. Minor tweaks at most.
- **70-84%**: Moderate match. Targeted revisions would meaningfully improve fit.
- **55-69%**: Stretch. Significant gaps to address. Consider whether supplementary materials can bridge the gap.
- **Below 55%**: Weak fit for this specific role. May still be worth applying depending on context, but expectations should be calibrated.

## Workflow

### Opt-in Flow

The scorer integrates into the orchestrator workflow with an explicit opt-in:

**At the start (before resume-targeter):**
> "Want me to score your resume against this JD before we start targeting? This gives us a baseline to measure improvement."

- **YES** → Score the base resume (before-score). After resume-targeter finishes, automatically score the targeted resume (after-score) and show the delta.
- **NO** → Skip the before-score. After resume-targeter finishes, ask: "Want me to score the final resume?" If yes, score once (no before/after comparison).

### Phase 1: Gather Inputs

Collect:
- **Resume to score** — the base resume (for before-score) or targeted resume (for after-score)
- **Decoded JD** — read from `decoded-jds/[company]-[role-slug]-[YYYY-MM].md`
- **Memory** — read `memory.md` for context on the user's actual experience beyond what's on the resume

### Phase 2: Score

Run the three-dimension assessment. For each dimension, work through every item methodically — don't skip requirements or rush the evaluation.

### Phase 3: Deliver Score Report

Present two layers:

**Quick glance (in chat):**
> **Overall: 74%** (Keyword: 82% | Qualification: 85% | Values: 55%)
> **Fit: Moderate** — Strong technical match, but values framing needs work.
> **Biggest gaps:** Experimentation language, measurement framework framing, return narrative.

**Detailed report (saved as markdown):**

Full breakdown with per-item assessments, specific gap analysis, and actionable suggestions.

### Phase 4: Suggestions

After scoring, produce two types of suggestions:

#### Resume Corrections
Specific changes to the resume that would improve the score. Each suggestion should:
- Reference a specific bullet, section, or gap
- Explain what to change and why
- Estimate the score impact (e.g., "Adding experimentation language to Nike bullet 2 would move Values Alignment from Partial to Aligned on the 'experimentation mindset' theme")

Example:
> - **Apple bullet 2** (KPI governance): Add the phrase "measurement framework" — the JD uses this exact term and your bullet describes exactly that but doesn't use the language.
> - **Nike section**: Add the studio health score KPI story as a new bullet — this directly addresses the "measurement frameworks" theme which is currently a gap.
> - **Summary**: Include "experimentation" and "A/B testing" — these are must-have keywords currently missing from your summary.

#### Supplementary Material Recommendations
When gaps can't be fully closed by resume changes alone, recommend other materials:

Example:
> - **Cover letter** (via why-this-company skill): Address the return-to-Disney narrative. The resume can't explain "why here, why now" but a cover letter can.
> - **Portfolio piece** (via portfolio-coach skill): An A/B test case study would concretely demonstrate experimentation skills that the resume only claims.

Each recommendation names the skill that would produce it, creating a natural handoff in the orchestrator.

### Phase 5: Before/After Comparison (if opted in)

When both before and after scores exist, present a delta report:

> **Before → After**
> Overall: 54% → 81% (+27)
> Keyword: 62% → 88% (+26)
> Qualification: 65% → 85% (+20)
> Values: 35% → 70% (+35)
>
> **What improved:**
> - Added experimentation language across 3 bullets (+15 keyword, +20 values)
> - Nike KPI framework bullet addressed measurement gap (+10 qualification)
> - Summary reframed around Disney's priorities (+15 values)
>
> **Still open:**
> - No direct A/B test case study (portfolio would close this)
> - Return-to-Disney narrative not addressed in resume (cover letter territory)

## Output Format

Save the full score report as markdown:

**Location:** `scores/[company]-[role-slug]-[YYYY-MM]-before.md` or `scores/[company]-[role-slug]-[YYYY-MM]-after.md`

```markdown
# [Company] — Resume Score: [Job Title]

## Score Summary
- **Overall: X%** (Keyword: X% | Qualification: X% | Values: X%)
- **Fit: [Strong / Moderate / Stretch / Weak]**
- **Resume scored:** [Base / Targeted]
- **Date:** [date]

## Keyword Coverage (X%)

| JD Keyword/Term | Found in Resume? | Where | Notes |
|---|---|---|---|
| SQL (advanced) | Yes | Apple, WF, Nike | Multiple mentions, clear depth |
| A/B testing | No | — | Not mentioned anywhere |
| ... | ... | ... | ... |

## Qualification Match (X%)

| Requirement | Type | Rating | Evidence | Gap Action |
|---|---|---|---|---|
| 7+ years analytics | Must-have | Strong | 6+ years across 5 companies | Slight shortfall on YOE |
| Experimentation design | Must-have | Partial | Dashboard A/B approach at Nike | Needs explicit framing |
| ... | ... | ... | ... | ... |

## Values Alignment (X%)

| Theme | Rating | Resume Signal | What's Missing |
|---|---|---|---|
| Data storytelling | Aligned | Stakeholder redirection, dashboard design | — |
| Experimentation mindset | Partial | KPI framework, regression | Needs A/B language |
| ... | ... | ... | ... |

## Suggestions

### Resume Corrections
1. ...
2. ...

### Supplementary Materials
1. ...
2. ...

## Before/After Delta (if applicable)
[Delta report as described above]
```

## Relationship to Other Skills

**Depends on:** decoded-jd (must run first to provide the implicit expectations and values layer)

**Bookends resume-targeter:** Scores before resume-targeter runs (baseline), then automatically scores after (improvement measurement). The before/after delta shows the tangible value of targeting.

**Feeds into:** why-this-company and portfolio-coach through specific supplementary material recommendations. Each recommendation names the downstream skill.

**Standalone use:** Can score any resume against any decoded JD at any time — useful for re-evaluating after manual edits or comparing different resume versions.

## Important Reminders

- The score is a diagnostic tool, not a pass/fail gate. A 60% score with strong qualification match might still be worth applying — especially if supplementary materials can close the gap.
- Be honest about low scores. Inflating the number to make the user feel better defeats the purpose.
- The values alignment dimension is inherently more subjective than the other two. Flag this in the output and note when your confidence is lower.
- When scoring a base resume (before targeting), expect a lower score. That's the point — it shows the room for improvement.
- The suggestions section is where the real value lives. A score without actionable next steps is just a number.
