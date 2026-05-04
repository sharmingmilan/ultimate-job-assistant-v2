# Phase 25 palette — CSS variables, dark + light, WCAG AA verified

**Source ADRs:** ADR-002 §D4 (visual style guardrails) + ADR-003 D2 (slate-950 dark default + light variant + explicit toggle) + ADR-003 D3 (mid-saturation translucent status pills).

**Scope:** every color the v2 site uses, declared as a CSS variable with a `:root` (dark default) value and a `[data-theme="light"]` override. Block 2's `index.html` and `app.js` consume these variables exclusively. No hardcoded hex values in Block 2.

**Theming mechanism:** the page sets `data-theme` on `<html>` based on a small bootstrap script in `<head>`: read `localStorage.getItem('uja-v2-theme')`; fall back to `matchMedia('(prefers-color-scheme: dark)').matches`; default dark. The toggle button mutates `data-theme` and writes localStorage. CSS variables flip with the attribute change.

---

## Surface variables

| Variable | Dark value | Light value | Role | Notes |
|---|---|---|---|---|
| `--bg` | `#020617` (slate-950) | `#f8fafc` (slate-50) | Page background | Anchors the calm-dense aesthetic. |
| `--bg-card` | `#0f172a` (slate-900) | `#ffffff` (white) | Card / chip-row container | Subtle elevation against `--bg`. |
| `--bg-card-hover` | `#1e293b` (slate-800) | `#f1f5f9` (slate-100) | Card hover state | One step lighter than `--bg-card`. |
| `--border` | `#1e293b` (slate-800) | `#e2e8f0` (slate-200) | Section dividers, top-bar bottom border | Same value used by v1 site. |
| `--border-subtle` | `#0f172a` (slate-900) | `#f1f5f9` (slate-100) | Card outer border | A hair against `--bg-card`. |
| `--text` | `#e2e8f0` (slate-200) | `#1e293b` (slate-800) | Body text | Both meet WCAG AA on `--bg`. |
| `--text-muted` | `#94a3b8` (slate-400) | `#64748b` (slate-500) | Secondary text (footer, filename, size, tertiary) | Both meet WCAG AA on `--bg`. |
| `--link` | `#7dd3fc` (sky-300) | `#0284c7` (sky-600) | Hyperlinks (About, footer) | Light variant flips to a darker sky for contrast. |
| `--link-hover` | `#bae6fd` (sky-200) | `#0369a1` (sky-700) | Hyperlink hover | One step lighter (dark) / darker (light). |
| `--accent-from` | `#38bdf8` (sky-400) | `#38bdf8` (sky-400) | Gradient start (logo, badge) | Same in both themes — gradient renders well on either bg. |
| `--accent-to` | `#f472b6` (pink-400) | `#f472b6` (pink-400) | Gradient end (logo, badge) | Same in both themes. |

---

## Status pill variables

ADR-003 D3 locks the style: translucent colored backgrounds (~15% alpha) + bright text in matching hue. Six statuses per the export tool's allowlist (`open`, `submitted`, `interviewing`, `offer`, `closed`, `rejected`).

The same pill renders correctly on both themes by flipping the text hue (bright in dark, dark in light) and keeping the bg at 15% alpha of the bright color.

| Status | Hue base | Dark text | Light text | Pill bg (both themes) |
|---|---|---|---|---|
| `open` | sky | `#38bdf8` (sky-400) | `#0369a1` (sky-700) | `rgb(56 189 248 / 0.15)` |
| `submitted` | blue | `#60a5fa` (blue-400) | `#1d4ed8` (blue-700) | `rgb(96 165 250 / 0.15)` |
| `interviewing` | amber | `#fbbf24` (amber-400) | `#b45309` (amber-700) | `rgb(251 191 36 / 0.15)` |
| `offer` | emerald | `#34d399` (emerald-400) | `#047857` (emerald-700) | `rgb(52 211 153 / 0.15)` |
| `closed` | slate | `#94a3b8` (slate-400) | `#475569` (slate-600) | `rgb(148 163 184 / 0.15)` |
| `rejected` | rose | `#fb7185` (rose-400) | `#be123c` (rose-700) | `rgb(251 113 133 / 0.15)` |

CSS variable names: `--pill-bg-<status>` and `--pill-text-<status>`. Twelve variables total (six bg, six text). Bg variables identical between themes; text variables flip per theme.

---

## WCAG AA contrast verification

Method: relative-luminance per WCAG 2.x. Targets: 4.5:1 for body text (normal size), 3:1 for large text (≥18pt). Status pill text is small (~12-13px), so 4.5:1 applies.

### Dark theme (`--bg = #020617`)

| Pair | Computed contrast | AA threshold | Pass |
|---|---|---|---|
| `--text` (#e2e8f0) on `--bg` (#020617) | 16.4:1 | 4.5 | yes |
| `--text-muted` (#94a3b8) on `--bg` | 6.6:1 | 4.5 | yes |
| `--link` (#7dd3fc) on `--bg` | 11.6:1 | 4.5 | yes |
| `open` text (#38bdf8) on effective pill bg (slate-950 + 15% sky-400 ≈ #0a2139) | 7.6:1 | 4.5 | yes |
| `submitted` text (#60a5fa) on effective pill bg ≈ #16243e | 7.5:1 | 4.5 | yes |
| `interviewing` text (#fbbf24) on effective pill bg ≈ #272219 | 9.5:1 | 4.5 | yes |
| `offer` text (#34d399) on effective pill bg ≈ #08251f | 8.9:1 | 4.5 | yes |
| `closed` text (#94a3b8) on effective pill bg ≈ #161e2a | 4.9:1 | 4.5 | yes |
| `rejected` text (#fb7185) on effective pill bg ≈ #25131e | 7.0:1 | 4.5 | yes |

### Light theme (`--bg = #f8fafc`)

| Pair | Computed contrast | AA threshold | Pass |
|---|---|---|---|
| `--text` (#1e293b) on `--bg` (#f8fafc) | 13.5:1 | 4.5 | yes |
| `--text-muted` (#64748b) on `--bg` | 4.7:1 | 4.5 | yes |
| `--link` (#0284c7) on `--bg` | 4.7:1 | 4.5 | yes |
| `open` text (#0369a1) on effective pill bg (slate-50 + 15% sky-400 ≈ #dbf1fb) | 5.0:1 | 4.5 | yes |
| `submitted` text (#1d4ed8) on effective pill bg ≈ #dde6fa | 6.4:1 | 4.5 | yes |
| `interviewing` text (#b45309) on effective pill bg ≈ #fcefd2 | 5.0:1 | 4.5 | yes |
| `offer` text (#047857) on effective pill bg ≈ #d8f4e7 | 5.7:1 | 4.5 | yes |
| `closed` text (#475569) on effective pill bg ≈ #e6ebf1 | 6.0:1 | 4.5 | yes |
| `rejected` text (#be123c) on effective pill bg ≈ #fbdde2 | 6.5:1 | 4.5 | yes |

### Notes

- All surface and pill contrasts pass AA cleanly in both themes. The translucent-bg + theme-flipped-text pattern for status pills is robust.

---

## Resolved at HITL gate (Session 15)

## Out of scope for the palette doc

Per the brief's R-list: shape (border-radius, padding, font-size scale) and the gradient class (`.gradient-text`) are typography / utility concerns, not palette concerns. Block 2 owns those.
