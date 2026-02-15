import pytest

from src.load_data import insert_rows
from src.query_data import fetch_summary
from tests.fakes import FakeConn, sample_row


@pytest.mark.db
def test_insert_rows_on_pull_writes_required_non_null_fields():
    conn = FakeConn()
    inserted = insert_rows(conn, [sample_row("required")])

    assert inserted == 1
    assert len(conn.rows) == 1

    first = conn.rows[0]
    assert first["program"] is not None
    assert first["url"] is not None
    assert first["status"] is not None
    assert first["term"] is not None


@pytest.mark.db
def test_idempotency_duplicate_rows_do_not_create_duplicates():
    conn = FakeConn()
    row = sample_row("dupe")

    first_inserted = insert_rows(conn, [row])
    second_inserted = insert_rows(conn, [row])

    assert first_inserted == 1
    assert second_inserted == 0
    assert len(conn.rows) == 1


@pytest.mark.db
def test_simple_summary_query_returns_expected_keys():
    conn = FakeConn()
    insert_rows(conn, [sample_row("1"), sample_row("2", status="Rejected")])

    summary = fetch_summary(conn)
    assert set(summary.keys()) == {"total", "international", "accepted", "intl_pct", "accepted_pct"}
