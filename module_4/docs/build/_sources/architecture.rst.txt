Architecture
============

The service has three layers:

- Web layer: ``module_4/src/flask_app.py`` handles routes and busy-state logic.
- ETL layer: ``module_4/src/scrape.py`` and ``module_4/src/load_data.py`` pull and load rows.
- Analysis layer: ``module_4/src/query_data.py`` computes summary metrics used by the UI.
