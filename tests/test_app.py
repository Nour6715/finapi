"""Tests automatiques pour l'API FinAPI."""
import pytest
from finapi.app import create_app


@pytest.fixture
def client():
    """Cree un client de test Flask."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_returns_200(client):
    """Le endpoint /health doit renvoyer HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_json(client):
    """Le endpoint /health doit renvoyer {"status": "ok"}."""
    response = client.get("/health")
    data = response.get_json()
    assert data == {"status": "ok"}


def test_price_invalid_ticker_returns_404(client):
    """Un ticker invalide doit renvoyer HTTP 404."""
    response = client.get("/price/ZZZZZZZZZ")
    assert response.status_code == 404


def test_history_invalid_days_returns_400(client):
    """Un parametre days invalide doit renvoyer HTTP 400."""
    response = client.get("/history/AAPL?days=abc")
    assert response.status_code == 400


def test_compare_missing_tickers_returns_400(client):
    """Appel a /compare sans tickers doit renvoyer HTTP 400."""
    response = client.get("/compare")
    assert response.status_code == 400
    