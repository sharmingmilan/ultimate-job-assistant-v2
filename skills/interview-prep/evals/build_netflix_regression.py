#!/usr/bin/env python3
"""
Build a regression content.json modeled on the Netflix Interview Prep project.

This script is a STRUCTURAL regression — it generates a content.json that
covers all 11 topics from the original Netflix build at the same shape
(11 topics x 3 phases x 3 difficulties = 99 problem cards), then the build
script renders a PWA. The smoke test confirms the renderer handles full
Netflix-scale content without errors or budget overrun.

The CONTENT here is intentionally placeholder-quality. A real Netflix run
would replace this with hand-authored worked examples (the original took
multiple sessions to author). The point of this regression is to prove the
TEMPLATE does not break at scale, not to ship study-quality content.

Usage:
    python3 skills/interview-prep/evals/build_netflix_regression.py [output_path]

Default output: skills/interview-prep/evals/netflix-regression-content.json
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

NETFLIX_TOPICS = [
    ("joins", "Multi-Table Joins", "T1", "Appears in every SQL interview"),
    ("windows", "Window Functions", "T1", "Very common: ranking, running totals, period-over-period"),
    ("ctes", "CTEs and Query Structure", "T1", "Signals senior-level code organization"),
    ("dates", "Date Manipulation", "T1", "Fiscal periods, rolling windows, durations"),
    ("dedup", "Deduplication", "T1", "Vendor name normalization, fuzzy dup detection"),
    ("case_agg", "CASE and Conditional Aggregation", "T1", "Bucketing, pivoting, flag composition"),
    ("nulls", "NULL Handling", "T1", "NULL semantics trip even experienced candidates"),
    ("full_outer", "FULL OUTER JOIN and Reconciliation", "T2", "AP vs HUB ledger reconciliation"),
    ("self_joins", "Self-Joins", "T2", "Intervals, overlaps, first/last-per-group"),
    ("set_ops", "Set Operations", "T2", "UNION / INTERSECT / EXCEPT for snapshot diffs"),
    ("pandas", "Pandas - groupby, merge, rolling", "PY", "Single Python question expected"),
]

DIFFICULTIES = ["easy", "medium", "hard"]


def make_schema_panel(topic_id, difficulty):
    return {
        "table": "payments",
        "columns": ["payment_id", "production_id", "vendor_id", "amount_usd", "paid_on"],
        "rows": [
            ["PMT-001", "P101", "V001", 12500, "2026-04-12"],
            ["PMT-002", "P101", "V002", 8000, "2026-04-15"],
            ["PMT-003", "P102", "V001", 4500, "2026-04-22"],
        ],
    }


def make_worked(topic_id, topic_title, difficulty):
    return {
        "difficulty": difficulty,
        "prompt": (
            f"Regression placeholder for topic {topic_title} at {difficulty} difficulty. "
            f"Business motivation: this is a synthetic prompt for structural regression "
            f"testing of the Ultimate Job Assistant interview-prep PWA template. "
            f"A real Netflix run would replace this with a hand-authored worked example."
        ),
        "schemas": [make_schema_panel(topic_id, difficulty)],
        "solution": (
            f"-- Worked example for {topic_id} at {difficulty}\n"
            f"SELECT production_id, SUM(amount_usd) AS total\n"
            f"FROM payments\n"
            f"GROUP BY production_id\n"
            f"ORDER BY total DESC;"
        ),
        "walk": [
            f"Walk bullet 1 for {topic_id} {difficulty}.",
            f"Walk bullet 2 for {topic_id} {difficulty}.",
            f"Walk bullet 3 for {topic_id} {difficulty}.",
            f"Walk bullet 4 for {topic_id} {difficulty}.",
        ],
    }


def make_faded(topic_id, topic_title, difficulty):
    return {
        "difficulty": difficulty,
        "prompt": f"Regression placeholder (faded) for {topic_title} at {difficulty}.",
        "schemas": [make_schema_panel(topic_id, difficulty)],
        "scaffold": (
            f"-- Faded for {topic_id} {difficulty}\n"
            f"SELECT production_id, _____(amount_usd) AS total\n"
            f"FROM payments\n"
            f"GROUP BY _____\n"
            f"ORDER BY total _____;"
        ),
        "solution": (
            f"-- Faded for {topic_id} {difficulty}\n"
            f"SELECT production_id, SUM(amount_usd) AS total\n"
            f"FROM payments\n"
            f"GROUP BY production_id\n"
            f"ORDER BY total DESC;"
        ),
        "walk": [
            f"First blank: aggregator (SUM)",
            f"Second blank: GROUP BY column (production_id)",
            f"Third blank: sort direction (DESC)",
            f"Fourth bullet for the {topic_id} faded case.",
        ],
    }


def make_retrieval(topic_id, topic_title, difficulty):
    return {
        "difficulty": difficulty,
        "prompt": f"Regression retrieval placeholder for {topic_title} at {difficulty}.",
        "schemas": [make_schema_panel(topic_id, difficulty)],
        "solution": (
            f"-- Retrieval reference for {topic_id} {difficulty}\n"
            f"SELECT vendor_id, COUNT(*) AS payments\n"
            f"FROM payments\n"
            f"WHERE paid_on >= '2026-01-01'\n"
            f"GROUP BY vendor_id;"
        ),
        "selfExplain": f"Why {topic_id} matters here at {difficulty}: explain in your own words.",
        "explanation": (
            f"This retrieval problem tests the {topic_id} concept at {difficulty} level. "
            f"The reference solution is one of several valid approaches; the value "
            f"comes from generating it without scaffolding."
        ),
    }


def build_topic(topic_id, title, tier, freq):
    mode = "python" if topic_id == "pandas" else "sql"
    return {
        "id": topic_id,
        "title": title,
        "tier": tier,
        "frequency_signal": freq,
        "sources": ["https://example.com/regression-source"],
        "language_mode": mode,
        "worked": [make_worked(topic_id, title, d) for d in DIFFICULTIES],
        "faded": [make_faded(topic_id, title, d) for d in DIFFICULTIES],
        "retrieval": [make_retrieval(topic_id, title, d) for d in DIFFICULTIES],
    }


def build_real_questions():
    return [
        {
            "id": "rq_001",
            "category": "SQL",
            "title": "Top 3 vendors per production",
            "prompt": "Return the top 3 vendors by spend per production, tiebreak on vendor_id.",
            "concepts": ["window functions", "ROW_NUMBER", "tiebreak"],
            "difficulty": "medium",
            "source": "Regression fixture (would be a real Glassdoor URL in a live run)",
            "source_url": "https://example.com/regression-glassdoor-thread",
        },
        {
            "id": "rq_002",
            "category": "Python",
            "title": "Rolling 7-day average per group",
            "prompt": "Given a payments DataFrame with date and amount columns and a production_id, compute a 7-day rolling average per production.",
            "concepts": ["pandas groupby", "rolling", "merge"],
            "difficulty": "medium",
            "source": "Regression fixture (would be a real source URL in a live run)",
            "source_url": "https://example.com/regression-blind-thread",
        },
    ]


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "netflix-regression-content.json"
    content = {
        "metadata": {
            "company": "Netflix",
            "role": "Data Analyst, Production Finance Operations and Innovation",
            "convention": "netflix-data-analyst-2026-04",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "primary_language": "sql",
            "dialect_note": "Regression target: Presto/Trino on Iceberg. Examples shown as Postgres-compatible SQL.",
            "empty_state_explanation": "Regression test fixture; real_questions tab populated with two synthetic-source examples for structural testing.",
        },
        "topics": [build_topic(*t) for t in NETFLIX_TOPICS],
        "real_questions": build_real_questions(),
        "exam_meta": {
            "format": "45-60 minute CoderPad screen, ~4 SQL + 1 Python",
            "alternateFormat": "Some candidates report a take-home variant",
            "keyInsight": "The screen tests verbalized reasoning under time pressure, not memorized syntax",
            "highROI": "Practice writing complete queries before running anything (mirrors the actual interview)",
        },
        "patterns": {
            "sql": [
                {"title": "Top N per group", "summary": "ROW_NUMBER + filter pattern", "snippet": "ROW_NUMBER() OVER (PARTITION BY g ORDER BY x DESC)"},
                {"title": "Half-open date interval", "summary": "Avoids BETWEEN gotchas with timestamps", "snippet": "WHERE col >= start AND col < end"},
            ],
            "python": [
                {"title": "groupby + agg", "summary": "Aggregate by group with multiple metrics", "snippet": "df.groupby('g').agg(total=('amt','sum'))"},
            ],
        },
    }
    out.write_text(json.dumps(content, indent=2, ensure_ascii=False))
    print(f"Wrote regression content.json: {out}")
    print(f"  topics: {len(content['topics'])}")
    print(f"  problem cards (worked + faded + retrieval): {sum(len(t['worked']) + len(t['faded']) + len(t['retrieval']) for t in content['topics'])}")
    print(f"  real_questions: {len(content['real_questions'])}")
    print(f"  size on disk: {out.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
