"""Read analysis metrics from the applicants table."""


def _pct(part, whole):
    if not whole:
        return 0.0
    return (part / whole) * 100.0


def fetch_summary(conn):
    """Return raw summary counts and percentages for rendering."""
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM applicants;")
    total = cur.fetchone()[0] or 0

    cur.execute(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE us_or_international = %s;
        """,
        ("International",),
    )
    international = cur.fetchone()[0] or 0

    cur.execute(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE LOWER(status) LIKE '%%accept%%';
        """
    )
    accepted = cur.fetchone()[0] or 0

    cur.close()

    return {
        "total": total,
        "international": international,
        "accepted": accepted,
        "intl_pct": _pct(international, total),
        "accepted_pct": _pct(accepted, total),
    }


def build_analysis(conn):
    """Build analysis rows consumed by the Flask template."""
    summary = fetch_summary(conn)
    return [
        {
            "question": "How many entries do you have in your database?",
            "answer": f"Applicant count: {summary['total']}",
        },
        {
            "question": "What percentage of entries are from international students?",
            "answer": f"Percent International: {summary['intl_pct']:.2f}%",
        },
        {
            "question": "What percent of entries are acceptances?",
            "answer": f"Percent Accepted: {summary['accepted_pct']:.2f}%",
        },
    ]
