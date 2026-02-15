1. Name:
    Joo Hyun Lee (jlee887)

2. Module Info:
    Module 4: Pytest Test Suite, CI, and Sphinx Documentation

3. Approach:

    A. Project Structure
        - Created module_4 with the required layout:
          * src/ for Flask + ETL/DB/analysis code
          * tests/ for all pytest files
          * docs/ for Sphinx source and generated HTML
        - Kept code modular so tests can inject fake scraper/loader/query behavior.

    B. Flask App and Endpoints
        - Implemented Flask app factory create_app(...) in src/flask_app.py.
        - Exposed routes:
          * GET /analysis (and /)
          * POST /pull-data
          * POST /update-analysis
        - Added busy-state gating for pull/update behavior.
        - Endpoint responses include status payload fields such as ok/busy.

    C. Analysis Rendering / Formatting
        - Analysis template renders required components:
          * page title/text "Analysis"
          * "Pull Data" and "Update Analysis" buttons
          * answer rows labeled with "Answer:"
        - Percentages are formatted with two decimals (e.g., 66.67%).
        - Added stable UI selectors:
          * data-testid="pull-data-btn"
          * data-testid="update-analysis-btn"

    D. Database and Loading
        - Implemented required schema creation in src/load_data.py and src/create_table.py.
        - Implemented insert logic with required non-null fields and idempotency policy.
        - Used ON CONFLICT (url) DO NOTHING to prevent duplicate rows on repeated pulls.

    E. Pytest Suite
        - Added tests for all required categories:
          * test_flask_page.py (page/routes/components)
          * test_buttons.py (button endpoints + busy-state)
          * test_analysis_format.py (Answer label + two-decimal percentage)
          * test_db_insert.py (insert/idempotency/query keys)
          * test_integration_end_to_end.py (pull -> update -> render)
        - Added deterministic fakes/fixtures in tests/fakes.py and tests/conftest.py.
        - All tests are marked with one or more required markers:
          web, buttons, analysis, db, integration.

    F. Coverage and CI
        - Configured pytest-cov in pytest.ini with fail-under=100.
        - Verified command:
          pytest -m "web or buttons or analysis or db or integration"
        - Coverage result is 100% and saved in coverage_summary.txt.
        - Added GitHub Actions workflow (tests.yml) with Postgres service and pytest run.

    G. Sphinx Documentation
        - Added Sphinx documentation under docs/source:
          * setup.rst
          * architecture.rst
          * api.rst
          * testing.rst
        - Enabled autodoc for key modules:
          scrape.py, clean.py, load_data.py, query_data.py, flask_app.py.
        - Built HTML docs under docs/build.

4. Files Included:
        - src/ (clean.py, scrape.py, load_data.py, query_data.py, flask_app.py, create_table.py, templates/)
        - tests/ (all required pytest files)
        - pytest.ini
        - requirements.txt
        - coverage_summary.txt
        - docs/source/ and docs/build/
        - .github/workflows/tests.yml
        - actions_success.png

5. Notes:
        - Test suite is designed to be deterministic and does not depend on live network scraping.
        - CI import/path issues were resolved in workflow by using module execution for schema creation
          and PYTHONPATH for pytest collection.
        - For deliverables, workflow file is present at both:
          * .github/workflows/tests.yml
          * module_4/.github/workflows/tests.yml

6. Read the Docs link:
    https://jhu-software-concepts-jlee887.readthedocs.io/en/latest/index.html
