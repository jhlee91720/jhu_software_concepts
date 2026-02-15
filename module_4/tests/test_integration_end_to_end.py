import pytest

from src.flask_app import create_app
from src.load_data import insert_rows
from src.query_data import build_analysis
from tests.fakes import FakeConn, sample_row


@pytest.mark.integration
def test_end_to_end_pull_update_render_flow():
    conn = FakeConn()
    scraper_rows = [
        sample_row("a", status="Accepted", citizenship="International"),
        sample_row("b", status="Rejected", citizenship="American"),
        sample_row("c", status="Accepted", citizenship="International"),
    ]

    app = create_app(
        conn_factory=lambda: conn,
        scraper=lambda: scraper_rows,
        loader=insert_rows,
        query_builder=build_analysis,
    )
    app.config["TESTING"] = True
    client = app.test_client()

    pull = client.post("/pull-data")
    assert pull.status_code == 200
    assert len(conn.rows) == 3

    update = client.post("/update-analysis")
    assert update.status_code == 200

    page = client.get("/analysis")
    html = page.get_data(as_text=True)
    assert page.status_code == 200
    assert "Analysis" in html
    assert "Answer:" in html
    assert "66.67%" in html


@pytest.mark.integration
def test_multiple_pulls_with_overlap_stay_consistent_with_uniqueness_policy():
    conn = FakeConn()

    pulls = [
        [sample_row("1"), sample_row("2")],
        [sample_row("2"), sample_row("3")],
    ]
    state = {"idx": 0}

    def scraper():
        data = pulls[state["idx"]]
        state["idx"] = min(state["idx"] + 1, len(pulls) - 1)
        return data

    app = create_app(
        conn_factory=lambda: conn,
        scraper=scraper,
        loader=insert_rows,
        query_builder=build_analysis,
    )
    app.config["TESTING"] = True
    client = app.test_client()

    assert client.post("/pull-data").status_code == 200
    assert client.post("/pull-data").status_code == 200
    assert len(conn.rows) == 3

    html = client.get("/analysis").get_data(as_text=True)
    assert "Applicant count: 3" in html
