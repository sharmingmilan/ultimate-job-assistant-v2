#!/usr/bin/env bash
# install-hooks.sh — copy tracked git hooks into .git/hooks/
#
# Run once after cloning the canonical repo:
#
#   bash scripts/install-hooks.sh
#
# Idempotent: re-running overwrites existing hooks with the latest tracked
# version. Safe to re-run after `git pull` if a hook source changed.
#
# Why this exists:
# .git/hooks/ is a per-clone, untracked directory. The hooks we want everyone
# to share live as tracked files in references/git-hooks/. This script is the
# bridge.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="${REPO_ROOT}/references/git-hooks"
DST_DIR="${REPO_ROOT}/.git/hooks"

if [[ ! -d "${REPO_ROOT}/.git" ]]; then
  echo "ERROR: ${REPO_ROOT} is not a git repo. Run this from the canonical clone." >&2
  exit 1
fi

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "ERROR: hook source directory not found: ${SRC_DIR}" >&2
  exit 1
fi

mkdir -p "${DST_DIR}"

installed=0
for src in "${SRC_DIR}"/*; do
  [[ -f "${src}" ]] || continue
  name="$(basename "${src}")"
  dst="${DST_DIR}/${name}"
  cp "${src}" "${dst}"
  chmod +x "${dst}"
  echo "  installed: ${name} -> .git/hooks/${name}"
  installed=$((installed + 1))
done

echo ""
echo "Done. ${installed} hook(s) installed."
echo "Verify: cat .git/hooks/pre-push (top of file should match references/git-hooks/pre-push)."
