# Netflix Regression Eval

**Purpose:** Prove the new generic `interview-prep` skill produces a structurally-equivalent PWA when fed Netflix-shaped content. This is a structural regression — content quality is intentionally placeholder-grade. A real Netflix run authors hand-crafted worked examples through Phase D of the skill workflow.

**Last run:** 2026-05-02 (Phase 5 of UJA v0.1.0 build)

**Result:** ALL CHECKS PASS

---

## What the regression covers

| Dimension | Netflix reference build | This regression run | Match? |
|---|---|---|---|
| Topics | 11 (10 SQL + 1 Python) | 11 (10 SQL + 1 Python) | ✅ |
| Phases per topic | Came / Saw / Conquered | Came / Saw / Conquered | ✅ |
| Difficulties per phase | easy, medium, hard | easy, medium, hard | ✅ |
| Total problem cards | 99 (11 × 3 × 3) | 99 (11 × 3 × 3) | ✅ |
| Real Questions tab | sourced entries | sourced entries (2 placeholder) | ✅ structurally |
| Patterns tab | SQL + Python sub-sections | SQL + Python sub-sections | ✅ |
| Citation footer | 12 references | 12 references | ✅ |
| Bundle weight | ~344 KB (Netflix shipped) | ~119 KB (regression) | ✅ both under 400 KB |

The regression bundle is smaller than the Netflix shipped bundle because the
regression content is placeholder-quality. A real Netflix run with hand-authored
walkthroughs, full schema panels, and 30+ sourced real questions would push the
bundle weight closer to the Netflix-shipped figure.

## What the regression does NOT cover

- **Content quality.** The regression problem cards are intentionally placeholder.
  Quality is validated through the human-in-the-loop checkpoints in Phase D of
  the actual skill workflow.
- **Visual fidelity.** No pixel comparison against the Netflix build. Visual
  parity is not a goal; the Netflix build was bespoke and the new PWA is a
  generic template.
- **PWA install on a real iOS device.** The smoke test is headless Chromium.
  iOS PWA install is verified manually per build (see SPEC §6.4 acceptance #7).
- **Service worker offline behavior.** The smoke test does not toggle network
  connectivity. SW registration is checked; offline reload is a manual step.

## How to re-run

```bash
cd "Ultimate Job Assistant"

# 1. Generate regression content
python3 skills/interview-prep/evals/build_netflix_regression.py
# → writes skills/interview-prep/evals/netflix-regression-content.json

# 2. Build the PWA
python3 skills/interview-prep/template/build_pwa.py \
  skills/interview-prep/evals/netflix-regression-content.json \
  /tmp/uja-netflix-regression

# 3. Smoke test
cp skills/interview-prep/template/smoke_test.cjs /tmp/uja-netflix-regression/
cd /tmp/uja-netflix-regression
node smoke_test.cjs .
# expect exit 0 with "ALL CHECKS PASS"
```

The CI workflow (`.github/workflows/ci.yml`) runs steps 2–3 against
`sample-content.json`, not the regression content. The regression is a
heavier check that's run on demand or before tagging a release.

## What to look for if it fails

- **Schema validation failure.** Almost certainly the schema or the regression
  generator drifted apart. Re-read `content-schema.json`; align the generator.
- **Brace imbalance.** Usually a JSX bug in `app.jsx.template` introduced by an
  unbalanced edit. Use `node -e "const html = require('fs').readFileSync('index.html', 'utf8'); console.log('{:', (html.match(/\{/g) || []).length, '} :', (html.match(/\}/g) || []).length);"`
- **Bundle exceeds 400 KB.** Either the template grew (refactor) or the content
  is genuinely heavy (move heavy walks to lazy-loaded JSON).
- **`pageerror` events.** Babel-standalone is reporting a runtime JSX error.
  Check the browser console manually by running `python3 -m http.server` in the
  build directory and opening it in a browser.
- **`__CONTENT__ not injected`.** Build script `render()` likely stopped replacing
  `{{CONTENT_JSON}}` because of a token-clash with the content (rare).
- **Editable textarea didn't accept input.** Usually means the wrong textarea
  was targeted. Saw and Conquered phases have aria-label `*attempt*`; worked
  examples are read-only by design.

## Provenance

The original Netflix Interview Prep project's spec, project notes, and user-facing
README live at `skills/interview-prep/references/netflix-example/`. This regression
mirrors the structural shape they describe in §3 (Topic List) and §6.4 (Acceptance
Criteria).
