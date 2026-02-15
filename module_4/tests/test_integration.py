import pytest
import os
import psycopg
from src.app import create_app


@pytest.mark.integration
def test_end_to_end_pull_updates_analysis():

    db_url = os.getenv("DATABASE_URL", "dbname=gradcafe")

    # count rows before
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM applicants;")
            before = cur.fetchone()[0]

    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    # trigger pull
    resp = client.post("/pull-data")
    assert resp.status_code in (200, 202)

    # count rows after
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM applicants;")
            after = cur.fetchone()[0]

    assert after >= before

    # verify analysis page loads after update
    resp2 = client.get("/analysis")
    assert resp2.status_code == 200
