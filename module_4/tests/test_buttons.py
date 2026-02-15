import pytest

from src.flask_app import create_app
from src.load_data import insert_rows
from src.query_data import build_analysis
from tests.fakes import FakeConn, sample_row


@pytest.mark.buttons
def test_post_pull_data_returns_200_and_loads_rows():
    conn = FakeConn()
    rows = [sample_row("1"), sample_row("2", status="Rejected")]

    app = create_app(
        conn_factory=lambda: conn,
        scraper=lambda: rows,
        loader=insert_rows,
        query_builder=build_analysis,
    )
    app.config["TESTING"] = True

    response = app.test_client().post("/pull-data")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["busy"] is False
    assert len(conn.rows) == 2


@pytest.mark.buttons
def test_post_update_analysis_returns_200_when_not_busy(app):
    response = app.test_client().post("/update-analysis")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["busy"] is False


@pytest.mark.buttons
def test_update_analysis_returns_409_and_does_nothing_when_busy():
    conn = FakeConn()
    called = {"count": 0}

    def query_builder(_conn):
        called["count"] += 1
        return []

    app = create_app(
        conn_factory=lambda: conn,
        scraper=lambda: [],
        loader=lambda _conn, _rows: 0,
        query_builder=query_builder,
    )
    app.config["TESTING"] = True
    app.config["PULL_IN_PROGRESS"] = True

    response = app.test_client().post("/update-analysis")
    assert response.status_code == 409
    payload = response.get_json()
    assert payload["busy"] is True
    assert called["count"] == 0


@pytest.mark.buttons
def test_pull_data_returns_409_when_busy(app):
    app.config["PULL_IN_PROGRESS"] = True
    response = app.test_client().post("/pull-data")
    assert response.status_code == 409
    payload = response.get_json()
    assert payload["busy"] is True
