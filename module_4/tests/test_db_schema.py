import pytest
import psycopg
import os

@pytest.mark.db
def test_applicants_table_exists():

    # same connection logic your app uses
    db_url = os.getenv("DATABASE_URL", "dbname=gradcafe")

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:

            # check if table exists
            cur.execute("SELECT to_regclass('public.applicants');")
            table = cur.fetchone()[0]

    assert table == "applicants"
