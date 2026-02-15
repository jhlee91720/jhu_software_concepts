"""Simple data source adapter used by the Pull Data endpoint.

This module intentionally uses a local JSONL file so tests stay deterministic.
"""

import os

from src.load_data import read_jsonl


DEFAULT_SAMPLE_PATH = "module_3/data/llm_extend_applicant_data (1).json"


def _map_row(raw):
    return {
        "program": raw.get("program", "Unknown Program"),
        "comments": raw.get("comments", ""),
        "date_added": raw.get("date_added", "2026-01-01"),
        "url": raw.get("url", "https://example.com/fallback-url"),
        "applicant_status": raw.get("applicant_status", raw.get("status", "Pending")),
        "semester_year_start": raw.get("semester_year_start", raw.get("term", "Fall 2026")),
        "citizenship": raw.get("citizenship", raw.get("us_or_international", "International")),
        "gpa": raw.get("gpa"),
        "gre": raw.get("gre"),
        "gre_v": raw.get("gre_v"),
        "gre_aw": raw.get("gre_aw"),
        "masters_or_phd": raw.get("masters_or_phd", raw.get("degree", "Masters")),
        "llm-generated-program": raw.get("llm-generated-program", raw.get("llm_generated_program", "Computer Science")),
        "llm-generated-university": raw.get("llm-generated-university", raw.get("llm_generated_university", "Unknown University")),
    }


def scrape_rows(sample_path=None, limit=20):
    """Return up to `limit` rows from a local dataset, with a fallback row."""
    path = sample_path or os.getenv("GRADCAFE_SAMPLE_JSONL", DEFAULT_SAMPLE_PATH)

    if os.path.exists(path):
        rows = read_jsonl(path)
        return [_map_row(row) for row in rows[:limit]]

    return [
        {
            "program": "Johns Hopkins University Computer Science",
            "comments": "fallback sample",
            "date_added": "2026-01-01",
            "url": "https://example.com/fallback-sample-1",
            "applicant_status": "Accepted",
            "semester_year_start": "Fall 2026",
            "citizenship": "International",
            "gpa": "3.80",
            "gre": "330",
            "gre_v": "160",
            "gre_aw": "4.5",
            "masters_or_phd": "Masters",
            "llm-generated-program": "Computer Science",
            "llm-generated-university": "Johns Hopkins University",
        }
    ]
