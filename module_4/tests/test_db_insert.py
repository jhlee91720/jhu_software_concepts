import os
import pytest
import psycopg
from src.app import create_app

@pytest.mark.db
def test_pull_data_inserts_rows_and_is_idempotent():
    db_url = os.getenv("DATABASE_URL", "dbname=gradcafe")

    # Count rows before
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM applicants;")
            before = cur.fetchone()[0]

    # Run pull-data once (API style: no ui=1)
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()
    resp1 = client.post("/pull-data")
    assert resp1.status_code in (200, 202)

    # Count rows after first pull
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM applicants;")
            after1 = cur.fetchone()[0]

    assert after1 == before +1

    # Run pull-data again
    resp2 = client.post("/pull-data")
    assert resp2.status_code in (200, 202)

    # Count rows after second pull
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM applicants;")
            after2 = cur.fetchone()[0]

    # Should not create duplicates (idempotent)
    assert after2 == after1
