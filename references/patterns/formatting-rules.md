# Formatting Rules Reference
# Applies to: USER-FACING APPLICATION OUTPUTS — resumes, cover letters, speaking points, thank-you letters, recruiter prep, any artifact sent to a hiring contact
# Last updated: 2026-05-02 (clarified scope; see Scope section below)

---

## Scope

These rules apply to **user-facing application outputs** — the artifacts a candidate sends to a recruiter, hiring manager, or networking contact. They do NOT apply to internal Claude-facing documentation: SKILL.md files, SPEC.md, CLAUDE.md, ROADMAP.md, DESIGN_DOC.md, SESSION_LOG.md, ONBOARDING.md, ROADMAP, and any markdown under `skills/*/references/`.

The reasoning: punctuation discipline matters when the audience is a human reviewer at the receiving company. Internal docs are read by Claude and the project owner; readability dominates over rigid punctuation rules.

If you are unsure whether a file is in scope, ask: "Does this file get sent to or shown to someone outside the project?" If yes, the rules apply.

## Universal Rules (in-scope outputs)

1. **No dashes as punctuation.** No hyphens, en dashes, or em dashes used as sentence punctuation in user-facing outputs. Restructure the sentence, use commas, semicolons, or periods instead.
2. **No fabrication.** All claims about companies or user experience must come from verified research or memory.md.

## Resume-Specific Rules

3. **Contact line on one line.** Strip `https://` and `http://` prefixes from all URL display text. Verify in DOCX XML that no `<w:t>` element contains these prefixes.
4. **No rogue spacers between bullets.** Within a company section, all bullets must be evenly spaced with no empty paragraphs between them.
5. **One spacer line between company sections.** Insert one empty spacer paragraph before each company header table (except the first company after the EXPERIENCE header).
6. **One spacer line before SKILLS.** The SKILLS section header must have an empty spacer paragraph above it.
7. **Skills formatting.** "Skills:" prefix bold; skill list itself not bold.
8. **Preserve base resume layout.** Use the base resume's table-based company headers (company | date, title | location). Do not flatten to inline text.
9. **Two-page max.** Resume must never exceed 2 pages. If it does, tighten bullets before generating PDF.

## Cover Letter Rules

10. **Signature block.** End every cover letter with the user's preferred sign-off from memory.md.
11. **Three to four paragraphs max.** No flattery, no cliches.
12. **PDF format.** 1-inch margins, contact header, date, greeting, body, signature.

## Speaking Points Rules

13. **Cheat sheet, not a script.** Each point scannable in one sentence.
14. **Both .md and .pdf.** Always generate both formats.

## Source of Truth

- **memory.md** -- user preferences, signature, formatting rules
- **Skill SKILL.md files** -- skill-level enforcement of these rules
- **This file** -- consolidated reference (keep in sync with above two)

## Why this scoping was clarified

Originally the rule was written as "applies to all outputs in any context." In practice the project's own internal documentation (SKILL.md files, SPEC.md, design docs) used em-dashes liberally because they aid readability for technical content. The clarification on 2026-05-02 makes the rule match how the project actually behaves: strict on user-facing application artifacts, lenient on internal docs.

If you ever ship an artifact to a recruiter, run a final em-dash scan over it before delivery.
