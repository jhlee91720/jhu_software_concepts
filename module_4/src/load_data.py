"""Load scraped rows into Postgres applicants table."""

import json

from src.clean import clean_text, to_float


REQUIRED_NON_NULL_FIELDS = ("program", "url", "status", "term")


def create_table(conn):
    """Ensure applicants table exists with required schema and uniqueness policy."""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS applicants (
            p_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            program TEXT NOT NULL,
            comments TEXT,
            date_added DATE,
            url TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            term TEXT NOT NULL,
            us_or_international TEXT,
            gpa FLOAT,
            gre FLOAT,
            gre_v FLOAT,
            gre_aw FLOAT,
            degree TEXT,
            llm_generated_program TEXT,
            llm_generated_university TEXT
        );
        """
    )
    conn.commit()
    cur.close()


def _prepared_row(raw):
    return {
        "program": clean_text(raw.get("program")),
        "comments": clean_text(raw.get("comments")),
        "date_added": clean_text(raw.get("date_added")),
        "url": clean_text(raw.get("url")),
        "status": clean_text(raw.get("applicant_status") or raw.get("status")),
        "term": clean_text(raw.get("semester_year_start") or raw.get("term")),
        "us_or_international": clean_text(raw.get("citizenship") or raw.get("us_or_international")),
        "gpa": to_float(raw.get("gpa")),
        "gre": to_float(raw.get("gre")),
        "gre_v": to_float(raw.get("gre_v")),
        "gre_aw": to_float(raw.get("gre_aw")),
        "degree": clean_text(raw.get("masters_or_phd") or raw.get("degree")),
        "llm_generated_program": clean_text(raw.get("llm-generated-program") or raw.get("llm_generated_program")),
        "llm_generated_university": clean_text(raw.get("llm-generated-university") or raw.get("llm_generated_university")),
    }


def _has_required_fields(row):
    return all(row.get(field) for field in REQUIRED_NON_NULL_FIELDS)


def insert_rows(conn, rows):
    """Insert rows with idempotency via unique URL conflict handling."""
    cur = conn.cursor()
    inserted = 0

    for raw in rows:
        row = _prepared_row(raw)
        if not _has_required_fields(row):
            continue

        cur.execute(
            """
            INSERT INTO applicants (
                program, comments, date_added, url, status, term,
                us_or_international, gpa, gre, gre_v, gre_aw,
                degree, llm_generated_program, llm_generated_university
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING;
            """,
            (
                row["program"],
                row["comments"],
                row["date_added"],
                row["url"],
                row["status"],
                row["term"],
                row["us_or_international"],
                row["gpa"],
                row["gre"],
                row["gre_v"],
                row["gre_aw"],
                row["degree"],
                row["llm_generated_program"],
                row["llm_generated_university"],
            ),
        )
        inserted += max(0, getattr(cur, "rowcount", 0))

    conn.commit()
    cur.close()
    return inserted


def read_jsonl(path):
    """Read line-delimited JSON rows."""
    rows = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_jsonl(conn, path):
    """Convenience wrapper: read JSONL and insert all valid rows."""
    rows = read_jsonl(path)
    return insert_rows(conn, rows)
