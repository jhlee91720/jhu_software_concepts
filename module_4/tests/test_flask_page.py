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

  
  
  
  
  
@pytest.mark.buttons
def test_pull_data_ok_when_not_running():
    app = create_app()
    app.config["TESTING"] = True
    app.config["PULL_RUNNING"] = False

    client = app.test_client()
    resp = client.post("/pull-data")

    assert resp.status_code in (200, 202)
    assert resp.json == {"ok": True}

    
@pytest.mark.buttons
def test_pull_data_blocked_when_running():
    app = create_app()
    app.config["TESTING"] = True
    app.config["PULL_RUNNING"] = True

    client = app.test_client()
    resp = client.post("/pull-data")

    assert resp.status_code == 409
    assert resp.json == {"busy": True}


@pytest.mark.buttons
def test_update_analysis_blocked_when_pull_running():
    app = create_app()
    app.config["TESTING"] = True
    app.config["PULL_RUNNING"] = True

    client = app.test_client()
    resp = client.post("/update-analysis")

    assert resp.status_code == 409
    assert resp.json == {"busy": True}


