#!/usr/bin/env python3
"""
scan_pii.py — Scan files for PII patterns before publishing to the public repo.

This script is used in two places:
  1. CI (warn-only) on every push to the private repo.
  2. The public-repo sync script (Phase 7) where it BLOCKS the sync if any
     pattern is found in files about to be copied to the public companion.

Patterns are conservative — false positives are acceptable; false negatives are not.

Usage:
    python3 scripts/scan_pii.py [--paths PATH1 PATH2 ...] [--strict] [--exclude PATTERN]

Exit codes:
    0  no PII patterns matched
    1  PII patterns matched (only in --strict mode; otherwise prints and exits 0)

The default scan paths are the union of skill source code, references, and project
docs that could plausibly be sanitized for public sharing. The script EXPLICITLY
SKIPS personal-data folders (resumes/, scores/, etc.) since those are git-ignored
and shouldn't be in any commit anyway — if a future bug puts them there, scan_pii
will catch the exposure on the contents.
"""

import argparse
import re
import sys
from pathlib import Path

# Patterns to detect. Tuned for Milan's profile but conservative.
PATTERNS = {
    "milan_name": re.compile(r"\bMilan\b|\bMilan Sharma\b|\bSharma\b", re.IGNORECASE),
    "milan_email": re.compile(r"msharm406|msharm@|msharm\.|msharm/"),
    "milan_phone": re.compile(r"\(?661\)?\s*\d{3}\s*-?\s*\d{4}|661-873-5077|6618735077"),
    "milan_address": re.compile(r"Culver City"),
    "milan_linkedin": re.compile(r"linkedin\.com/in/msharm"),
    "real_employer_pinterest": re.compile(r"\bPinterest\b"),
    "real_employer_apple_data_analyst": re.compile(r"\bApple\b.*\b(Data Analyst|Production Finance)\b", re.IGNORECASE),
    "real_employer_wells": re.compile(r"\bWells Fargo\b"),
    "real_employer_nike": re.compile(r"\bNike\b"),
}

# Files where these patterns are EXPECTED and benign. Skip them.
EXEMPT_FILE_PATTERNS = [
    re.compile(r"^memory\.md$"),               # private only by convention; .gitignored if going public
    re.compile(r"\.gitignore$"),
    re.compile(r"^scripts/scan_pii\.py$"),     # this file (literal patterns are matches against itself)
    re.compile(r"references/examples/.*-waymo\.md$"),  # generic Waymo example bundle
]

# Paths to never recurse into.
SKIP_DIRS = {".git", "node_modules", ".github/cache", "__pycache__", ".cache"}

# Default scan paths if --paths is not given.
DEFAULT_PATHS = ["skills", "references", ".github", "scripts", "ONBOARDING.md", "README.md", "SPEC.md", "ROADMAP.md", "DESIGN_DOC.md", "CLAUDE.md"]


def is_exempt(path: Path, root: Path) -> bool:
    rel = str(path.relative_to(root))
    return any(p.search(rel) for p in EXEMPT_FILE_PATTERNS)


def scan_file(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return {}
    found = {}
    for name, pat in PATTERNS.items():
        matches = pat.findall(text)
        if matches:
            # Take only first 3 matches to keep output bounded
            found[name] = list(set(matches))[:3]
    return found


def walk_paths(roots, repo_root):
    for r in roots:
        rp = Path(r)
        if not rp.is_absolute():
            rp = repo_root / rp
        if not rp.exists():
            continue
        if rp.is_file():
            yield rp
            continue
        for p in rp.rglob("*"):
            if p.is_dir():
                if p.name in SKIP_DIRS:
                    # rglob doesn't accept skip-dirs natively; just continue
                    continue
                continue
            # skip files inside skip dirs anywhere in their parents
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if p.suffix in {".png", ".jpg", ".jpeg", ".pdf", ".docx", ".xlsx", ".ico", ".woff", ".woff2"}:
                continue
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", nargs="*", default=None,
                    help="Files/dirs to scan. Defaults to skill code + project docs.")
    ap.add_argument("--strict", action="store_true",
                    help="Exit 1 if any pattern matches. Otherwise warn and exit 0.")
    ap.add_argument("--repo-root", default=".",
                    help="Repository root. Defaults to current directory.")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    paths = args.paths if args.paths else DEFAULT_PATHS

    print(f"PII scanner — repo root: {repo_root}")
    print(f"  scanning: {paths}")
    print(f"  mode: {'STRICT (will exit 1 on hits)' if args.strict else 'WARN (will exit 0 even on hits)'}")
    print()

    hits = {}
    file_count = 0
    for f in walk_paths(paths, repo_root):
        if is_exempt(f, repo_root):
            continue
        file_count += 1
        found = scan_file(f)
        if found:
            hits[str(f.relative_to(repo_root))] = found

    print(f"Scanned {file_count} files.")
    print()

    if hits:
        print(f"⚠ Patterns found in {len(hits)} file(s):")
        for path, patterns in hits.items():
            print(f"  {path}")
            for name, samples in patterns.items():
                print(f"    [{name}] samples: {samples}")
        print()
        if args.strict:
            print("STRICT mode — failing.")
            sys.exit(1)
        else:
            print("WARN mode — proceeding. Review before any public sync.")
            sys.exit(0)
    else:
        print("✅ No PII patterns matched.")
        sys.exit(0)


if __name__ == "__main__":
    main()
