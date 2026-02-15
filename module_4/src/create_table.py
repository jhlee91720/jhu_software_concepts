import psycopg

conn = psycopg.connect("dbname=gradcafe")
cur = conn.cursor()

# Drop table if it exists (safe now because no data yet)
cur.execute("""
DROP TABLE IF EXISTS applicants;
""")

# Create fresh table with correct schema
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

cur.close()
conn.close()