#!/usr/bin/env python3
"""sync_to_public_v2.py — sync v2 canonical to v2 deploy-source.

Mirrors scripts/sync_to_public.py for the v0.2.0 pair:
  src: ultimate-job-assistant-v2 (canonical, private)
  dst: ultimate-job-assistant-v2-public (deploy-source, private)

Usage:
    python scripts/sync_to_public_v2.py [--dry-run] [--no-zip]

Requires:
    - PUBLIC_REPO_TOKEN_V2 in env (PAT B from V2_SETUP.md), OR
    - the dst repo is already cloned at ../ultimate-job-assistant-v2-public

Re-uses scripts/scan_pii.py for the PII gate.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # v2 canonical root
DST_REPO_NAME = "ultimate-job-assistant-v2-public"
DST_DEFAULT = ROOT.parent / DST_REPO_NAME

# Files copied from src to dst. (src_relative, dst_relative).
# Trailing-slash semantics: implicit — directories are recursed.
ALLOWLIST = [
    # Project docs (sanitized)
    ("ONBOARDING.md", "ONBOARDING.md"),  # if present
    ("V2_SETUP.md", "V2_SETUP.md"),

    # All skill code (generic; PII scanner verifies)
    ("skills/decoded-jd/SKILL.md", "skills/decoded-jd/SKILL.md"),
    ("skills/networking-intros/SKILL.md", "skills/networking-intros/SKILL.md"),
    ("skills/orchestrator/SKILL.md", "skills/orchestrator/SKILL.md"),
    ("skills/portfolio-coach/SKILL.md", "skills/portfolio-coach/SKILL.md"),
    ("skills/portfolio-coach/references", "skills/portfolio-coach/references"),
    ("skills/resume-scorer/SKILL.md", "skills/resume-scorer/SKILL.md"),
    ("skills/resume-targeter/SKILL.md", "skills/resume-targeter/SKILL.md"),
    ("skills/why-this-company/SKILL.md", "skills/why-this-company/SKILL.md"),
    ("skills/interview-prep", "skills/interview-prep"),

    # Generic references
    ("references/README.md", "references/README.md"),
    ("references/patterns", "references/patterns"),
    ("references/scripts", "references/scripts"),
    ("references/templates", "references/templates"),
    ("references/zip-bundle", "references/zip-bundle"),
    ("references/git-hooks", "references/git-hooks"),
    # Phase 23: canonical Cowork MCP-config template emitted by start-uja-mcp.sh.
    ("references/cowork-mcp-config-snippet.json", "references/cowork-mcp-config-snippet.json"),

    # NEW for v2: the local web host backend (host/uja_mcp/ from Phase 23 is
    # picked up via the broad host/ entry below).
    ("host", "host"),
    ("start-uja.sh", "start-uja.sh"),
    ("start-uja.bat", "start-uja.bat"),
    # Phase 23 launchers: emit a ready-to-paste Cowork MCP-config snippet.
    ("start-uja-mcp.sh", "start-uja-mcp.sh"),
    ("start-uja-mcp.bat", "start-uja-mcp.bat"),

    # Build/CI scripts
    ("scripts/scan_pii.py", "scripts/scan_pii.py"),
    ("scripts/sync_to_public_v2.py", "scripts/sync_to_public_v2.py"),
    ("scripts/install-hooks.sh", "scripts/install-hooks.sh"),

    # ADRs (the architectural record IS public for v0.2.0 — it's how we explain
    # the design to the inner circle. Verify with PII scan.)
    ("docs/ADR-001-v0.2.0-architecture.md", "docs/ADR-001-v0.2.0-architecture.md"),
    ("docs/ADR-002-architecture-rethink.md", "docs/ADR-002-architecture-rethink.md"),

    # Website source. NOTE: during the bring-up phase on the v1 canonical's
    # dev/v0.2.0 branch the v2 site lives at website/v2/. After v2 canonical
    # promotes that to website/, this allowlist entry will hit the standard
    # location.
    ("website/v2", "website"),  # rewrite: src website/v2 → dst website
    # Once v2 canonical's website/ is the v2 site directly, swap the line above
    # to: ("website", "website")

    # Netlify deploy config — published from the v2 site dir when on v2 canonical
    ("website/v2/netlify.toml", "netlify.toml"),
]

# Session briefs (Dispatch-pattern brief-on-disk per CLAUDE.md "Dispatch session
# pattern" section). Auto-include all docs/session-*-brief.md so future briefs
# don't need a manual allowlist update on every new session.
ALLOWLIST.extend(
    (str(p.relative_to(ROOT)), str(p.relative_to(ROOT)))
    for p in sorted(ROOT.glob("docs/session-*-brief.md"))
)

# Files we DELIBERATELY exclude even if they're inside an allowlisted directory.
EXCLUDE_DST = {
    # ROADMAP stays canonical-only (matches v1 policy).
    "ROADMAP.md",
    # The Job-Assist eval-fixture docx (even redacted) is candidate-shaped.
    "skills/resume-targeter/evals",
    "references/examples",
    # PDF generators have hardcoded contact info baked into rendering.
    "references/scripts/generate-cover-letter-pdf.py",
    "references/scripts/generate-speaking-points-pdf.py",
    # docx-xml-editing.md contains a real phone number as an example.
    "references/patterns/docx-xml-editing.md",
}


def run(cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def is_excluded(rel_dst: str) -> bool:
    for ex in EXCLUDE_DST:
        if rel_dst == ex or rel_dst.startswith(ex.rstrip("/") + "/"):
            return True
    return False


def copy_one(src: Path, dst: Path, dry_run: bool):
    if not src.exists():
        print(f"  SKIP (missing): {src.relative_to(ROOT)}")
        return 0
    if dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst) if not dry_run else None
        else:
            dst.unlink() if not dry_run else None
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    # Print full src and dst paths (basename was misleading when copying to nested dst).
    try:
        rel_dst = dst.relative_to(dst.anchor) if dst.is_absolute() else dst
    except ValueError:
        rel_dst = dst
    print(f"  {'DRY' if dry_run else 'CP '}: {src.relative_to(ROOT)} → {rel_dst}")
    return 1


def prune_excluded(public_root: Path, dry_run: bool):
    pruned = 0
    for ex in sorted(EXCLUDE_DST):
        target = public_root / ex
        if target.exists():
            print(f"  {'DRY-PRUNE' if dry_run else 'PRUNE   '}: {ex}")
            if not dry_run:
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            pruned += 1
    return pruned


def pii_scan(public_root: Path) -> bool:
    scanner = ROOT / "scripts" / "scan_pii.py"
    if not scanner.exists():
        print("WARN: scripts/scan_pii.py not found; skipping PII scan.")
        return True
    proc = subprocess.run(
        [sys.executable, str(scanner), "--strict", "--repo-root", str(public_root)],
        capture_output=True, text=True,
    )
    print(proc.stdout)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        return False
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dst", type=Path, default=DST_DEFAULT,
                   help=f"Path to the cloned dst repo. Default: {DST_DEFAULT}")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not args.dst.exists():
        print(f"ERROR: dst repo not cloned at {args.dst}", file=sys.stderr)
        print(f"       git clone https://github.com/sharmingmilan/{DST_REPO_NAME}.git {args.dst}", file=sys.stderr)
        sys.exit(2)

    print(f"src: {ROOT}")
    print(f"dst: {args.dst}")
    print(f"dry-run: {args.dry_run}")
    print()

    print("== copy allowlist ==")
    n = 0
    for src_rel, dst_rel in ALLOWLIST:
        if is_excluded(dst_rel):
            continue
        n += copy_one(ROOT / src_rel, args.dst / dst_rel, args.dry_run)
    print(f"  copied: {n} entries")
    print()

    print("== prune EXCLUDE_DST ==")
    pruned = prune_excluded(args.dst, args.dry_run)
    print(f"  pruned: {pruned} entries")
    print()

    print("== PII scan (STRICT) ==")
    if not pii_scan(args.dst):
        print("FAIL: PII scan reported sensitive content. Aborting before push.", file=sys.stderr)
        sys.exit(3)
    print("  ok")
    print()

    if args.dry_run:
        print("dry-run complete; no commit/push.")
        return

    # Commit + push (let the caller actually `git push` so they can review the
    # diff first; we do NOT auto-push for safety)
    print("== git status (in dst) ==")
    status = run(["git", "status", "--short"], cwd=args.dst, check=False)
    print(status.stdout)

    if not status.stdout.strip():
        print("nothing to commit.")
        return

    print()
    print("Next steps (manual, review before pushing):")
    print(f"  cd {args.dst}")
    print(f"  git diff")
    print(f"  git add -A && git commit -m 'sync from v2 canonical'")
    print(f"  git push origin main")


if __name__ == "__main__":
    main()
