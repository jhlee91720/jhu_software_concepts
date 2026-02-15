import json

import pytest

from src import clean
from src import create_table as create_table_module
from src import flask_app
from src.load_data import insert_rows, load_jsonl, read_jsonl
from src.scrape import scrape_rows
from tests.fakes import FakeConn, sample_row


@pytest.mark.analysis
def test_clean_helpers_cover_branches():
    assert clean.clean_text(None) is None
    assert clean.clean_text("a\x00b") == "ab"

    assert clean.to_float(None) is None
    assert clean.to_float(3) == 3.0
    assert clean.to_float(" GPA: 3.75 ") == 3.75
    assert clean.to_float("abc") is None
    assert clean.to_float("1.2.3") is None

    assert clean.normalize_text(None) == ""
    assert clean.normalize_text("Comp-Sci (M.S.)") == "comp sci m s"


@pytest.mark.db
def test_load_jsonl_and_skip_invalid_required_fields(tmp_path):
    conn = FakeConn()

    path = tmp_path / "sample.jsonl"
    valid = sample_row("jsonl-ok")
    invalid = sample_row("jsonl-bad")
    invalid["program"] = None

    path.write_text("\n".join([json.dumps(valid), "", json.dumps(invalid)]), encoding="utf-8")

    parsed = read_jsonl(path)
    assert len(parsed) == 2

    inserted = load_jsonl(conn, path)
    assert inserted == 1
    assert len(conn.rows) == 1


@pytest.mark.db
def test_insert_rows_handles_cursor_without_rowcount():
    class CursorWithoutRowcount:
        def execute(self, _sql, _params=None):
            return None

        def close(self):
            return None

    class ConnWithoutRowcount:
        def __init__(self):
            self.commits = 0

        def cursor(self):
            return CursorWithoutRowcount()

        def commit(self):
            self.commits += 1

    conn = ConnWithoutRowcount()
    inserted = insert_rows(conn, [sample_row("no-rowcount")])
    assert inserted == 0
    assert conn.commits == 1


@pytest.mark.integration
def test_scrape_rows_file_and_fallback_paths(tmp_path):
    path = tmp_path / "rows.jsonl"
    path.write_text(json.dumps(sample_row("from-file")) + "\n", encoding="utf-8")

    rows = scrape_rows(sample_path=str(path), limit=1)
    assert len(rows) == 1
    assert rows[0]["url"].endswith("from-file")

    fallback = scrape_rows(sample_path=str(tmp_path / "missing.jsonl"), limit=1)
    assert len(fallback) == 1
    assert fallback[0]["program"]


@pytest.mark.buttons
def test_flask_internal_helpers_and_error_paths(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    monkeypatch.setattr(flask_app.psycopg, "connect", lambda url: url)
    assert flask_app._default_conn_factory() == "postgresql://example"

    flask_app._close_quietly(None)

    class BoomClose:
        def close(self):
            raise RuntimeError("boom")

    flask_app._close_quietly(BoomClose())

    conn = FakeConn()
    app_pull_fail = flask_app.create_app(
        conn_factory=lambda: conn,
        scraper=lambda: [sample_row("err")],
        loader=lambda _conn, _rows: (_ for _ in ()).throw(RuntimeError("load failed")),
        query_builder=lambda _conn: [],
    )
    app_pull_fail.config["TESTING"] = True
    pull_resp = app_pull_fail.test_client().post("/pull-data")
    assert pull_resp.status_code == 500
    assert app_pull_fail.config["PULL_IN_PROGRESS"] is False

    app_update_fail = flask_app.create_app(
        conn_factory=lambda: conn,
        scraper=lambda: [],
        loader=lambda _conn, _rows: 0,
        query_builder=lambda _conn: (_ for _ in ()).throw(RuntimeError("query failed")),
    )
    app_update_fail.config["TESTING"] = True
    update_resp = app_update_fail.test_client().post("/update-analysis")
    assert update_resp.status_code == 500


@pytest.mark.db
def test_create_table_main_invokes_connect_and_create(monkeypatch):
    calls = {"url": None, "created": False, "closed": False}

    class Conn:
        def close(self):
            calls["closed"] = True

    def fake_connect(url):
        calls["url"] = url
        return Conn()

    def fake_create_table(_conn):
        calls["created"] = True

    monkeypatch.setenv("DATABASE_URL", "postgresql://unit-test")
    monkeypatch.setattr(create_table_module.psycopg, "connect", fake_connect)
    monkeypatch.setattr(create_table_module, "create_table", fake_create_table)

    create_table_module.main()

    assert calls["url"] == "postgresql://unit-test"
    assert calls["created"] is True
    assert calls["closed"] is True
