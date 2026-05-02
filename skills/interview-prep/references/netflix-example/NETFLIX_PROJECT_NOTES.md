# CLAUDE.md — Netflix SQL Prep project

> **Path notice (2026-05):** Sections below that reference `/home/claude/`, `/mnt/user-data/outputs/`, or other sandbox paths describe an **older Claude artifact build environment**, not this repo’s layout on disk. On this machine, treat **`Netflix Interview Prep/files/`** (this folder’s siblings: `index.html`, `netflix-sql-prep.jsx`, deploy folders, root `README.md`) as the source of truth. Ignore obsolete absolute paths when locating files.

This file is Claude's working context for the Netflix interview-prep project. If you're a Claude instance reading this in a future session, this is what you need to be immediately productive.

---

## 1. Project goal

Help Milan prepare for a **Netflix Data Analyst, Production Finance Operations & Innovation** interview (job req JR38497, LA). Known format: roughly one week of prep, technical round is ~4 SQL questions + 1 Python question in a 45–60 minute CoderPad session.

The deliverable is an iPhone/laptop-installable PWA that teaches SQL through the dual lens of (a) Netflix's actual tech stack (Presto/Trino on Iceberg) and (b) Production Finance's actual domain (vendors, productions, payments, crew, AP/HUB reconciliation).

---

## 2. How the content was researched

### Netflix-specific signal sources

The app's framing, domain vocabulary, and problem selection came from:

- **Netflix Tech Blog** posts on data infrastructure (confirmed Presto/Trino, Iceberg tables, daily batch pipelines for financial data)
- **Netflix job description** for JR38497 — flagged Production Finance Operations as distinct from core Data Science, emphasizing vendor management, production close, variance analysis
- **Glassdoor / Blind** data points on Netflix DA interviews — 4-SQL-plus-1-Python structure, CoderPad, case-study style prompts grounded in business questions
- **Public Netflix financial vocabulary** — "ATL/BTL" (above/below the line), "1099 vendors," "fiscal-month-close," "burn rate" — these appear in the problem prompts to build domain fluency

### Why these 11 topics

The topic list is ranked by expected interview frequency based on the above research:

1. **Tier 1 (very likely):** Multi-table joins, window functions, CTEs, date manipulation, deduplication, CASE, NULL handling — every SQL interview touches these
2. **Tier 2 (likely for this role):** FULL OUTER JOIN (reconciliation is a Production Finance staple), self-joins, set operations — these appear when the role has a finance/ops flavor
3. **Python (PY):** pandas — one question expected; groupby/merge/rolling are the modal asks

The domain examples were deliberately chosen to teach a SQL pattern while surfacing a real Netflix concern (e.g., the "concentration risk" worked example in Joins teaches conditional aggregation + ROW_NUMBER windowing while modeling the actual risk Netflix cares about: single-vendor over-exposure on a production).

---

## 3. Directory layout

### Source files (Claude's workspace)

```
/home/claude/
├── learning/
│   └── app.jsx               # Master React source, ~5500 lines
├── vercel-app/
│   ├── app-web.jsx           # JSX with `import React` / `export default` stripped
│   ├── index.html            # Built deployment file (what Vercel serves)
│   └── build.py              # Injects app-web.jsx into index.html template
└── convert.py                # Runs first: app.jsx → vercel-app/app-web.jsx
```

### Delivered files (what the user sees)

```
/mnt/user-data/outputs/
├── index.html                # The built app, ~250KB, self-contained
├── netflix-sql-prep.jsx      # The JSX source, for reference
├── manifest.json             # PWA manifest
├── sw.js                     # Service worker (offline cache)
├── icon-192.png, icon-512.png
├── README.md                 # User-facing deployment instructions
├── CLAUDE.md                 # This file
└── SPECS.md                  # Product/pedagogy spec
```

### Build pipeline

```
learning/app.jsx                      [edit this]
    ↓ python3 /home/claude/convert.py
vercel-app/app-web.jsx                [intermediate]
    ↓ python3 /home/claude/vercel-app/build.py
vercel-app/index.html                 [ship this]
    ↓ cp
/mnt/user-data/outputs/index.html     [user download]
```

The `convert.py` step strips `import React from 'react'`, removes `export default`, and preserves the component function. The `build.py` step slots the resulting JSX into a Babel-runtime template with CDN script tags (React 18, Tailwind, Babel-standalone, all from jsDelivr).

---

## 4. Content architecture inside app.jsx

### Three main data structures

```js
SCHEMAS = {                       // Netflix-themed sample tables for schema panels
  productions: { columns, rows },
  vendors:     { columns, rows },
  payments:    { columns, rows },
  // ...
}

TOPIC_EXTRAS = {                  // Hand-authored medium + hard Came/Saw content
  joins:       { workedMedium, workedHard, fadedMedium, fadedHard },
  windows:     { ... },
  // ... all 11 topics present
}

TOPICS = [                        // Master topic list with retrieval problems
  {
    id: 'joins',
    title: 'Multi-Table Joins',
    tier: 'T1',
    worked:    { prompt, solution, walk },      // EASY worked for Came phase
    faded:     { prompt, scaffold, solution, walk },  // EASY faded for Saw
    retrieval: [                                // 3 problems for Conquered phase
      { difficulty: 'easy',   prompt, solution, schemas, selfExplain, explanation },
      { difficulty: 'medium', prompt, solution, schemas, selfExplain, explanation },
      { difficulty: 'hard',   prompt, solution, schemas, selfExplain, explanation }
    ]
  },
  // ... 11 topics total
]

EXAM_SQL = [                      // Real Netflix CodeSignal SQL questions (session 4)
  { id, category, title, prompt, concepts, difficulty, source, solution?, hint?, note? },
  // 29 questions from Glassdoor/Blind/1point3acres/DataLemur/InterviewQuery
]

EXAM_PY = [                       // Real Netflix CodeSignal Python questions (session 4)
  // 16 questions, same shape as EXAM_SQL
]

EXAM_META = { format, alternateFormat, keyInsight, highROI }
EXAM_PATTERNS_SQL = [...]          // Top 17 SQL patterns to drill
EXAM_PATTERNS_PY  = [...]          // Top 10 Python patterns to drill
```

### How the three phases render content

- **Came (worked examples):** `deriveWorkedExamples(topic)` returns `[easy, medium, hard]` by combining `topic.worked` (easy) with `TOPIC_EXTRAS[topic.id].workedMedium/Hard`. Each renders as schema panel + SQL + bulleted walkthrough.
- **Saw (faded practice):** `deriveFadedExamples(topic)` does the same but returns scaffolds with `_____` blanks; user fills them via a plaintext textarea.
- **Conquered (retrieval):** Each of `topic.retrieval` renders in the `QuestionCard` component with the full SQL editor (syntax highlighting, auto-indent, persistent via localStorage).

### Fallback behavior

If `TOPIC_EXTRAS[topic.id]` lacks `workedMedium` / `workedHard`, the deriver falls back to deriving medium/hard content from `topic.retrieval[1]` and `topic.retrieval[2]`. This kept the app functional during incremental content authoring — **all 11 topics are now hand-authored, so fallback no longer triggers in practice**.

---

## 5. Learning-science mapping: principle → code

The app is designed around six evidence-backed strategies. Each has a concrete rendering:

| Principle | Source | How it's implemented |
|---|---|---|
| **Worked examples** | Sweller & Cooper (1985); Renkl (2014) | Came phase shows complete solutions with numbered walkthroughs before any practice |
| **Fading / scaffolding** | Atkinson et al. (2003) | Saw phase strips portions of solutions, asking user to fill blanks |
| **Retrieval practice** | Roediger & Karpicke (2006) | Conquered phase forces free recall — blank editor, no scaffold |
| **Interleaving** | Rohrer (2012); Taylor & Rohrer (2010) | "Interleave" mode mixes problems across topics via Fisher-Yates shuffle with topic-spread constraint |
| **Spacing** | Cepeda et al. (2006) | Problems marked as "needs review" resurface after a cooldown; persisted in localStorage |
| **Dual coding** | Paivio (1971); Mayer (2009) | `SchemaPanel` shows column names + sample rows alongside every SQL prompt — visual + verbal encoding |
| **Elaboration** | Chi et al. (1994) | Italic "Before moving on, explain this back to yourself" prompts after first worked example; `selfExplain` field on retrieval problems |

These citations appear in the app footer so the user can sanity-check the approach.

---

## 6. The SQL editor

`QuestionCard` contains a custom `SqlEditor` component (~260 lines). Implementation notes:

- **Syntax highlighting:** transparent `<textarea>` layered over a syntax-colored `<pre>` element. User types in the textarea; a tokenizer runs on every keystroke and updates the pre. Keywords get pink, functions cyan, strings green, numbers amber.
- **Tab handling:** Tab key inserts 2 spaces (default browser behavior would move focus). Shift+Tab unindents.
- **Auto-indent:** Enter key maintains the prior line's leading whitespace.
- **Persistence:** Each question's editor content is saved to `localStorage` under a key like `netflix_sql_prep_q_joins_medium`. Progress survives page reloads.

The editor is deliberately NOT a full Monaco or CodeMirror — those would balloon the bundle beyond what CDN-only delivery allows. 260 hand-written lines preserves the "single-file, no build step, no auth" deployment story.

---

## 7. Deployment model

**Single static file, CDN-loaded dependencies, no build step on the server.**

- `index.html` contains all the app JS (as a `<script type="text/babel">` block) plus `<script src=>` tags pulling React 18, Tailwind, and Babel-standalone from jsDelivr (chosen over unpkg for better CORS under Vercel)
- PWA manifest + service worker = installable on iPhone home screen, works offline after first load
- `localStorage` stores progress; no backend
- User drags the folder onto Vercel or Netlify Drop, gets an HTTPS URL in ~30 seconds

Why this model over create-react-app / Vite / Next.js:
1. **Fragile surface area.** User is a non-engineer interview prepping; any step that could break (npm install, node version mismatch, CORS) blocks their study time.
2. **Time horizon.** App only needs to survive ~7 days; re-deploying is a minor cost.
3. **Portability.** The single HTML file can be opened by double-clicking in a file manager if the Vercel hosting ever fails.

---

## 8. How to resume in a future session

If Milan (or Claude reading this) returns to the project:

1. **Read this file first.** It's the fastest way to rebuild context.
2. **Check `/home/claude/learning/app.jsx` exists.** If the filesystem was reset (Claude sessions don't persist files across separate chats), you may need to reconstruct from `/mnt/user-data/outputs/netflix-sql-prep.jsx`.
3. **Before editing, verify the build pipeline works:**
   ```bash
   python3 /home/claude/convert.py && python3 /home/claude/vercel-app/build.py
   node -e "const s = require('fs').readFileSync('/home/claude/learning/app.jsx', 'utf8');
            const o = (s.match(/\{/g) || []).length;
            const c = (s.match(/\}/g) || []).length;
            console.log('braces:', o, c, o === c ? 'OK' : 'MISMATCH');"
   ```
4. **After edits, test with Playwright headless** before shipping. Template in section 10 below.
5. **Ship with `present_files`** to `/mnt/user-data/outputs/index.html` and `netflix-sql-prep.jsx`.

---

## 9. Common edits and gotchas

### Adding a new problem to an existing topic

Find the topic in the `TOPICS` array. To add a new retrieval problem, append to the `retrieval` array. To add or edit worked/faded content, edit `TOPIC_EXTRAS[topic_id]`.

### Changing a walkthrough

Every `walk` array is an array of strings, rendered as a numbered list. Each string should be 1–3 sentences. Keep bullets substantive — this is where the pedagogy lives.

### str_replace pitfalls observed in this project

- Large replacements (>500 lines) sometimes fail silently; split into per-topic chunks
- The `old_str` must be unique and character-exact — copy from `view` output without the line-number prefix
- After any successful edit, previous `view` output of that file is stale; re-view before the next edit to the same file
- Always run the brace-balance check after large edits

### Tailwind classes

The CDN Tailwind compiles classes on page load by scanning the DOM. It only includes classes it sees — so dynamic string concatenation like `` `bg-${color}-500` `` won't work. Always use full class names.

### React without build tools

The app uses `React.useState` etc. (not `import { useState }`) because there's no bundler to resolve imports. If you add new React features, reference them as `React.X` everywhere.

---

## 10. Testing template

```bash
cd /home/claude/vercel-app && python3 -m http.server 8775 > /tmp/httpd.log 2>&1 &
HTTPD_PID=$!
sleep 1

cat > /tmp/verify.cjs << 'EOF'
const { chromium } = require('/home/claude/.npm-global/lib/node_modules/playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('http://localhost:8775/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(6000);
  const diag = await page.evaluate(() => ({
    buttons: document.querySelectorAll('button').length,
    hasContent: document.body.innerText.includes('Multi-Table Joins'),
  }));
  console.log('diag:', JSON.stringify(diag));
  console.log('errors:', errors.length ? errors : 'none');
  await browser.close();
})();
EOF
node /tmp/verify.cjs
kill $HTTPD_PID 2>/dev/null
```

Port numbers keep climbing across turns (8768, 8769, 8770...) because killed Python servers sometimes leave ports in TIME_WAIT state for ~60 seconds.

---

## 11. Session journal

| Date | Session work |
|---|---|
| 2026-04-18 (session 1) | Initial research, 7-day plan, full React app with 11 topics + 33 retrieval problems built; SQL editor integrated; PWA wrapper + Vercel deploy docs; initial hand-authored easy worked examples |
| 2026-04-18 (session 2) | Expansion to 3 difficulties per topic. Hand-authored medium + hard worked examples + faded scaffolds for all 11 topics in `TOPIC_EXTRAS`. Each walkthrough 6–10 bullets explaining the reasoning, not just the SQL |
| 2026-04-18 (session 3) | Added CLAUDE.md and SPECS.md documentation |
| 2026-04-20 (session 4) | Added "Real Qs" (exam) tab as third mode alongside Learn/Interleave. Compiled from `netflix-data-analyst-2026-04-codesignal-prep.md` — 29 SQL + 16 Python questions from real candidate reports. Each question has source attribution, difficulty pill, concepts tags, optional hint, optional solution, and (for SQL) a practice editor. 17 of 45 have hand-written solutions for the highest-frequency patterns. Includes meta banner with format expectations + "Patterns to Drill" sub-tab with SQL (17) and Python (10) pattern-reinforcement tables. |

---

## 12. Known limits

- **No evaluation of user-typed SQL.** The editor is for thinking/practice; solutions are compared visually against the provided answer. A real code-runner would require a backend.
- **localStorage can be cleared.** iOS Safari clears web-app data after ~7 days inactive; warned in README.
- **Bundle weight.** ~250KB HTML; CDN deps add ~400KB on first load. Fine for prep tool; would be wrong for production.
- **One user, one device's worth of state.** No sync, no accounts.
- **No images, diagrams, or ERDs.** Schema is shown as text tables. Adding visual ERDs would require SVG authoring or an image asset pipeline.

None of these are bugs — they're deliberate scoping for a 7-day-horizon study tool.
