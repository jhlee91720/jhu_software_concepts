1. Name:
    Joo Hyun Lee (jlee887)

2. Module Info:
    Module 3: Database Queries, PostgreSQL Integration, and Flask Webpage

3. Approach:

    A. Database Setup
        - Created PostgreSQL database named "gradcafe".
        - Built applicants table using create_table.py.
        - Loaded cleaned dataset into PostgreSQL using load_data.py.
        - Data fields include both original scraped fields and LLM-generated fields.

    B. Data Loading / Cleaning
        - Used cleaned dataset from Module 2 as input.
        - Added normalization logic during querying to handle variations in program,
          university, and degree names (e.g., CS, computer science, CompSci).
        - Removed problematic characters (e.g., NULL bytes) during loading to
          avoid PostgreSQL text errors.

    C. SQL Queries (query_data.py)
        - Implemented required queries Q1–Q9 using psycopg.
        - Used SQL aggregation functions such as COUNT(), AVG(), and filtering
          conditions (WHERE clauses).
        - For cases with inconsistent naming (e.g., JHU variants), used
          normalization (LOWER() and keyword matching) instead of complex regex
          to keep queries readable and easier to maintain.

    D. Flask Web Application
        - Created a Flask app (app.py) that connects to PostgreSQL.
        - Displays query results on a single styled analysis page.
        - Uses templates:
            * base.html
            * analysis.html
        - Results are passed as structured data and rendered dynamically.

    E. Pull Data Feature (Part B)
        - Added "Pull Data" button to call Module 2 scraper using subprocess.
        - Runs module_2/scrape.py to fetch new data.
        - After completion, page redirects back to updated analysis view.

    F. Update Analysis Feature
        - Added "Update Analysis" button to refresh analysis results.
        - Prevents execution while pull data process is running.

4. Files Included:
        - load_data.py
        - query_data.py
        - app.py
        - templates/ (analysis.html, base.html)
        - limitations.pdf
        - screenshots of console output and webpage
        - requirements.txt

5. Notes:
        - Normalization approach was chosen instead of regex for Q7 to keep the
          logic simple and consistent with typical SQL filtering workflows.
        - Regex could provide more flexible matching but would increase
          complexity without significant benefit for this dataset.
