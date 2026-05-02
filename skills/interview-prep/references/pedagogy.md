# Pedagogy reference — interview-prep skill

The `interview-prep` skill is built around evidence-based principles from cognitive science. This document is the canonical reference for what those principles are, where they appear in the generated PWA, and the source citations that render in the PWA footer.

If you (Claude or human) ever need to defend a design choice in this skill, this is the file you cite.

---

## The principles, mapped to the PWA

### Worked examples (Sweller & Cooper, 1985; Renkl, 2014)

A "worked example" is a complete solution presented before any practice — the learner reads the solution rather than generating it. Cognitive Load Theory predicts (and decades of evidence support) that worked examples reduce extraneous load during initial encoding, freeing working memory for the underlying schema.

**Where it appears:** the **Came** phase. Each topic shows three complete solutions (easy, medium, hard) with full SQL/Python/markdown answers and 6–10-bullet walkthroughs that explain the *choices* in the solution.

**Critical detail:** walkthroughs that just label the code ("This is an INNER JOIN") provide minimal value. Walkthroughs that explain the *decision* ("INNER JOIN here because orphan payments should drop out — we only care about payments that match a production") are what actually transfer.

### Fading (Atkinson, Renkl & Merrill, 2003)

After exposure to worked examples, gradually remove parts of the solution to shift cognitive load back to the learner. Done well, fading produces near-optimal practice trajectories.

**Where it appears:** the **Saw** phase. Same problems as the worked examples, but with 4–8 strategic blanks at error-prone tokens (join type, NULL operator, window function choice, threshold literals).

**Critical detail:** blanks placed at trivia (aliases, formatting) waste a fading opportunity. Blanks at the genuinely hard choice points ("ROW_NUMBER vs RANK", "IS NULL vs = NULL") are what produce the gain.

### Retrieval practice (Roediger & Karpicke, 2006)

The act of retrieving information from memory — not re-reading or re-watching — is what cements long-term retention. Testing yourself is a learning event, not a measurement event.

**Where it appears:** the **Conquered** phase. New problems (not the same prompts as worked or faded), no scaffolding, blank editor, schema panel only. The user writes the answer freely; their attempt persists to localStorage.

**Critical detail:** the value comes from the struggle. The editor deliberately doesn't run the SQL because instant feedback short-circuits the retrieval effort.

### Interleaving (Rohrer, 2012; Taylor & Rohrer, 2010)

Mixing problems across topics in a single session improves discrimination among similar concepts and produces better long-term retention than blocking practice on one topic at a time. The catch: interleaving feels harder, so learners often prefer (and self-select into) blocked practice — but the test results favor interleaving.

**Where it appears:** the **Interleave mode** toggle in the PWA's top nav. When on, problems are pulled from across all topics in shuffled order with a topic-spread constraint (no two consecutive problems from the same topic).

**Critical detail:** the PWA shows a one-line nudge — "Interleave feels harder. That's the point." — to counteract the learner's metacognitive resistance.

### Spacing (Cepeda et al., 2006)

Distributing study sessions over time produces dramatically better retention than concentrated study, even at constant total study time. The optimal gap depends on the desired retention horizon, but for any horizon the spaced version dominates.

**Where it appears:** problems can be flagged for review; flagged problems resurface after a cooldown that lengthens with each correct pass (initially 1 day, then ~3, ~7).

**Critical detail:** for a 7-day prep horizon, full SM-2 / Anki-fidelity spaced repetition is over-engineered. The flag-and-cooldown is sufficient. (Real SRS is in `ROADMAP.md` Track 4 for longer-horizon use.)

### Dual coding (Paivio, 1971; Mayer, 2009)

Information presented in both verbal and visual modalities is retained better than either alone, because the two encoding systems support each other at retrieval time.

**Where it appears:** every prompt that references a table is accompanied by a **schema panel** showing column names and 3–5 sample rows. The verbal prompt and the visual schema work together.

**Critical detail:** sample rows must be **internally consistent** across the entire site (vendor V001 means the same thing on every panel). Inconsistency forces the learner to maintain multiple mental models and burns the dual-coding benefit.

### Elaboration (Chi et al., 1994)

Generating self-explanations during study — explaining the material in your own words — produces deeper understanding than passively re-reading. The act of explaining surfaces gaps in your own knowledge.

**Where it appears:** an italic "Before moving on, explain this back to yourself in your own words" prompt after the first worked example of each topic. Retrieval problems include a `selfExplain` seed question ("Why did I choose a LEFT JOIN here?").

**Critical detail:** the prompt is gentle, not gating. Pushing the user past the self-explain step is fine; the cost of skipping it is paid in slower learning, not in being blocked.

---

## Citations (PWA footer)

These are the references rendered in the citation footer of every generated PWA, in the order they should appear:

```
- Atkinson, R. K., Renkl, A., & Merrill, M. M. (2003). Transitioning from studying examples to solving problems. Journal of Educational Psychology, 95.
- Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., & Rohrer, D. (2006). Distributed practice in verbal recall tasks. Psychological Bulletin, 132.
- Chi, M. T. H., et al. (1994). Eliciting self-explanations improves understanding. Cognitive Science, 18.
- Dunlosky, J., et al. (2013). Improving students' learning with effective learning techniques. Psychological Science in the Public Interest, 14.
- Mayer, R. E. (2009). Multimedia Learning (2nd ed.). Cambridge University Press.
- Paivio, A. (1971). Imagery and Verbal Processes. Holt, Rinehart and Winston.
- Renkl, A. (2014). Toward an instructionally oriented theory of example-based learning. Cognitive Science, 38.
- Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning. Psychological Science, 17.
- Rohrer, D. (2012). Interleaving helps students distinguish among similar concepts. Educational Psychology Review, 24.
- Sweller, J. (1988). Cognitive load during problem solving. Cognitive Science, 12.
- Sweller, J., & Cooper, G. A. (1985). The use of worked examples as a substitute for problem solving. Cognition and Instruction, 2.
- Taylor, K., & Rohrer, D. (2010). The effects of interleaved practice. Applied Cognitive Psychology, 24.
```

These are real, primary-source citations — not pop-science summaries. The skill should not substitute newer trade-press references for these; the primary-source list is what gives the PWA's pedagogical claims their credibility.

---

## What is NOT in scope

This file is a *reference for the pedagogy*. It is NOT:

- A full literature review (those exist elsewhere — see Dunlosky et al. 2013 for a great one)
- An evaluation framework for measuring the PWA's effectiveness on real users (that would be an A/B testable hypothesis, out of scope for v0.1.0)
- Rationale for why this specific topic list (that lives in the per-application `[convention]-format.md` Phase B output)

If a future SaaS version of UJA wants to add A/B-tested learning effectiveness measurement, that's a Track-5 item in `ROADMAP.md`.
