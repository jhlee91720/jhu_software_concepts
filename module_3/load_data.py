import json
import psycopg


# JSON file contains strings in GPA
# database column GPA is float
# changing string to numeric float
def to_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip()

    # keep only digits and dot
    cleaned = ""
    for ch in s:
        if ch.isdigit() or ch == ".":
            cleaned += ch

    if cleaned == "":
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None

# JSONL has a string containing NUL character. psql refuses to store that in TEXT
# cleaning text fields
def clean_text(value):
    if value is None:
        return None
    s = str(value)
    # remove NUL bytes that Postgres can't store in TEXT
    return s.replace("\x00", "")

def main():
    # #safe refresh
    # cur.execute("TRUNCATE TABLE applicants RESTART IDENTITY;")
    # conn.commit()
    
    path = "module_3/data/llm_extend_applicant_data (1).json"

    conn = psycopg.connect("dbname=gradcafe")
    cur = conn.cursor()

    inserted = 0
    skipped = 0
    
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start = 1):
            try:
                obj = json.loads(line)

                #creating a table within the db
                cur.execute("""
                    INSERT INTO applicants (
                        program,
                        comments,
                        date_added,
                        url,
                        status,
                        term,
                        us_or_international,
                        gpa,
                        gre,
                        gre_v,
                        gre_aw,
                        degree,
                        llm_generated_program,
                        llm_generated_university
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    clean_text(obj.get("program")),
                    clean_text(obj.get("comments")),
                    clean_text(obj.get("date_added")),
                    clean_text(obj.get("url")),
                    clean_text(obj.get("applicant_status")),
                    clean_text(obj.get("semester_year_start")),
                    clean_text(obj.get("citizenship")),
                    to_float(obj.get("gpa")),
                    to_float(obj.get("gre")),
                    to_float(obj.get("gre_v")),
                    to_float(obj.get("gre_aw")),
                    clean_text(obj.get("masters_or_phd")),
                    clean_text(obj.get("llm-generated-program")),
                    clean_text(obj.get("llm-generated-university")),
                ))
                
                inserted += 1
            except Exception as e:
                skipped += 1
                if skipped <= 5:
                    print ("Skipped line", i, "because:", e)
                    

    conn.commit()
    cur.close()
    conn.close()

    print("Inserted one row.")

if __name__ == "__main__":
    main()
