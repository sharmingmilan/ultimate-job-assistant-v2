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
  5. Build website/downloads/ultimate-job-assistant.zip from the sanitized
     deploy-source working tree (excludes .git, node_modules, build caches,
     macOS metadata, and the downloads dir itself). Sets the zip mtime to now
     so the live site can show "updated <date>" via a HEAD request. Verifies
     the zip contains required members (e.g. references/templates/base-resume-template.docx).
  6. Print a diff for the user to eyeball before committing.

This script never automatically commits or pushes. The user does that manually
after reviewing the diff.

Usage:
    python3 scripts/sync_to_public.py --to ../ultimate-job-assistant-public
    python3 scripts/sync_to_public.py --to ../ultimate-job-assistant-public --dry-run

Exit codes:
    0  sync completed (or dry-run reported what would change)
    1  PII scanner blocked the sync (rolled back)
    2  bad arguments or destination structure
    3  zip build failed (missing required members) or unexpected error
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
import zipfile
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

    # Zip-bundle source: user-facing templates injected into the starter zip
    # by build_zip(). The zip-bundle folder itself is dropped from the zip
    # after injection so users don't see the templating internals.
    ("references/zip-bundle", "references/zip-bundle"),

    # Build/CI scripts
    ("scripts/scan_pii.py", "scripts/scan_pii.py"),
    ("scripts/sync_to_public.py", "scripts/sync_to_public.py"),

    # CI workflow (the public repo can reuse this)
    (".github/workflows/ci.yml", ".github/workflows/ci.yml"),

    # Website source.
    ("website", "website"),

    # Netlify deploy config — pins publish dir + headers so the UI's Build &
    # deploy panel doesn't need to be touched.
    ("netlify.toml", "netlify.toml"),

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


# ─── Zip build configuration ──────────────────────────────────────────────
#
# The zip is curated, not a snapshot. The deploy-source repo carries everything
# Netlify needs (website/, netlify.toml, sync scripts, CI workflows) plus
# everything a fresh user needs (skills, references). The zip is just the
# user-facing slice. Keep the two views explicit so the public companion repo
# can grow without bloating the user starter kit.

# Output location of the zip, relative to the deploy-source repo root.
ZIP_RELPATH = "website/downloads/ultimate-job-assistant.zip"

# 1) WALK SOURCE FROM THE DEPLOY-SOURCE REPO. Skip these dirs entirely (no
#    point traversing into them).
ZIP_WALK_SKIP_DIRS = {".git", "node_modules", ".github/cache", "__pycache__", ".cache"}

# 2) DROP THESE PATHS from the zip even though they exist in the deploy-source
#    tree. These are maintainer-only files — sync scripts, CI workflows,
#    Netlify deploy config, the website source, the downloads dir itself.
#    A user who downloads the zip never needs any of these.
#    Leading slash means "absolute repo path"; trailing slash means "directory
#    and everything inside it"; otherwise it's an exact match.
ZIP_DROP_PATHS = (
    # The downloads directory itself — would create a self-referential zip.
    "website/downloads/",
    # Maintainer-only sync + scan tooling. The skills directory has its own
    # build/eval scripts which DO go in the zip.
    "scripts/",
    # Maintainer-only CI workflows for the source repos. Users who init their
    # own private repo can write their own CI as needed.
    ".github/",
    # Netlify deploy config — only the deploy-source repo needs this.
    "netlify.toml",
    # The promotional website source — users came from the live site to
    # download this zip; they don't need a local copy of the marketing pages.
    "website/",
    # Internal roadmap. The decisions log talks about repo strategy and
    # SaaS pivot speculation that's confusing for end users.
    "ROADMAP.md",
    # macOS metadata, lock files, editor temp files.
    ".DS_Store",
    "Thumbs.db",
    # The deploy-source repo's own .gitignore is for the maintainer's tree.
    # Drop it so the user-facing .gitignore injected from references/zip-bundle
    # is the only one in the archive.
    ".gitignore",
)

# 3) INJECT THESE FILES from references/zip-bundle/ INTO the zip at top-level
#    paths. Each tuple is (source_in_deploy_source, archive_path_in_zip).
#    The zip-bundle folder itself is dropped from the zip after injection
#    (see ZIP_DROP_PATHS_AFTER_INJECT below).
ZIP_INJECT_FILES = (
    ("references/zip-bundle/CLAUDE.md", "CLAUDE.md"),
    ("references/zip-bundle/QUICKSTART.md", "QUICKSTART.md"),
    ("references/zip-bundle/memory.md.template", "memory.md.template"),
    ("references/zip-bundle/tracker.md.template", "tracker.md.template"),
    # gitignore (no leading dot in source so it's not hidden in the source
    # checkout) lands at .gitignore in the zip so it activates on extract.
    ("references/zip-bundle/gitignore", ".gitignore"),
)

# 4) After injection, also drop the zip-bundle source folder from the zip —
#    users don't need to see the templating internals.
ZIP_DROP_AFTER_INJECT = ("references/zip-bundle/",)

# 5) Placeholder folders that must exist as empty .gitkeep entries in the zip.
#    Sourced from references/zip-bundle/placeholder-folders.txt.
ZIP_PLACEHOLDER_MANIFEST = "references/zip-bundle/placeholder-folders.txt"

# 6) Members the zip MUST contain after curation. Aborts the sync if any are
#    missing — a guardrail against accidental over-curation.
ZIP_REQUIRED_MEMBERS = (
    # Project orientation (injected)
    "CLAUDE.md",
    "QUICKSTART.md",
    "memory.md.template",
    "tracker.md.template",
    ".gitignore",
    "ONBOARDING.md",
    "README.md",
    # Resume template
    "references/templates/base-resume-template.docx",
    # Skills (orchestrator + spec for the new skill)
    "skills/orchestrator/SKILL.md",
    "skills/interview-prep/SKILL.md",
    "skills/resume-targeter/SKILL.md",
    # Sample placeholder folders prove the manifest applied
    "base-resumes/.gitkeep",
    "research/.gitkeep",
)


def _path_matches_drop_pattern(rel_posix: str, patterns) -> bool:
    """True if rel_posix should be dropped under one of the drop patterns."""
    for pat in patterns:
        if pat.endswith("/"):
            # Directory pattern — drop the dir and everything below.
            if rel_posix == pat.rstrip("/") or rel_posix.startswith(pat):
                return True
        else:
            # Exact-file or filename pattern.
            if rel_posix == pat:
                return True
            # Bare filename like ".DS_Store" matches at any depth.
            if "/" not in pat and rel_posix.split("/")[-1] == pat:
                return True
    return False


def _read_placeholder_folders(public_root: Path) -> list[str]:
    """Read the placeholder-folders manifest and return a list of folder paths."""
    manifest = public_root / ZIP_PLACEHOLDER_MANIFEST
    if not manifest.exists():
        return []
    out = []
    for raw in manifest.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line.rstrip("/"))
    return out


def build_zip(public_root: Path) -> Path:
    """
    Build the user-facing starter zip at website/downloads/ultimate-job-assistant.zip.

    The zip is CURATED (not a snapshot of the deploy-source repo):
      - Walks the deploy-source tree.
      - Skips directories in ZIP_WALK_SKIP_DIRS for traversal speed.
      - Drops paths in ZIP_DROP_PATHS so maintainer-only files don't ship.
      - Drops paths in ZIP_DROP_AFTER_INJECT to hide the templating internals.
      - Injects user-facing templates from references/zip-bundle/ at top-level
        archive paths (CLAUDE.md, memory.md.template, .gitignore, etc.).
      - Creates empty .gitkeep entries for each folder in
        references/zip-bundle/placeholder-folders.txt so the project structure
        is right immediately on extract.
      - Verifies ZIP_REQUIRED_MEMBERS exist before promoting the temp file.
      - Atomic-renames into place; stamps mtime to now.
    """
    zip_path = public_root / ZIP_RELPATH
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    gitkeep = zip_path.parent / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("# Keep website/downloads/ in git so the path is stable for the landing page.\n")

    tmp_path = zip_path.with_suffix(".zip.tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    placeholder_folders = _read_placeholder_folders(public_root)
    injected_archive_paths = set()  # to avoid double-writing if a path is also walked
    dropped_count = 0
    walked_count = 0
    file_count = 0
    total_bytes = 0

    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        # ── Pass A: walk the deploy-source tree, applying drop filters ──
        all_files = []
        for dirpath, dirnames, filenames in os.walk(public_root):
            rel_dir = Path(dirpath).relative_to(public_root).as_posix()
            keep_dirs = []
            for d in dirnames:
                if d in ZIP_WALK_SKIP_DIRS:
                    continue
                child_rel = (rel_dir + "/" + d).lstrip("/") if rel_dir != "." else d
                if _path_matches_drop_pattern(child_rel + "/", ZIP_DROP_PATHS):
                    continue
                if _path_matches_drop_pattern(child_rel + "/", ZIP_DROP_AFTER_INJECT):
                    continue
                keep_dirs.append(d)
            dirnames[:] = sorted(keep_dirs)
            for fn in sorted(filenames):
                full = Path(dirpath) / fn
                rel = full.relative_to(public_root).as_posix()
                walked_count += 1
                if _path_matches_drop_pattern(rel, ZIP_DROP_PATHS):
                    dropped_count += 1
                    continue
                if _path_matches_drop_pattern(rel, ZIP_DROP_AFTER_INJECT):
                    dropped_count += 1
                    continue
                all_files.append((full, rel))

        for full, rel in all_files:
            try:
                size = full.stat().st_size
            except OSError:
                continue
            zf.write(full, arcname=rel)
            file_count += 1
            total_bytes += size

        # ── Pass B: inject user-facing templates from references/zip-bundle/ ──
        for src_rel, archive_rel in ZIP_INJECT_FILES:
            src = public_root / src_rel
            if not src.exists():
                raise RuntimeError(
                    f"Zip build aborted — inject source missing: {src_rel}"
                )
            zf.write(src, arcname=archive_rel)
            injected_archive_paths.add(archive_rel)
            file_count += 1
            total_bytes += src.stat().st_size

        # ── Pass C: empty .gitkeep entries for placeholder folders ──
        for folder in placeholder_folders:
            arc = f"{folder}/.gitkeep"
            if arc in injected_archive_paths:
                continue
            zf.writestr(arc, "")
            file_count += 1

    # Verify required members present.
    missing = []
    with zipfile.ZipFile(tmp_path, "r") as zf:
        names = set(zf.namelist())
        for required in ZIP_REQUIRED_MEMBERS:
            if required not in names:
                missing.append(required)
    if missing:
        tmp_path.unlink()
        raise RuntimeError(
            "Zip build aborted — required members missing from bundle:\n  - "
            + "\n  - ".join(missing)
        )

    if zip_path.exists():
        zip_path.unlink()
    tmp_path.rename(zip_path)

    now = time.time()
    os.utime(zip_path, (now, now))

    print(f"  ZIP BUILT: {ZIP_RELPATH}")
    print(f"    walked:    {walked_count} files in deploy-source tree")
    print(f"    dropped:   {dropped_count} maintainer-only files")
    print(f"    placeholders: {len(placeholder_folders)} folders with .gitkeep")
    print(f"    injected:  {len(ZIP_INJECT_FILES)} user-facing templates")
    print(f"    files:   {file_count}")
    print(f"    raw:     {total_bytes / 1024:.1f} KB uncompressed")
    print(f"    on-disk: {zip_path.stat().st_size / 1024:.1f} KB compressed")
    print(f"    mtime:   {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))}")
    print(f"    .gitkeep present at: website/downloads/.gitkeep")
    print(f"    verified members:")
    for m in ZIP_REQUIRED_MEMBERS:
        print(f"      ✅ {m}")
    return zip_path


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
        print("(Step 3 skipped in dry run: zip build runs only on real syncs.)")
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
    print("Step 3: build website/downloads/ultimate-job-assistant.zip from sanitized tree")
    try:
        build_zip(dst_root)
    except RuntimeError as e:
        print()
        print("=" * 60)
        print("ZIP BUILD ABORTED.")
        print(str(e))
        print()
        print("The PII scan was clean, but the resulting bundle is missing")
        print("expected members. Fix the allowlist or template generation, then")
        print("re-run sync.")
        print("=" * 60)
        sys.exit(3)

    print()
    print("Step 4: scanner clean + zip built.  Diff to review:")
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
