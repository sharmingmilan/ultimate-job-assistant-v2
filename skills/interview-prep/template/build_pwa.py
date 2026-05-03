#!/usr/bin/env python3
"""
Build a deployable Ultimate Job Assistant interview-prep PWA from a content.json.

Usage:
    python3 build_pwa.py <content.json> <output_dir>

Reads the templates from the same directory as this script (assumes you call it
from skills/interview-prep/template/), validates the content against the
content-schema.json one level up, and writes the deploy folder.

Exit codes:
    0  success
    1  schema validation failed
    2  template missing
    3  unexpected error
"""
import json
import sys
import shutil
import re
from pathlib import Path
from datetime import datetime, timezone


def fail(code, msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def validate_content(content_path, schema_path):
    try:
        from jsonschema import validate, ValidationError
    except ImportError:
        print("WARNING: jsonschema not installed; skipping validation. Install with: pip install jsonschema")
        return
    with open(schema_path) as f:
        schema = json.load(f)
    with open(content_path) as f:
        content = json.load(f)
    try:
        validate(instance=content, schema=schema)
        print(f"  schema validation: OK")
    except ValidationError as e:
        path = " -> ".join(str(p) for p in e.absolute_path)
        fail(1, f"content fails schema validation at '{path}': {e.message[:200]}")


def short_name(company, max_len=12):
    s = re.sub(r"[^a-zA-Z0-9 ]", "", company)
    return s[:max_len].strip() or "Prep"


def render(template_text, replacements):
    out = template_text
    for k, v in replacements.items():
        out = out.replace("{{" + k + "}}", v)
    return out


def main():
    if len(sys.argv) != 3:
        fail(3, "usage: build_pwa.py <content.json> <output_dir>")
    content_path = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve()
    template_dir = Path(__file__).parent
    schema_path = template_dir.parent / "content-schema.json"

    print(f"Building UJA interview-prep PWA")
    print(f"  content: {content_path}")
    print(f"  output:  {out_dir}")
    print(f"  template: {template_dir}")
    print()

    if not content_path.is_file():
        fail(3, f"content.json not found: {content_path}")
    for tname in ["index.html.template", "app.jsx.template", "manifest.json.template", "sw.js", "icon-192.png", "icon-512.png"]:
        p = template_dir / tname
        if not p.exists():
            fail(2, f"missing template file: {p}")

    if schema_path.exists():
        validate_content(content_path, schema_path)
    else:
        print(f"  WARNING: schema not found at {schema_path}; skipping validation")

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(content_path) as f:
        content = json.load(f)
    company = content["metadata"]["company"]
    role = content["metadata"]["role"]
    title = f"{company} {role}"

    # Render index.html
    idx_tpl = (template_dir / "index.html.template").read_text()
    app_jsx = (template_dir / "app.jsx.template").read_text()
    content_json = json.dumps(content, ensure_ascii=False)
    rendered_html = render(idx_tpl, {
        "TITLE": title,
        "COMPANY": company,
        "CONTENT_JSON": content_json,
        "APP_JSX": app_jsx,
    })
    (out_dir / "index.html").write_text(rendered_html)

    # Render manifest.json
    man_tpl = (template_dir / "manifest.json.template").read_text()
    rendered_man = render(man_tpl, {
        "COMPANY": company,
        "ROLE": role,
        "SHORT_NAME": short_name(company),
    })
    (out_dir / "manifest.json").write_text(rendered_man)

    # Copy static assets
    for fname in ["sw.js", "icon-192.png", "icon-512.png"]:
        shutil.copyfile(template_dir / fname, out_dir / fname)

    # Copy raw content.json + raw app.jsx for transparency
    shutil.copyfile(content_path, out_dir / "content.json")
    (out_dir / "app.jsx").write_text(app_jsx)

    # Write a deploy README
    readme = f"""# {title} — Interview Prep PWA

Generated: {datetime.now(timezone.utc).isoformat()}

## What this is

A study site for the {role} interview at {company}. Built by Ultimate Job Assistant
on the same pedagogical model documented in references/pedagogy.md.

## How to deploy (free, ~30 seconds)

1. Visit https://app.netlify.com/drop
2. Drag this entire folder onto the page
3. You'll get an HTTPS URL in seconds

## How to install on your phone

**iPhone (Safari):**
1. Open the deployed URL
2. Tap the share button
3. Scroll down and tap "Add to Home Screen"

**Android (Chrome):**
1. Open the deployed URL
2. Tap the three-dot menu
3. Tap "Install app"

After install the site loads instantly and works offline.

## Files in this folder

- `index.html` — the deployable single-file app (~250–400 KB)
- `app.jsx` — unminified React source for reference
- `content.json` — the topic and question data
- `manifest.json`, `sw.js`, `icon-192.png`, `icon-512.png` — PWA shell

## Progress is per-browser

Your typed answers persist to `localStorage` in each browser. iOS Safari may clear
this after about 7 days of inactivity. If you study daily, you should not lose
progress. Don't clear browser data for this site unless you want to start over.
"""
    (out_dir / "README.md").write_text(readme)

    # Sanity stats
    idx_size = (out_dir / "index.html").stat().st_size
    print(f"  rendered: index.html ({idx_size:,} bytes)")
    print(f"  rendered: manifest.json")
    print(f"  copied:   sw.js, icon-192.png, icon-512.png, content.json, app.jsx, README.md")
    print()
    if idx_size > 400_000:
        print(f"  WARNING: index.html exceeds 400KB target ({idx_size:,} bytes)")
    else:
        print(f"  index.html is within the 400KB budget")
    print(f"\nBuild complete: {out_dir}")


if __name__ == "__main__":
    main()
