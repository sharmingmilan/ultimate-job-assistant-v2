/*
 * Ultimate Job Assist v2 site renderer
 *
 * Renders the Application packages and Config templates sections from
 * exports/index.json and templates/index.json. Plus theme toggle, status
 * filter chip state machine, and empty / loading / error states.
 *
 * No frameworks, no bundler. Single defer-loaded script.
 *
 * Source ADRs: ADR-002 §D4, ADR-003 D1-D8.
 * Source briefs: docs/session-14-brief.md (Phase 25 brief, R1-R6 + Block 2 spec).
 * Source design docs: docs/phase25-palette.md, phase25-component-sketches.md, phase25-copy-review.md.
 */

(function () {
  'use strict';

  // ============================================================
  // Helpers
  // ============================================================

  // Title-Case a single-word company token (R1).
  // Input is canonical lowercase ("netflix" -> "Netflix").
  function prettifyCompany(raw) {
    if (!raw) return '';
    return raw.split(' ').map(function (w) {
      return w.charAt(0).toUpperCase() + w.slice(1);
    }).join(' ');
  }

  // Kebab-to-Title-Case for role slugs (R1).
  // "data-analyst" -> "Data Analyst", "lead-data-analyst" -> "Lead Data Analyst".
  function prettifyRole(raw) {
    if (!raw) return '';
    return raw.split('-').map(function (w) {
      return w.charAt(0).toUpperCase() + w.slice(1);
    }).join(' ');
  }

  // YYYY-MM -> "Month YYYY" (per ADR-003 Appendix A.3).
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  function formatMonth(yyyymm) {
    if (!yyyymm) return '';
    var parts = yyyymm.split('-');
    if (parts.length !== 2) return yyyymm;
    var idx = parseInt(parts[1], 10) - 1;
    if (idx < 0 || idx > 11) return yyyymm;
    return MONTHS[idx] + ' ' + parts[0];
  }

  // Bytes -> "156 KB" / "1.2 MB" / etc.
  function humanBytes(n) {
    if (n == null || isNaN(n)) return '';
    if (n < 1024) return n + ' B';
    if (n < 1024 * 1024) return Math.round(n / 1024) + ' KB';
    var mb = n / (1024 * 1024);
    return (mb < 10 ? mb.toFixed(1) : Math.round(mb)) + ' MB';
  }

  // ============================================================
  // Theme toggle (per ADR-003 D2)
  // ============================================================

  function setupThemeToggle() {
    var btn = document.querySelector('[data-theme-toggle]');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme') || 'dark';
      var next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      try {
        localStorage.setItem('uja-v2-theme', next);
      } catch (e) {
        // Quota / private-mode failure — non-fatal.
        console.warn('Could not persist theme:', e);
      }
    });
  }

  // ============================================================
  // Status filter chip state machine (per ADR-003 D1)
  // ============================================================

  // Active filters live in JS as a Set<status>. Empty Set == "All" active.
  var activeFilters = new Set();

  function setupChipHandlers() {
    var chips = document.querySelectorAll('.filter-chip');
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var status = chip.getAttribute('data-status');
        if (status === 'all') {
          activeFilters.clear();
        } else {
          if (activeFilters.has(status)) {
            activeFilters.delete(status);
          } else {
            activeFilters.add(status);
          }
        }
        updateChipActiveStates();
        renderPackagesList();
      });
    });
  }

  function updateChipActiveStates() {
    var chips = document.querySelectorAll('.filter-chip');
    chips.forEach(function (chip) {
      var status = chip.getAttribute('data-status');
      var active = (status === 'all' && activeFilters.size === 0) || activeFilters.has(status);
      if (active) {
        chip.setAttribute('data-active', '');
        chip.setAttribute('aria-pressed', 'true');
      } else {
        chip.removeAttribute('data-active');
        chip.setAttribute('aria-pressed', 'false');
      }
    });
  }

  // ============================================================
  // Card rendering
  // ============================================================

  // State holders populated by the fetch step
  var packagesData = null; // array of export rows (preserves _sort_index_exports order)
  var templatesData = null; // array of template rows

  function renderPackageCard(row) {
    var company = prettifyCompany(row.company);
    var role = prettifyRole(row.role);
    var initial = (company.charAt(0) || '?').toUpperCase();
    var month = formatMonth(row.application_month);
    var size = humanBytes(row.size_bytes);
    var status = row.status || 'open';
    var label = company + ' ' + role + ' package';

    var card = document.createElement('a');
    card.className = 'card';
    card.href = './exports/' + row.filename;
    card.setAttribute('download', '');
    card.setAttribute('aria-label', 'Download ' + label);
    card.setAttribute('data-status', status);

    card.innerHTML =
      '<div class="card-logo" data-initial="' + initial + '">' + initial + '</div>' +
      '<div class="card-body">' +
        '<div class="card-header">' +
          '<span class="card-company">' + escapeHtml(company) + '</span>' +
          '<span class="card-role">' + escapeHtml(role) + '</span>' +
        '</div>' +
        '<div class="card-meta">' +
          '<span class="card-month">' + escapeHtml(month) + '</span>' +
          '<span class="status-pill" data-status="' + escapeHtml(status) + '">' + escapeHtml(prettifyCompany(status)) + '</span>' +
          '<span class="card-size">' + escapeHtml(size) + '</span>' +
        '</div>' +
      '</div>';
    return card;
  }

  function renderTemplateCard(row) {
    // Templates schema is symmetric to exports but Phase 25 doesn't yet ship any.
    // Reserved for v0.2.4+. If templates data has rows, render them as plain
    // download cards without the status pill.
    var name = row.name || row.filename || 'template';
    var size = humanBytes(row.size_bytes);

    var card = document.createElement('a');
    card.className = 'card card--template';
    card.href = './templates/' + (row.filename || '');
    card.setAttribute('download', '');
    card.setAttribute('aria-label', 'Download ' + name);

    card.innerHTML =
      '<div class="card-logo" data-initial="T">T</div>' +
      '<div class="card-body">' +
        '<div class="card-header">' +
          '<span class="card-company">' + escapeHtml(name) + '</span>' +
        '</div>' +
        '<div class="card-meta">' +
          '<span class="card-size">' + escapeHtml(size) + '</span>' +
        '</div>' +
      '</div>';
    return card;
  }

  function escapeHtml(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // ============================================================
  // Section renderers
  // ============================================================

  function renderPackagesList() {
    var container = document.querySelector('[data-card-list="packages"]');
    if (!container) return;
    container.innerHTML = '';

    if (!packagesData) {
      // Loading state stays; nothing to render yet.
      return;
    }

    if (packagesData.length === 0) {
      container.innerHTML =
        '<div class="empty-state">' +
          '<p>No application packages yet.</p>' +
          '<p class="empty-state-hint">Run the export tool from your project folder to add one.</p>' +
        '</div>';
      return;
    }

    var filtered = packagesData.filter(function (row) {
      return activeFilters.size === 0 || activeFilters.has(row.status);
    });

    if (filtered.length === 0) {
      container.innerHTML = '<div class="empty-state"><p>No packages match this filter.</p></div>';
      return;
    }

    filtered.forEach(function (row) {
      container.appendChild(renderPackageCard(row));
    });
  }

  function renderTemplatesList() {
    var container = document.querySelector('[data-card-list="templates"]');
    if (!container) return;
    container.innerHTML = '';

    if (!templatesData) {
      return;
    }

    if (templatesData.length === 0) {
      container.innerHTML =
        '<div class="empty-state">' +
          '<p>No config templates published yet.</p>' +
        '</div>';
      return;
    }

    templatesData.forEach(function (row) {
      container.appendChild(renderTemplateCard(row));
    });
  }

  // ============================================================
  // Counts
  // ============================================================

  function updateCounts() {
    if (!packagesData) return;
    var total = packagesData.length;
    document.querySelectorAll('[data-count-total]').forEach(function (el) {
      el.textContent = total;
    });
    var byStatus = {};
    packagesData.forEach(function (row) {
      byStatus[row.status] = (byStatus[row.status] || 0) + 1;
    });
    document.querySelectorAll('[data-count-status]').forEach(function (el) {
      var s = el.getAttribute('data-count-status');
      el.textContent = byStatus[s] || 0;
    });
  }

  // ============================================================
  // Fetch + parse
  // ============================================================

  function fetchJson(path) {
    return fetch(path, { cache: 'no-store' }).then(function (resp) {
      if (!resp.ok) {
        throw new Error('HTTP ' + resp.status + ' for ' + path);
      }
      return resp.json();
    });
  }

  function showPackagesError() {
    var container = document.querySelector('[data-card-list="packages"]');
    if (!container) return;
    container.innerHTML =
      '<div class="empty-state empty-state--error">' +
        '<p>Couldn\'t load packages. Reload the page to try again.</p>' +
        '<p class="empty-state-hint">If the problem persists, the export tool may need to run in your project folder.</p>' +
      '</div>';
  }

  function showTemplatesError() {
    var container = document.querySelector('[data-card-list="templates"]');
    if (!container) return;
    container.innerHTML =
      '<div class="empty-state empty-state--error">' +
        '<p>Couldn\'t load templates. Reload the page to try again.</p>' +
      '</div>';
  }

  function loadPackages() {
    fetchJson('./exports/index.json').then(function (data) {
      // Validate shape per Phase 24's index.json schema v1.
      if (!data || data.schema_version !== 1 || !Array.isArray(data.exports)) {
        console.warn('exports/index.json: unexpected shape; treating as empty');
        packagesData = [];
      } else {
        packagesData = data.exports;
      }
      updateCounts();
      updateChipActiveStates();
      renderPackagesList();
    }).catch(function (err) {
      console.warn('exports fetch failed:', err);
      // Treat missing file as empty (R3) rather than error, since the very
      // first deploy may not have any exports yet.
      if (String(err.message || '').indexOf('HTTP 404') >= 0) {
        packagesData = [];
        updateCounts();
        updateChipActiveStates();
        renderPackagesList();
      } else {
        showPackagesError();
      }
    });
  }

  function loadTemplates() {
    fetchJson('./templates/index.json').then(function (data) {
      if (!data || data.schema_version !== 1 || !Array.isArray(data.templates)) {
        console.warn('templates/index.json: unexpected shape; treating as empty');
        templatesData = [];
      } else {
        templatesData = data.templates;
      }
      renderTemplatesList();
    }).catch(function (err) {
      console.warn('templates fetch failed:', err);
      if (String(err.message || '').indexOf('HTTP 404') >= 0) {
        templatesData = [];
        renderTemplatesList();
      } else {
        showTemplatesError();
      }
    });
  }

  // ============================================================
  // Init
  // ============================================================

  function init() {
    setupThemeToggle();
    setupChipHandlers();
    updateChipActiveStates();
    loadPackages();
    loadTemplates();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose a small API surface for the Block 3 site-renderer test (see
  // website/v2/tests/site-renderer.test.html).
  window.__ujaSite = {
    prettifyCompany: prettifyCompany,
    prettifyRole: prettifyRole,
    formatMonth: formatMonth,
    humanBytes: humanBytes,
    setData: function (kind, rows) {
      if (kind === 'packages') {
        packagesData = rows;
        updateCounts();
        updateChipActiveStates();
        renderPackagesList();
      } else if (kind === 'templates') {
        templatesData = rows;
        renderTemplatesList();
      }
    },
    setFilter: function (statuses) {
      activeFilters = new Set(statuses || []);
      updateChipActiveStates();
      renderPackagesList();
    },
  };

})();
