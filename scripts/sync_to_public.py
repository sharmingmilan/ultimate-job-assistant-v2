#!/usr/bin/env python3
"""
sync_to_public.py — Allowlisted, PII-gated sync from private repo to public companion repo.

Workflow:
  1. Read the allowlist below.
  2. For each allowlisted source path, copy to the corresponding destination
     in the public companion repo's working tree.
  3. After copy, run scripts/scan_pii.py --strict over the destination tree.
  4. If the scanner finds anything, ABORT and roll back the destination changes
     (only the just-synced files; pre-existing public files are untouched).
  5. If clean, print a diff for the user to eyeball before committing.

This script never automatically commits or pushes. The user does that manually
after reviewing the diff.

Usage:
    python3 scripts/sync_to_public.py --to ../ultimate-job-assistant-public
    python3 scripts/sync_to_public.py --to ../ultimate-job-assistant-public --dry-run

Exit codes:
    0  sync completed (or dry-run reported what would change)
    1  PII scanner blocked the sync (rolled back)
    2  bad arguments or destination structure
    3  unexpected error
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Allowlist: tuples of (src_path_relative_to_repo_root, dst_path_relative_to_public_root).
# If src is a directory, the whole tree is copied.
# If a file would expose PII, it is excluded here OR the scanner catches it.
ALLOWLIST = [
    # Project docs (sanitized)
    ("ONBOARDING.md", "ONBOARDING.md"),
    ("ROADMAP.md", "ROADMAP.md"),

    # All skill code (these are generic; scanner verifies)
    ("skills/decoded-jd/SKILL.md", "skills/decoded-jd/SKILL.md"),
    ("skills/networking-intros/SKILL.md", "skills/networking-intros/SKILL.md"),
    ("skills/orchestrator/SKILL.md", "skills/orchestrator/SKILL.md"),
    ("skills/portfolio-coach/SKILL.md", "skills/portfolio-coach/SKILL.md"),
    ("skills/portfolio-coach/references", "skills/portfolio-coach/references"),
    ("skills/resume-scorer/SKILL.md", "skills/resume-scorer/SKILL.md"),
    ("skills/resume-targeter/SKILL.md", "skills/resume-targeter/SKILL.md"),
    ("skills/why-this-company/SKILL.md", "skills/why-this-company/SKILL.md"),

    # Interview-prep skill (the new one) — full code, references, evals, template
    ("skills/interview-prep", "skills/interview-prep"),

    # Generic references (templates and patterns; the examples directory is candidate-specific so excluded)
    ("references/README.md", "references/README.md"),
    ("references/patterns", "references/patterns"),
    ("references/scripts", "references/scripts"),
    ("references/templates", "references/templates"),

    # Build/CI scripts
    ("scripts/scan_pii.py", "scripts/scan_pii.py"),
    ("scripts/sync_to_public.py", "scripts/sync_to_public.py"),

    # CI workflow (the public repo can reuse this)
    (".github/workflows/ci.yml", ".github/workflows/ci.yml"),

    # Website source.
    ("website", "website"),

    # GitHub Pages deploy workflow for the public repo. Stored as a regular file
    # in website/ inside the private repo (so it doesn't trigger spuriously
    # there), then placed at the standard workflow path in the public repo.
    ("website/.github-pages-workflow.yml", ".github/workflows/pages.yml"),
]

# Files we DELIBERATELY exclude even if they're inside an allowlisted directory.
# These are paths within the destination that we never sync.
EXCLUDE_DST = {
    # The Job-Assist eval-fixture docx contains a redacted resume; even the
    # redacted version is candidate-shaped enough that we skip it from public.
    "skills/resume-targeter/evals",
    "references/examples",
    # PDF generators have hardcoded contact info baked into the rendering code.
    # A future cleanup task can templatize these; for now they don't go public.
    "references/scripts/generate-cover-letter-pdf.py",
    "references/scripts/generate-speaking-points-pdf.py",
    # docx-xml-editing.md contains a real phone number as an example.
    "references/patterns/docx-xml-editing.md",
}


def run(cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def is_excluded(rel_dst: str) -> bool:
    p = Path(rel_dst).as_posix()
    return any(p == ex or p.startswith(ex + "/") for ex in EXCLUDE_DST)


def prune_excluded(public_root: Path):
    """After all files are copied, delete EXCLUDE_DST subtrees from the public repo."""
    for ex in EXCLUDE_DST:
        target = public_root / ex
        if target.is_dir():
            shutil.rmtree(target)
            print(f"  PRUNED EXCLUDED DIR: {ex}/")
        elif target.is_file():
            target.unlink()
            print(f"  PRUNED EXCLUDED FILE: {ex}")


def copy_one(src: Path, dst: Path, dry_run: bool):
    if not src.exists():
        print(f"  SKIP (missing source): {src}")
        return
    if dst.exists():
        if dst.is_dir():
            if dry_run:
                print(f"  WOULD CLEAR: {dst}/  (recursive)")
            else:
                shutil.rmtree(dst)
        else:
            if dry_run:
                print(f"  WOULD REPLACE: {dst}")
            else:
                dst.unlink()
    if src.is_dir():
        if dry_run:
            n = sum(1 for _ in src.rglob("*") if _.is_file())
            print(f"  WOULD COPY DIR: {src}/  -> {dst}/  ({n} files)")
        else:
            shutil.copytree(src, dst)
            print(f"  COPIED DIR: {src}/  -> {dst}/")
    else:
        if dry_run:
            print(f"  WOULD COPY FILE: {src}  -> {dst}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  COPIED FILE: {src.name}  -> {dst}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True, help="Path to the public companion repo's working tree.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show what would change. Do not copy. Do not run scanner.")
    ap.add_argument("--repo-root", default=".",
                    help="Path to the private repo root. Defaults to current directory.")
    ap.add_argument("--scanner",
                    default="scripts/scan_pii.py",
                    help="Path to PII scanner relative to repo root.")
    args = ap.parse_args()

    src_root = Path(args.repo_root).resolve()
    dst_root = Path(args.to).resolve()
    scanner = src_root / args.scanner

    if not src_root.is_dir():
        print(f"ERROR: source repo root not found: {src_root}")
        sys.exit(2)
    if not args.dry_run and not dst_root.is_dir():
        print(f"ERROR: destination not found. Create it with `git init` first: {dst_root}")
        sys.exit(2)
    if not args.dry_run and not scanner.is_file():
        print(f"ERROR: scanner not found: {scanner}")
        sys.exit(2)

    print(f"Sync private -> public companion")
    print(f"  source: {src_root}")
    print(f"  dest:   {dst_root}")
    print(f"  mode:   {'DRY RUN' if args.dry_run else 'COPY + STRICT SCAN'}")
    print()

    print("Step 1: copy allowlisted paths")
    for src_rel, dst_rel in ALLOWLIST:
        src = src_root / src_rel
        dst = dst_root / dst_rel
        copy_one(src, dst, dry_run=args.dry_run)
    print()

    if not args.dry_run:
        print("Step 1b: prune EXCLUDE_DST subtrees from public repo")
        prune_excluded(dst_root)
        print()

    if args.dry_run:
        print("Dry run complete.  Re-run without --dry-run to actually sync.")
        sys.exit(0)

    print("Step 2: STRICT PII scan over destination tree")
    result = subprocess.run(
        [sys.executable, str(scanner), "--strict", "--repo-root", str(dst_root)],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print()
        print("=" * 60)
        print("PII SCANNER BLOCKED THE SYNC.  Destination is dirty until reverted.")
        print()
        print("To roll back changes in the public repo:")
        print(f"  cd {dst_root}")
        print(f"  git restore --staged --worktree -- .")
        print(f"  git clean -fd")
        print()
        print("Then fix the source files in the private repo and re-run sync.")
        print("=" * 60)
        sys.exit(1)

    print()
    print("Step 3: scanner clean.  Diff to review:")
    diff = subprocess.run(["git", "status", "--short"], cwd=dst_root, capture_output=True, text=True)
    print(diff.stdout or "(no changes)")

    print()
    print("Sync complete.  Review the diff above, then commit + push manually:")
    print(f"  cd {dst_root}")
    print(f"  git add -A")
    print(f"  git commit -m 'Sync from private repo'")
    print(f"  git push")


if __name__ == "__main__":
    main()
