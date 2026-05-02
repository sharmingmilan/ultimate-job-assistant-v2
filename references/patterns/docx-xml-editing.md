# DOCX XML Editing Pattern
# For resume-targeter and any skill that modifies .docx files

---

## Workflow

1. **Unpack**: `python3 mnt/.claude/skills/docx/scripts/office/unpack.py [input.docx] [output-dir]`
2. **Edit XML**: Modify `[output-dir]/word/document.xml` using Edit tool or Python
3. **Validate** (optional): `python3 mnt/.claude/skills/docx/scripts/office/validate.py [output-dir]`
4. **Pack**: `python3 mnt/.claude/skills/docx/scripts/office/pack.py [output-dir] [output.docx]`
   - Use `--validate false` if pre-existing validation issues (e.g., tel: links)
5. **Convert to PDF**: `libreoffice --headless --convert-to pdf --outdir [dir] [output.docx]`

## Common XML Operations

### Replace text in a run
Find the `<w:t>` element containing the old text, replace with new text. Preserve all surrounding `<w:rPr>` formatting.

### Replace a full bullet
Find the `<w:p>` paragraph containing the bullet text. Replace all `<w:r>` runs while preserving the paragraph's `<w:pPr>` properties (especially `<w:numPr>` for bullet styling).

### Verify contact line
Grep for `https://` and `http://` in `<w:t>` elements of the contact paragraph. None should exist in display text.

### Verify page count
Convert to PDF and check page count before delivering. If over 2 pages, tighten bullets and reconvert.

## Known Issues

- **tel: links**: Base resume may contain `tel:+16618735077` in document.xml.rels which fails validation. Use `--validate false`.
- **Inter-device file moves**: `mv` between sandbox and mounted folder fails. Use `cp` or `cat source > destination` instead.
- **soffice.py timeout**: The soffice.py wrapper may timeout. Fall back to direct `libreoffice --headless --convert-to pdf` command.
