#!/usr/bin/env bash
# publish_to_github.sh — One-shot publishing for Ultimate Job Assistant v0.1.0
#
# What this does:
#   1. Verifies prerequisites (git, gh CLI). Offers to install gh via brew if missing.
#   2. Authenticates to GitHub (`gh auth login`). Skipped if already logged in.
#   3. Creates the private mirror repo:  ultimate-job-assistant     (private)
#   4. Pushes the private repo with full git history + tags.
#   5. Creates a sibling folder ../ultimate-job-assistant-public/ and inits it.
#   6. Creates the public companion repo: ultimate-job-assistant-public (public)
#   7. Runs scripts/sync_to_public.py to copy the allowlisted, PII-scrubbed files.
#   8. Commits + pushes the public companion.
#   9. Enables GitHub Pages on the public repo (Source: GitHub Actions).
#  10. Prints both repo URLs and the predicted Pages URL.
#
# Run from the private repo root:
#     cd "Ultimate Job Assistant"
#     bash scripts/publish_to_github.sh
#
# Idempotent: if a step is already done, it's skipped.
# If something fails, the script stops and tells you exactly what to fix.

set -euo pipefail

# ─── Configuration ─────────────────────────────────────────────────────────
PRIVATE_REPO_NAME="ultimate-job-assistant"
PUBLIC_REPO_NAME="ultimate-job-assistant-public"

# Colors
BOLD=$(tput bold 2>/dev/null || echo "")
GREEN=$(tput setaf 2 2>/dev/null || echo "")
YELLOW=$(tput setaf 3 2>/dev/null || echo "")
RED=$(tput setaf 1 2>/dev/null || echo "")
RESET=$(tput sgr0 2>/dev/null || echo "")

ok()    { echo "${GREEN}✓${RESET} $1"; }
info()  { echo "${BOLD}▸${RESET} $1"; }
warn()  { echo "${YELLOW}⚠${RESET} $1"; }
fail()  { echo "${RED}✗${RESET} $1"; exit 1; }

# ─── Step 0: sanity ────────────────────────────────────────────────────────
info "Step 0: Sanity check"
if [ ! -f "SPEC.md" ] || [ ! -d "skills/interview-prep" ]; then
  fail "Run this from the Ultimate Job Assistant project root (the folder containing SPEC.md)."
fi
PROJECT_ROOT="$(pwd)"
PARENT_DIR="$(dirname "$PROJECT_ROOT")"
PUBLIC_DIR="$PARENT_DIR/$PUBLIC_REPO_NAME"
ok "Project root: $PROJECT_ROOT"
ok "Public companion will be: $PUBLIC_DIR"
echo ""

# ─── Step 1: prerequisites ─────────────────────────────────────────────────
info "Step 1: Verify prerequisites"
command -v git >/dev/null || fail "git is not installed. Install Xcode Command Line Tools: xcode-select --install"
ok "git: $(git --version | awk '{print $3}')"

if ! command -v gh >/dev/null; then
  warn "GitHub CLI (gh) is not installed."
  if command -v brew >/dev/null; then
    read -r -p "  Install gh via Homebrew now? [y/N] " yn
    if [[ "$yn" =~ ^[Yy]$ ]]; then
      brew install gh
    else
      fail "gh is required. Install it from https://cli.github.com or run: brew install gh"
    fi
  else
    fail "Neither gh nor brew is installed. Install gh from https://cli.github.com first."
  fi
fi
ok "gh:  $(gh --version | head -1 | awk '{print $3}')"

command -v python3 >/dev/null || fail "python3 not found. Install Python 3 (it ships with macOS, try /usr/bin/python3 or via brew)."
ok "python3: $(python3 --version | awk '{print $2}')"
echo ""

# ─── Step 2: GitHub auth ───────────────────────────────────────────────────
info "Step 2: Authenticate with GitHub"
if gh auth status >/dev/null 2>&1; then
  GH_USER=$(gh api user --jq .login 2>/dev/null || echo "unknown")
  ok "Already authenticated as: $GH_USER"
else
  echo "  Launching gh auth login. Choose: GitHub.com → HTTPS → Y to git → Login with a web browser."
  gh auth login
  GH_USER=$(gh api user --jq .login)
  ok "Authenticated as: $GH_USER"
fi
echo ""

# ─── Step 3: create + push private repo ────────────────────────────────────
info "Step 3: Create + push the private mirror repo"
PRIVATE_FULL="$GH_USER/$PRIVATE_REPO_NAME"
if gh repo view "$PRIVATE_FULL" >/dev/null 2>&1; then
  warn "Repo $PRIVATE_FULL already exists. Skipping create."
else
  gh repo create "$PRIVATE_FULL" --private --description "Personal job-application toolkit (private). Companion: $GH_USER/$PUBLIC_REPO_NAME" --source=. --remote=origin --push=false
  ok "Created $PRIVATE_FULL (private)"
fi

# Make sure 'origin' is set
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "https://github.com/$PRIVATE_FULL.git"
fi
echo "  Pushing private repo (all branches + tags)..."
git push -u origin main 2>&1 | tail -5
git push origin --tags 2>&1 | tail -3
ok "Pushed: https://github.com/$PRIVATE_FULL"
echo ""

# ─── Step 4: build the public companion folder ─────────────────────────────
info "Step 4: Set up sibling public-companion folder"
if [ -d "$PUBLIC_DIR" ]; then
  if [ -d "$PUBLIC_DIR/.git" ]; then
    ok "$PUBLIC_DIR exists with .git/ — will reuse it."
  else
    fail "$PUBLIC_DIR exists but isn't a git repo. Move it aside or delete it before re-running."
  fi
else
  mkdir -p "$PUBLIC_DIR"
  cd "$PUBLIC_DIR"
  git init -b main >/dev/null
  git config user.email "$(cd "$PROJECT_ROOT" && git config user.email)"
  git config user.name  "$(cd "$PROJECT_ROOT" && git config user.name)"
  cat > README.md <<'README'
# Ultimate Job Assistant (public companion)

The public, sanitized companion to the personal `ultimate-job-assistant` project.

See [ONBOARDING.md](./ONBOARDING.md) to set up your own personalized version.
The website lives at the GitHub Pages URL listed at the bottom of this file (after first deploy).
README
  cat > .gitignore <<'GITIGNORE'
.DS_Store
node_modules/
*.log
GITIGNORE
  git add -A
  git commit -m "Initial commit (placeholder before first sync)" >/dev/null
  ok "Initialized $PUBLIC_DIR"
fi
cd "$PROJECT_ROOT"
echo ""

# ─── Step 5: create public companion on GitHub ─────────────────────────────
info "Step 5: Create the public companion repo on GitHub"
PUBLIC_FULL="$GH_USER/$PUBLIC_REPO_NAME"
if gh repo view "$PUBLIC_FULL" >/dev/null 2>&1; then
  warn "Repo $PUBLIC_FULL already exists. Skipping create."
else
  gh repo create "$PUBLIC_FULL" --public --description "Ultimate Job Assistant — research-driven, agentic job application toolkit. Companion to the personal project."
  ok "Created $PUBLIC_FULL (public)"
fi
cd "$PUBLIC_DIR"
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "https://github.com/$PUBLIC_FULL.git"
fi
cd "$PROJECT_ROOT"
echo ""

# ─── Step 6: sync allowlisted files into the public companion ──────────────
info "Step 6: Run sync_to_public.py (PII-gated allowlist copy)"
python3 scripts/sync_to_public.py --to "$PUBLIC_DIR"
echo ""

# ─── Step 7: commit + push public companion ───────────────────────────────
info "Step 7: Commit + push the public companion"
cd "$PUBLIC_DIR"
git add -A
if git diff --cached --quiet; then
  warn "Nothing to commit on the public companion."
else
  git commit -m "v0.1.0 — interview-prep skill, PWA template, website, docs

Synced from the private ultimate-job-assistant repo via scripts/sync_to_public.py.
PII scanner (STRICT mode) ran clean before this commit was created.

See ONBOARDING.md to set up your own version."
  ok "Committed."
fi
git push -u origin main 2>&1 | tail -5
ok "Pushed: https://github.com/$PUBLIC_FULL"
cd "$PROJECT_ROOT"
echo ""

# ─── Step 8: enable GitHub Pages ──────────────────────────────────────────
info "Step 8: Enable GitHub Pages on the public repo"
PAGES_RESPONSE=$(gh api -X POST "/repos/$PUBLIC_FULL/pages" \
  -f "build_type=workflow" 2>/dev/null || echo "")
if echo "$PAGES_RESPONSE" | grep -q '"html_url"'; then
  PAGES_URL=$(echo "$PAGES_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('html_url', ''))")
  ok "Pages enabled: $PAGES_URL"
else
  # Pages may already be enabled. Try GET.
  PAGES_URL=$(gh api "/repos/$PUBLIC_FULL/pages" --jq .html_url 2>/dev/null || echo "")
  if [ -n "$PAGES_URL" ]; then
    ok "Pages already configured: $PAGES_URL"
  else
    warn "Could not enable Pages automatically. Enable it manually:"
    warn "  https://github.com/$PUBLIC_FULL/settings/pages"
    warn "  Set Source: GitHub Actions"
    PAGES_URL="https://$GH_USER.github.io/$PUBLIC_REPO_NAME/"
  fi
fi
echo ""

# ─── Final report ──────────────────────────────────────────────────────────
echo "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo "${BOLD}  PUBLISH COMPLETE${RESET}"
echo "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo ""
echo "  Private mirror:  ${BOLD}https://github.com/$PRIVATE_FULL${RESET}"
echo "  Public repo:     ${BOLD}https://github.com/$PUBLIC_FULL${RESET}"
echo "  Public website:  ${BOLD}$PAGES_URL${RESET}"
echo ""
echo "  Pages takes ~1-2 minutes to build the first time. Watch the deploy at:"
echo "    https://github.com/$PUBLIC_FULL/actions"
echo ""
echo "  To re-sync (after future changes in the private repo):"
echo "    cd \"$PROJECT_ROOT\""
echo "    python3 scripts/sync_to_public.py --to \"$PUBLIC_DIR\""
echo "    cd \"$PUBLIC_DIR\" && git add -A && git commit -m '...' && git push"
echo ""
