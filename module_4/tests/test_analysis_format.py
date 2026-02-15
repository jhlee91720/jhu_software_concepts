import re

import pytest

from src.flask_app import create_app
from src.load_data import insert_rows
from src.query_data import build_analysis
from tests.fakes import FakeConn, sample_row


@pytest.mark.analysis
def test_analysis_contains_answer_labels_and_two_decimal_percentages():
    conn = FakeConn()
    insert_rows(conn, [
        sample_row("1", status="Accepted", citizenship="International"),
        sample_row("2", status="Rejected", citizenship="American"),
        sample_row("3", status="Accepted", citizenship="International"),
    ])

    app = create_app(
        conn_factory=lambda: conn,
        scraper=lambda: [],
        loader=insert_rows,
        query_builder=build_analysis,
    )
    app.config["TESTING"] = True

    response = app.test_client().get("/analysis")
    html = response.get_data(as_text=True)

    assert "Answer:" in html
    matches = re.findall(r"\d+\.\d{2}%", html)
    assert matches
