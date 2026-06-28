"""Tests de validation du endpoint /history."""


def test_invalid_days_returns_400(client):
    """days=abc doit renvoyer 400."""
    response = client.get("/history/AAPL?days=abc")
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == 400
    assert "entier" in data["error"]


def test_days_out_of_range_returns_400(client):
    """days=0 doit renvoyer 400."""
    response = client.get("/history/AAPL?days=0")
    assert response.status_code == 400


def test_days_too_large_returns_400(client):
    """days=999 doit renvoyer 400."""
    response = client.get("/history/AAPL?days=999")
    assert response.status_code == 400


def test_invalid_ticker_returns_404(client):
    """Ticker invalide doit renvoyer 404."""
    response = client.get("/price/ZZZZZZZZZ")
    assert response.status_code == 404


def test_compare_no_tickers_returns_400(client):
    """GET /compare sans parametres doit renvoyer 400."""
    response = client.get("/compare")
    assert response.status_code == 400


def test_compare_too_many_tickers_returns_400(client):
    """GET /compare avec plus de 10 tickers doit renvoyer 400."""
    tickers = ",".join([f"TICK{i}" for i in range(11)])
    response = client.get(f"/compare?tickers={tickers}")
    assert response.status_code == 400
