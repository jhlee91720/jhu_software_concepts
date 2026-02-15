import os
import psycopg

def main():
    db_url = os.getenv("DATABASE_URL", "dbname=gradcafe")
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS applicants;")
            cur.execute("""
            CREATE TABLE applicants (
                p_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                program TEXT,
                comments TEXT,
                date_added DATE,
                url TEXT,
                status TEXT,
                term TEXT,
                us_or_international TEXT,
                gpa FLOAT,
                gre FLOAT,
                gre_v FLOAT,
                gre_aw FLOAT,
                degree TEXT,
                llm_generated_program TEXT,
                llm_generated_university TEXT
            );
            """)
        conn.commit()

if __name__ == "__main__":
    main()
