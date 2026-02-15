import pytest
from src.app import create_app

@pytest.mark.web
def test_analysis_page_loads():
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client() # creates a fake browser

    resp = client.get("/analysis")
    html = resp.data.decode("utf-8")
    
    assert resp.status_code == 200
    
    assert "Analysis" in html
    assert "Pull Data" in html
    assert "Update Analysis" in html
    assert "Answer:" in html

