"""Flask application for GradCafe analysis and ETL controls."""

import os

import psycopg
from flask import Flask, current_app, jsonify, render_template

from src import load_data, query_data, scrape


def _default_conn_factory():
    database_url = os.getenv("DATABASE_URL", "dbname=gradcafe")
    return psycopg.connect(database_url)


def _close_quietly(conn):
    if conn is None:
        return
    try:
        conn.close()
    except Exception:
        pass


def _refresh_analysis(conn_factory, query_builder):
    conn = None
    try:
        conn = conn_factory()
        load_data.create_table(conn)
        return query_builder(conn)
    finally:
        _close_quietly(conn)


def create_app(conn_factory=None, scraper=None, loader=None, query_builder=None):
    app = Flask(__name__, template_folder="templates")

    conn_factory = conn_factory or _default_conn_factory
    scraper = scraper or scrape.scrape_rows
    loader = loader or load_data.insert_rows
    query_builder = query_builder or query_data.build_analysis

    app.config["PULL_IN_PROGRESS"] = False
    app.config["ANALYSIS_RESULTS"] = []

    @app.get("/")
    @app.get("/analysis")
    def analysis():
        if not current_app.config["ANALYSIS_RESULTS"]:
            current_app.config["ANALYSIS_RESULTS"] = _refresh_analysis(conn_factory, query_builder)
        return render_template("analysis.html", results=current_app.config["ANALYSIS_RESULTS"])

    @app.post("/pull-data")
    def pull_data():
        if current_app.config["PULL_IN_PROGRESS"]:
            return jsonify({"ok": False, "busy": True, "message": "Pull already running"}), 409

        current_app.config["PULL_IN_PROGRESS"] = True
        conn = None
        try:
            conn = conn_factory()
            load_data.create_table(conn)
            rows = scraper()
            inserted = loader(conn, rows)
            current_app.config["ANALYSIS_RESULTS"] = query_builder(conn)
            return jsonify({"ok": True, "busy": False, "inserted": inserted, "message": "Pull complete"}), 200
        except Exception as exc:
            return jsonify({"ok": False, "busy": False, "message": f"Pull failed: {exc}"}), 500
        finally:
            _close_quietly(conn)
            current_app.config["PULL_IN_PROGRESS"] = False

    @app.post("/update-analysis")
    def update_analysis():
        if current_app.config["PULL_IN_PROGRESS"]:
            return jsonify({"ok": False, "busy": True, "message": "Update blocked while pull is running"}), 409

        conn = None
        try:
            conn = conn_factory()
            load_data.create_table(conn)
            current_app.config["ANALYSIS_RESULTS"] = query_builder(conn)
            return jsonify({"ok": True, "busy": False, "message": "Analysis updated"}), 200
        except Exception as exc:
            return jsonify({"ok": False, "busy": False, "message": f"Update failed: {exc}"}), 500
        finally:
            _close_quietly(conn)

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True)
