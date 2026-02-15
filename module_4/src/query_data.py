import psycopg

def main():
    conn = psycopg.connect("dbname=gradcafe")
    cur = conn.cursor()

    # Q1: How many entries applied for Fall 2026? ##################################
    cur.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE term = %s;
    """, ("Fall 2026",))

    count_fall_2026 = cur.fetchone()[0]
    print("Applicant count (Fall 2026):", count_fall_2026)
    ###############################################################################
    
    # Q2: percentage of international students?####################################
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE us_or_international = 'International') AS international_count,
            COUNT(*) AS total_count
        FROM applicants;
    """)

    international_count, total_count = cur.fetchone()

    percent_international = round((international_count / total_count) * 100, 2)

    print("Percent International:", percent_international)
    ###############################################################################

    # Q3: averages for applicants who provided each metric ########################
    cur.execute("""
        SELECT
            AVG(gpa)   FILTER (WHERE gpa   IS NOT NULL) AS avg_gpa,
            AVG(gre)   FILTER (WHERE gre   IS NOT NULL) AS avg_gre,
            AVG(gre_v) FILTER (WHERE gre_v IS NOT NULL) AS avg_gre_v,
            AVG(gre_aw)FILTER (WHERE gre_aw IS NOT NULL) AS avg_gre_aw
        FROM applicants;
    """)

    avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()

    print("Average GPA:", round(avg_gpa, 2) if avg_gpa is not None else None)
    print("Average GRE:", round(avg_gre, 2) if avg_gre is not None else None)
    print("Average GRE-V:", round(avg_gre_v, 2) if avg_gre_v is not None else None)
    print("Average GRE-AW:", round(avg_gre_aw, 2) if avg_gre_aw is not None else None)
    ###############################################################################

    # Q4: average GPA of American students in Fall 2026 ###########################
    cur.execute("""
        SELECT AVG(gpa)
        FROM applicants
        WHERE term = %s
        AND us_or_international = %s
        AND gpa IS NOT NULL;
    """, ("Fall 2026", "American"))

    avg_gpa_american_fall_2026 = cur.fetchone()[0]

    print("Average GPA (American, Fall 2026):",
          round(avg_gpa_american_fall_2026, 2) if avg_gpa_american_fall_2026 is not None else None)

    ###############################################################################
    
    # Q5: What percent of entries for Fall 2026 are Acceptances?###################
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE term = %s AND status = 'Accepted') AS accepted_count,
            COUNT(*) FILTER (WHERE term = %s) AS total_count
        FROM applicants;
    """, ("Fall 2026", "Fall 2026"))

    accepted_count_fall_2026, total_count_fall_2026 = cur.fetchone()

    percent_accepted_fall_2026 = round((accepted_count_fall_2026 / total_count_fall_2026) * 100, 2)

    print("Percent Accepted (Fall 2026):", percent_accepted_fall_2026)

    ###############################################################################
    
    # Q6: Average GPA of Fall 2026 applicants who are Acceptances #################
    cur.execute("""
        SELECT AVG(gpa)
        FROM applicants
        WHERE term = %s
        AND status = %s
        AND gpa IS NOT NULL;
    """, ("Fall 2026", "Accepted"))

    avg_gpa_accepted_fall_2026 = cur.fetchone()[0]

    print("Average GPA (Accepted, Fall 2026):",
          round(avg_gpa_accepted_fall_2026, 2) if avg_gpa_accepted_fall_2026 is not None else None)

    ###############################################################################

    # Q7: JHU CS Masters count (normalization approach) ###########################

    def normalize_text(s):
        if s is None:
            return ""
        s = str(s).lower()

        # Replace punctuation with spaces (so "c.s." -> "c s", "m.s." -> "m s")
        for ch in [",", ".", "-", "_", "/", "(", ")", "[", "]", "{", "}", ":", ";", "'", '"']:
            s = s.replace(ch, " ")

        # Collapse multiple spaces
        s = " ".join(s.split())
        return s


    def has_cs(program_norm):
        # Check phrase variants first
        if "computer science" in program_norm:
            return True
        if "computer sci" in program_norm:
            return True
        if "comp sci" in program_norm:
            return True
        if "compsci" in program_norm:
            return True

        # Token-based check for "cs" / "c s" (after punctuation removal)
        tokens = program_norm.split()

        # "cs" as a token
        if "cs" in tokens:
            return True

        # "c s" as consecutive tokens (from "c.s." or "c s")
        for i in range(len(tokens) - 1):
            if tokens[i] == "c" and tokens[i + 1] == "s":
                return True

        return False

    def has_masters(degree_norm):
        # Normalize common variants into tokens
        d = degree_norm

        if "master" in d:   # covers "master" and "masters" and "master's"
            return True

        tokens = d.split()

        # "ms" or "msc" as tokens
        if "ms" in tokens or "msc" in tokens:
            return True

        # "m s" or "m sc" (from "m.s." or "m.sc." or "m sc")
        for i in range(len(tokens) - 1):
            if tokens[i] == "m" and tokens[i + 1] == "s":
                return True
            if tokens[i] == "m" and tokens[i + 1] == "sc":
                return True

        return False

    def is_jhu_cs_masters(program, degree):
        p = normalize_text(program)
        d = normalize_text(degree)

        # University variants: "jhu" OR "hopkin" root fragment catches hopkin/hopkins
        is_jhu = ("jhu" in p) or ("hopkin" in p)

        is_cs = has_cs(p)
        is_masters = has_masters(d)

        return is_jhu and is_cs and is_masters


    # Pull candidates only (fast): anything that looks like JHU/Hopkins
    cur.execute("""
        SELECT program, degree
        FROM applicants
        WHERE program ILIKE %s OR program ILIKE %s;
    """, ("%hopkin%", "%jhu%"))

    rows = cur.fetchall()

    q7_count = 0
    for program, degree in rows:
        if is_jhu_cs_masters(program, degree):
            q7_count += 1

    print("JHU CS Masters applicant count (normalize):", q7_count)

    ###############################################################################
    
    # Q8: 2026 acceptances for PhD in CS at Georgetown, MIT, Stanford, or Carnegie Mellon

    def is_target_university(program_norm):
        return (
            "georgetown" in program_norm or
            "massachusetts institute of technology" in program_norm or
            " mit " in (" " + program_norm + " ") or
            "stanford" in program_norm or
            "carnegie mellon" in program_norm or
            " cmu " in (" " + program_norm + " ")
        )

    def is_cs(program_norm):
        if "computer science" in program_norm:
            return True
        if "computer sci" in program_norm:
            return True
        if "comp sci" in program_norm:
            return True
        if "compsci" in program_norm:
            return True

        tokens = program_norm.split()
        if "cs" in tokens:
            return True
        for i in range(len(tokens) - 1):
            if tokens[i] == "c" and tokens[i + 1] == "s":
                return True
        return False

    cur.execute("""
        SELECT program, degree, status, date_added
        FROM applicants
        WHERE date_added >= %s AND date_added < %s
        AND status = %s
        AND degree = %s;
    """, ("2026-01-01", "2027-01-01", "Accepted", "PhD"))

    rows = cur.fetchall()

    q8_count = 0
    for program, degree, status, date_added in rows:
        p_norm = normalize_text(program)
        if is_target_university(p_norm) and is_cs(p_norm):
            q8_count += 1
    
    print("PhD CS acceptances (Georgetown, MIT, Stanford, CMU — 2026):", q8_count)

    ###############################################################################
    
    # Q9: Does Q8 change if we use LLM-generated fields? ##########################

    def is_target_university_llm(university_norm):
        # LLM field should be clean university name
        return (
            "georgetown" in university_norm or
            "stanford" in university_norm or
            "carnegie mellon" in university_norm or
            "cmu" == university_norm or
            "massachusetts institute of technology" in university_norm or
            "mit" == university_norm
        )

    cur.execute("""
        SELECT llm_generated_university, llm_generated_program
        FROM applicants
        WHERE date_added >= %s AND date_added < %s
        AND status = %s
        AND degree = %s;
    """, ("2026-01-01", "2027-01-01", "Accepted", "PhD"))

    rows = cur.fetchall()

    q9_count = 0
    for llm_uni, llm_prog in rows:
        uni_norm = normalize_text(llm_uni)
        prog_norm = normalize_text(llm_prog)

        if is_target_university_llm(uni_norm) and has_cs(prog_norm):
            q9_count += 1

    print("PhD CS acceptances (LLM fields — 2026):", q9_count)

    ###############################################################################
    
    # Q10: In Fall 2026, average GPA by citizenship group (American vs International)
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
    print("Avg GPA by citizenship (Fall 2026):")
    for group, avg_gpa in rows:
        print(group + ":", round(avg_gpa, 2) if avg_gpa is not None else None)

    ###############################################################################
    
    # Q11: In Fall 2026, acceptance rate by degree (PhD vs Masters) ###############
    cur.execute("""
        SELECT
            degree,
            COUNT(*) FILTER (WHERE status = 'Accepted') AS accepted_count,
            COUNT(*) AS total_count
        FROM applicants
        WHERE term = %s
        AND degree IN ('PhD', 'Masters')
        GROUP BY degree
        ORDER BY degree;
    """, ("Fall 2026",))

    rows = cur.fetchall()
    print("Acceptance rate by degree (Fall 2026):")
    for degree, accepted_count, total_count in rows:
        rate = round((accepted_count / total_count) * 100, 2) if total_count else 0.0
        print(degree + ":", rate, "%")

    ###############################################################################
    
    
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
