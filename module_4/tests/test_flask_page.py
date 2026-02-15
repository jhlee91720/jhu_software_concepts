import pytest
from bs4 import BeautifulSoup


@pytest.mark.web
def test_routes_exist(app):
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/" in routes
    assert "/analysis" in routes
    assert "/pull-data" in routes
    assert "/update-analysis" in routes


@pytest.mark.web
def test_get_analysis_page_loads_and_renders_components(client):
    response = client.get("/analysis")
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")

    assert soup.find("h1").get_text(strip=True) == "Analysis"
    assert soup.find("button", string="Pull Data") is not None
    assert soup.find("button", string="Update Analysis") is not None
    assert soup.select_one('button[data-testid="pull-data-btn"]') is not None
    assert soup.select_one('button[data-testid="update-analysis-btn"]') is not None

    answer_labels = [node.get_text() for node in soup.select("p.answer")]
    assert any("Answer:" in text for text in answer_labels)
