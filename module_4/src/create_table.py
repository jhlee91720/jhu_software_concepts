import os
import psycopg

def get_conn():
    # Use DATABASE_URL if present (GitHub Actions), otherwise fall back to local
    db_url = os.getenv("DATABASE_URL", "dbname=gradcafe")
    return psycopg.connect(db_url)

def create_tables():
    with get_conn() as conn:
        with conn.cursor() as cur:
            # idempotent: re-create cleanly each run
            cur.execute("DROP TABLE IF EXISTS applicants;")

            cur.execute("""
                CREATE TABLE applicants (
                    id SERIAL PRIMARY KEY,
                    program TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,

                    term TEXT,
                    us_or_international TEXT,
                    gpa DOUBLE PRECISION,
                    gre DOUBLE PRECISION,
                    gre_v DOUBLE PRECISION,
                    gre_aw DOUBLE PRECISION,
                    degree TEXT,
                    year INTEGER
                );
            """)

        conn.commit()

if __name__ == "__main__":
    create_tables()
