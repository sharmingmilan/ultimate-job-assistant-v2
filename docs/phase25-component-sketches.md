# Phase 25 component sketches — theme toggle, status pills, filter chips

**Source ADR:** ADR-003 D1 (filter chips), D2 (theme toggle), D3 (status pill style), D8 (top-bar shape).

**Purpose:** sketch the markup, behavior, and JS state machines for the three load-bearing interactive components. Block 2 implements these against the CSS variables in `website/v2/styles.css` (Block 1 commit).

---

## 1. Theme toggle

### Markup

```html
<button
  class="theme-toggle"
  type="button"
  aria-label="Switch theme"
  data-theme-toggle
>
  <!-- Sun icon visible when current theme is dark -->
  <svg class="theme-icon-sun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <circle cx="12" cy="12" r="4"></circle>
    <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"></path>
  </svg>
  <!-- Moon icon visible when current theme is light -->
  <svg class="theme-icon-moon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
  </svg>
</button>
```

CSS hides the inactive icon via `[data-theme="dark"] .theme-icon-moon { display: none }` and `[data-theme="light"] .theme-icon-sun { display: none }`. One button, one focus ring, one keyboard tab stop.

### Bootstrap script (in `<head>`, NOT deferred)

```html
<script>
  (function () {
    var stored = localStorage.getItem('uja-v2-theme');
    var theme = stored || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  })();
</script>
```

Runs synchronously before first paint to avoid theme-flash. ~6 lines minified.

### Toggle logic (in `app.js`)

```js
function setupThemeToggle() {
  var btn = document.querySelector('[data-theme-toggle]');
  if (!btn) return;
  btn.addEventListener('click', function () {
    var current = document.documentElement.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('uja-v2-theme', next);
  });
}
```

Total: ~10 lines.

### Keyboard activation

`<button>` element handles Enter and Space natively. No additional listener needed.

### Why localStorage and not URL hash or cookie

- localStorage persists across sessions without leaking to the network or site analytics (which don't exist anyway, but the principle holds).
- URL hash would add `#theme=light` to every share, which the user does not want.
- Cookies require a Set-Cookie response and would invite cookie-banner-laws conversation we don't want.

---

## 2. Status filter chip set

### Markup

```html
<div class="filter-chip-row" role="toolbar" aria-label="Filter by status">
  <button class="filter-chip" type="button" data-status="all" data-active>
    All <span class="filter-chip-count">0</span>
  </button>
  <button class="filter-chip" type="button" data-status="open">
    Open <span class="filter-chip-count">0</span>
  </button>
  <!-- ... one per status: submitted, interviewing, offer, closed, rejected -->
</div>
```

Empty count text on first render; populated by `app.js` after `index.json` fetch resolves.

### State machine

Multi-select with `All` as reset. State lives in JS as `Set<status>`. Default state: `{all: true}` (or empty set with All as the active class).

```js
var activeFilters = new Set(); // empty == "All"

function onChipClick(status) {
  if (status === 'all') {
    activeFilters.clear();
  } else {
    if (activeFilters.has(status)) {
      activeFilters.delete(status);
    } else {
      activeFilters.add(status);
    }
  }
  renderCards();
  renderChipActiveStates();
}

function passesFilter(card) {
  return activeFilters.size === 0 || activeFilters.has(card.status);
}
```

### Visual state

- Inactive chip: `--bg-card` background, `--text-muted` text, faint border. Subtle hover to `--bg-card-hover`.
- Active chip: full-color version of the status pill style (mid-saturation translucent bg + bright text per D3) — chip becomes a louder pill when selected.
- `All` chip: when no other chip is active, `All` is in the "active" visual state. Otherwise faint.

### Accessibility

- `<button>` not `<div>` — keyboard activation works natively.
- `role="toolbar"` on the container with `aria-label="Filter by status"`.
- Chip aria-pressed reflects active state: `aria-pressed="true"` when in `activeFilters`.

### Edge cases

- Zero packages: chip counts all zero. `All (0)` is shown; clicking does nothing visible.
- Filter selected but zero matches: render the empty-filter-state per copy review (`No packages match this filter.`).
- Multiple chips active and one runs out of matches mid-session: chip stays selected; render empty-filter-state until user adjusts.

---

## 3. Status pill (display-only, not interactive)

### Markup

```html
<span class="status-pill" data-status="submitted">Submitted</span>
```

### CSS (Block 2 implements)

```css
.status-pill {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.01em;
}
.status-pill[data-status="open"]         { background: var(--pill-bg-open);         color: var(--pill-text-open); }
.status-pill[data-status="submitted"]    { background: var(--pill-bg-submitted);    color: var(--pill-text-submitted); }
.status-pill[data-status="interviewing"] { background: var(--pill-bg-interviewing); color: var(--pill-text-interviewing); }
.status-pill[data-status="offer"]        { background: var(--pill-bg-offer);        color: var(--pill-text-offer); }
.status-pill[data-status="closed"]       { background: var(--pill-bg-closed);       color: var(--pill-text-closed); }
.status-pill[data-status="rejected"]     { background: var(--pill-bg-rejected);     color: var(--pill-text-rejected); }
```

Color flips happen automatically via CSS variables when `data-theme` changes. No JS required for theme reactivity on pills.

### Label mapping

Always Title Case via the JS prettify helper. Input is the lowercase `status` field from `index.json`.

### Why not a `<button>`

The pill is display-only — clicking a card opens the download, not the pill. The chip set above is the interactive surface for filtering by status.

---

## 4. Top-bar (per ADR-003 D8)

### Markup

```html
<header class="top-bar">
  <div class="top-bar-inner">
    <a href="./" class="brand">
      <img src="assets/logo.svg" alt="" width="28" height="28" />
      <span class="brand-name gradient-text">Ultimate Job Assist</span>
      <span class="version-badge">v0.2.3</span>
    </a>
    <nav class="top-bar-nav">
      <a href="#about" class="top-bar-link">About</a>
      <button class="theme-toggle" data-theme-toggle aria-label="Switch theme">
        <!-- icons per section 1 above -->
      </button>
    </nav>
  </div>
</header>
```

### Sizing per D8

- Total height: 48-64px.
- Inner container: max-width 64rem (1024px) per the calm-density target.
- Padding: 0.75rem (12px) vertical, 1.5rem (24px) horizontal.
- Border-bottom: 1px solid `var(--border)`.

### Sticky behavior - resolved at HITL gate (Session 15)

**Decision:** sticky. Top-bar pinned to viewport top while scrolling. Theme toggle + About link reachable from any scroll position.

CSS for Block 2:

```css
.top-bar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  /* Optional: subtle backdrop-blur for legibility if cards scroll behind */
  /* backdrop-filter: blur(6px); */
  /* If using backdrop-blur, drop the solid bg to a translucent version */
  /* background: color-mix(in srgb, var(--bg) 85%, transparent); */
}
```

Default: solid `--bg` background, no blur. Block 2 may add the optional `backdrop-filter` if the solid bg looks heavy in practice.

The `z-index: 10` keeps the top-bar above any scrolled card content. No other site element competes for the layer.

Reasoning recorded for posterity: future-proofs against application-list growth (past ~30 packages, scrolling becomes the dominant interaction); theme toggle reachable without scroll-back-up; one CSS change at the cost of ~48-64px of vertical real estate during scroll. Trade accepted.


### Markup

```html
<a href="./exports/netflix-data-analyst-2026-04.zip" download class="card" aria-label="Download Netflix Data Analyst package">
  <div class="card-logo" data-initial="N">N</div>
  <div class="card-body">
    <div class="card-header">
      <span class="card-company">Netflix</span>
      <span class="card-role">Data Analyst</span>
    </div>
    <div class="card-meta">
      <span class="card-month">April 2026</span>
      <span class="status-pill" data-status="submitted">Submitted</span>
      <span class="card-size">156 KB</span>
    </div>
  </div>
</a>
```

### Behavior

- Whole card is the download link (`<a download>`). Click anywhere → download.
- Hover: `--bg-card-hover` background, no underline.
- Focus: visible focus ring via `:focus-visible` outline.

### Logo placeholder

Pending favicon delivery (out of scope for Phase 25). For now, a colored circle with the company initial. Background color is a hash of the company name into the status hue palette to give visual variety without an external asset dependency.

### Accessibility

- `aria-label` on the `<a>` makes the entire card readable as a single link by screen readers.
- The card heading hierarchy is flat (no nested `<h3>` inside `<a>`) since the card is itself a link, not a section.

---

## Out of scope for Block 1

- The actual `index.html` skeleton (Block 2).
- The `app.js` renderer (Block 2).
- The `tests/site-renderer.test.html` (Block 3).
- The end-to-end smoke against the Q6 fixture (Block 4).

This doc is the bridge: Block 2 lifts the markup + JS verbatim, names the CSS classes per the patterns above, and uses the variables from `styles.css`.
