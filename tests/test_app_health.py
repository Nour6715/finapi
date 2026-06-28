"""Tests du endpoint /health."""


def test_health_returns_200(client):
    """GET /health doit renvoyer HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_json(client):
    """GET /health doit renvoyer {"status": "ok"}."""
    response = client.get("/health")
    assert response.get_json() == {"status": "ok"}


def test_health_content_type_is_json(client):
    """GET /health doit renvoyer du JSON."""
    response = client.get("/health")
    assert response.content_type == "application/json"


def test_db_news_invalid_ticker_returns_empty(client):
    response = client.get("/db/news/ZZZZZZZZZ")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 0
