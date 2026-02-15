import pytest

from src.flask_app import create_app
from src.query_data import build_analysis
from tests.fakes import FakeConn


@pytest.fixture
def fake_conn():
    return FakeConn()


@pytest.fixture
def app(fake_conn):
    app = create_app(
        conn_factory=lambda: fake_conn,
        scraper=lambda: [],
        loader=lambda _conn, _rows: 0,
        query_builder=build_analysis,
    )
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()
