import pytest
import re
from src.app import create_app

@pytest.mark.analysis
def test_percentages_use_two_decimal_places():
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    resp = client.get("/analysis")
    assert resp.status_code == 200

    html = resp.data.decode("utf-8")

    # Find any percent that has a decimal point
    decimal_percents = re.findall(r"\d+\.\d+%", html)
    assert len(decimal_percents) > 0

    # Every decimal percent must have exactly 2 digits after the dot
    for p in decimal_percents:
        assert re.fullmatch(r"\d+\.\d{2}%", p)
