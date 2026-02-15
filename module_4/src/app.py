from flask import Flask, render_template, redirect, url_for, jsonify, request
import psycopg
import subprocess
import os
import uuid

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"))

    app.config["PULL_RUNNING"] = False
    app.config["LAST_MESSAGE"] = None
    
    @app.route("/")
    def home():
        return redirect(url_for("analysis"))
      
    @app.route("/analysis")
    def analysis():
        results = build_results()
        message = app.config["LAST_MESSAGE"]
        app.config["LAST_MESSAGE"] = None
        return render_template("analysis.html", results=results, message=message)


    @app.route("/pull-data", methods=["POST"])
    def pull_data():

        if app.config["PULL_RUNNING"]:
            app.config["LAST_MESSAGE"] = "Pull Data is already running. Please wait."
            if "text/html" in request.headers.get("Accept", ""):
                return redirect(url_for("analysis"))
            else:
                return jsonify({"busy": True}), 409
        app.config["PULL_RUNNING"] = True
        
        if app.config.get("TESTING"):

            # create unique test URL only once per test run
            if "TEST_URL" not in app.config:
                app.config["TEST_URL"] = f"http://example.com/test-url-{uuid.uuid4()}"

            test_url = app.config["TEST_URL"]

            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO applicants (program, url, status)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (url) DO NOTHING;
                        """,
                        ("TEST_PROGRAM", test_url, "TEST_STATUS")
                    )
                conn.commit()

            app.config["LAST_MESSAGE"] = "Pull Data completed (test insert)."

        
        try:
            app.config["LAST_MESSAGE"] = "Pull Data completed (placeholder)."
        except Exception as e:
            app.config["LAST_MESSAGE"] = f"Pull Data failed: {e}"
        finally:
            app.config["PULL_RUNNING"] = False

        if "text/html" in request.headers.get("Accept", ""):
            return redirect(url_for("analysis"))
        else:
            return jsonify({"ok": True}), 202

    
    



    @app.route("/update-analysis", methods=["POST"])
    def update_analysis():

        if app.config["PULL_RUNNING"]:
            app.config["LAST_MESSAGE"] = "Update Analysis skipped because Pull Data is running."
            if "text/html" in request.headers.get("Accept", ""):
                return redirect(url_for("analysis"))
            else:
                return jsonify({"busy": True}), 409


        app.config["LAST_MESSAGE"] = "Analysis updated."
        if "text/html" in request.headers.get("Accept", ""):
            return redirect(url_for("analysis"))
        else:
            return jsonify({"ok": True}), 200

    
    return app

def get_conn():
    db_url = os.getenv("DATABASE_URL", "dbname=gradcafe")
    return psycopg.connect(db_url)

def normalize_text(s):
    if not s:
        return ""
    s = s.lower()
    for ch in [",", ".", "-", "_", "/", "(", ")", ":", ";"]:
        s = s.replace(ch, " ")
    return " ".join(s.split())

def is_cs_program(text):
    t = normalize_text(text)
    tokens = t.split()

    if "computer science" in t or "compsci" in t or "comp sci" in t:
        return True

    # handle CS / C.S.
    for i in range(len(tokens)-1):
        if tokens[i] == "c" and tokens[i+1] == "s":
            return True
    if "cs" in tokens:
        return True

    return False

def is_masters_degree(degree):
    d = normalize_text(degree)
    tokens = d.split()

    if "master" in d:
        return True
    if "ms" in tokens or "msc" in tokens:
        return True

    for i in range(len(tokens)-1):
        if tokens[i] == "m" and tokens[i+1] == "s":
            return True
    return False

def is_jhu(program):
    p = normalize_text(program)
    return "jhu" in p or "hopkin" in p

def is_target_university(program_text):
    p = normalize_text(program_text)

    # We check common variants/abbreviations
    if "georgetown" in p:
        return True
    if "stanford" in p:
        return True
    if "carnegie mellon" in p or "cmu" in p:
        return True
    if "massachusetts institute of technology" in p:
        return True

    # token-safe MIT check (avoid matching random words)
    tokens = p.split()
    if "mit" in tokens:
        return True

    return False

def is_target_university_llm(university_text):
    u = normalize_text(university_text)
    tokens = u.split()

    if "georgetown" in u:
        return True
    if "stanford" in u:
        return True
    if "carnegie mellon" in u or "cmu" in tokens:
        return True
    if "massachusetts institute of technology" in u or "mit" in tokens:
        return True

    return False

def fmt_avg(x):
    return "N/A" if x is None else f"{x:.2f}"


def build_results():
    conn = get_conn()
    cur = conn.cursor()

    results = []

    # Q1
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term = %s;
    """, ("Fall 2026",))
    count_fall_2026 = cur.fetchone()[0]
    results.append({
        "question": "How many entries do you have in your database who have applied for Fall 2026?",
        "answer": f"Applicant count: {count_fall_2026}"
    })
    
    
    
    # Q2: % International (not American or Other), to two decimals
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term = %s;
    """, ("Fall 2026",))
    total_fall_2026 = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term = %s
          AND us_or_international = %s;
    """, ("Fall 2026", "International"))
    intl_fall_2026 = cur.fetchone()[0]

    percent_international = 0.0
    if total_fall_2026 > 0:
        percent_international = (intl_fall_2026 / total_fall_2026) * 100

    results.append({
        "question": "What percentage of entries are from international students (not American or Other) (to two decimal places)?",
        "answer": f"Percent International: {percent_international:.2f}%%"
    })
    
    
    
    # Q3: Average GPA, GRE, GRE-V, GRE-AW for applicants who provide those metrics
    cur.execute("SELECT AVG(gpa) FROM applicants WHERE gpa IS NOT NULL;")
    avg_gpa = cur.fetchone()[0]

    cur.execute("SELECT AVG(gre) FROM applicants WHERE gre IS NOT NULL;")
    avg_gre = cur.fetchone()[0]

    cur.execute("SELECT AVG(gre_v) FROM applicants WHERE gre_v IS NOT NULL;")
    avg_gre_v = cur.fetchone()[0]

    cur.execute("SELECT AVG(gre_aw) FROM applicants WHERE gre_aw IS NOT NULL;")
    avg_gre_aw = cur.fetchone()[0]

    results.append({
        "question": "What is the average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics?",
        "answer": (
            f"Average GPA: {fmt_avg(avg_gpa)}, "
            f"Average GRE: {fmt_avg(avg_gre)}, "
            f"Average GRE-V: {fmt_avg(avg_gre_v)}, "
            f"Average GRE-AW: {fmt_avg(avg_gre_aw)}"
        )

    })



    # Q4: Average GPA of American students in Fall 2026
    cur.execute("""
        SELECT AVG(gpa)
        FROM applicants
        WHERE term = %s
        AND LOWER(us_or_international) = 'american'
        AND gpa IS NOT NULL;
    """, ("Fall 2026",))

    avg_gpa_american = cur.fetchone()[0]

    results.append({
        "question": "What is the average GPA of American students in Fall 2026?",
        "answer": f"Average GPA (American, Fall 2026): {fmt_avg(avg_gpa_american)}"
    })



    # Q5: Percent of Fall 2026 entries that are Acceptances
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term = %s;
    """, ("Fall 2026",))
    total_fall_2026 = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term = %s
          AND LOWER(status) LIKE '%%accept%%';
    """, ("Fall 2026",))
    accepted_fall_2026 = cur.fetchone()[0]

    percent_accepted = 0.0
    if total_fall_2026 > 0:
        percent_accepted = (accepted_fall_2026 / total_fall_2026) * 100

    results.append({
        "question": "What percent of entries for Fall 2026 are Acceptances (to two decimal places)?",
        "answer": f"Percent Accepted (Fall 2026): {percent_accepted:.2f}%"

    })



    # Q6: Average GPA of Fall 2026 applicants who are Acceptances
    cur.execute("""
        SELECT AVG(gpa)
        FROM applicants
        WHERE term = %s
          AND LOWER(status) LIKE '%%accept%%'
          AND gpa IS NOT NULL;
    """, ("Fall 2026",))

    avg_gpa_accepted = cur.fetchone()[0]

    results.append({
        "question": "What is the average GPA of applicants who have applied for Fall 2026 who are Acceptances?",
        "answer": f"Average GPA (Accepted, Fall 2026): {fmt_avg(avg_gpa_accepted)}"
    })



    # Q7: JHU Masters CS applicants
    cur.execute("""
        SELECT program, degree
        FROM applicants
        WHERE LOWER(program) LIKE '%%hopkin%%'
           OR LOWER(program) LIKE '%%jhu%%';
    """)

    rows = cur.fetchall()

    q7_count = 0
    for program, degree in rows:
        if is_jhu(program) and is_cs_program(program) and is_masters_degree(degree):
            q7_count += 1

    results.append({
        "question": "How many entries are from applicants who applied to JHU for a masters degree in computer science?",
        "answer": f"JHU CS Masters applicant count: {q7_count}"
    })
    
    
    # Q8: 2026 acceptances for PhD in CS at Georgetown, MIT, Stanford, or Carnegie Mellon
    cur.execute("""
        SELECT program
        FROM applicants
        WHERE date_added >= %s AND date_added < %s
          AND LOWER(status) LIKE '%%accept%%'
          AND degree = %s;
    """, ("2026-01-01", "2027-01-01", "PhD"))

    rows = cur.fetchall()

    q8_count = 0
    for (program,) in rows:
        if is_target_university(program) and is_cs_program(program):
            q8_count += 1

    results.append({
        "question": "How many entries from 2026 are acceptances from applicants who applied to Georgetown, MIT, Stanford, or Carnegie Mellon for a PhD in computer science?",
        "answer": f"PhD CS acceptances (Georgetown, MIT, Stanford, CMU — 2026): {q8_count}"
    })


    # Q9: same as Q8 but using LLM-generated fields
    cur.execute("""
        SELECT llm_generated_university, llm_generated_program
        FROM applicants
        WHERE date_added >= %s AND date_added < %s
          AND LOWER(status) LIKE '%%accept%%'
          AND degree = %s;
    """, ("2026-01-01", "2027-01-01", "PhD"))

    rows = cur.fetchall()

    q9_count = 0
    for llm_uni, llm_prog in rows:
        if is_target_university_llm(llm_uni) and is_cs_program(llm_prog):
            q9_count += 1

    diff = q9_count - q8_count

    results.append({
        "question": "Do your numbers for Q8 change if you use LLM generated data instead of downloaded data?",
        "answer": f"Downloaded: {q8_count}, LLM: {q9_count}, Difference: {diff}"
    })



    # Q10: Average GPA by citizenship (American vs International) in Fall 2026
    cur.execute("""
        SELECT us_or_international, AVG(gpa)
        FROM applicants
        WHERE term = %s
          AND gpa IS NOT NULL
          AND us_or_international IN ('American', 'International')
        GROUP BY us_or_international
        ORDER BY us_or_international;
    """, ("Fall 2026",))

    rows = cur.fetchall()

    # Build a clean answer string
    parts = []
    for group, avg_gpa in rows:
        parts.append(f"{group}: {fmt_avg(avg_gpa)}")
    q10_answer = ", ".join(parts)

    results.append({
        "question": "Additional Q1: In Fall 2026, do American and International applicants report different average GPAs?",
        "answer": q10_answer
    })



    # Q11: Acceptance rate by degree (PhD vs Masters) in Fall 2026
    cur.execute("""
        SELECT
            degree,
            COUNT(*) FILTER (WHERE LOWER(status) LIKE '%%accept%%') AS accepted_count,
            COUNT(*) AS total_count
        FROM applicants
        WHERE term = %s
          AND degree IN ('PhD', 'Masters')
        GROUP BY degree
        ORDER BY degree;
    """, ("Fall 2026",))

    rows = cur.fetchall()

    parts = []
    for degree, accepted_count, total_count in rows:
        rate = 0.0
        if total_count:
            rate = (accepted_count / total_count) * 100
        parts.append(f"{degree}: {fmt_avg(rate)}%")
    q11_answer = ", ".join(parts)

    results.append({
        "question": "Additional Q2: In Fall 2026, how do acceptance rates differ between PhD and Masters applicants?",
        "answer": q11_answer
    })


    cur.close()
    conn.close()
    return results

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

