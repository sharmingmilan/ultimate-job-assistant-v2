# References

Reusable templates, scripts, examples, and patterns for building skills and running workflows. Everything here is a copy; originals live in their respective locations.

## Structure

```
references/
├── templates/          ← Blank templates for new files
│   └── research-brief.md
├── scripts/            ← PDF generation scripts (reportlab)
│   ├── generate-speaking-points-pdf.py
│   └── generate-cover-letter-pdf.py
├── examples/           ← Completed outputs from the Waymo lifecycle test (pre-restructure naming)
│   ├── company-context-waymo.md       (historical, now replaced by research/[company].md)
│   ├── role-context-waymo-bi-analyst.md (historical, now replaced by tracker.md)
│   ├── research-brief-waymo.md
│   ├── decoded-jd-waymo.md
│   ├── score-after-waymo.md
│   ├── speaking-points-waymo.md
│   └── cover-letter-waymo.md
└── patterns/           ← Reusable methodology and rules
    ├── formatting-rules.md
    ├── docx-xml-editing.md
    ├── scoring-methodology.md
    └── adaptive-qa.md
```

## Usage

- **Building a new skill**: Check patterns/ for methodology that already exists
- **Starting a new application**: Use templates/research-brief.md as starting point for new company research
- **Generating PDFs**: Adapt scripts/ to the new content type
- **Quality reference**: Compare outputs against examples/ to maintain consistency
