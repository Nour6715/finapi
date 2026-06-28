"""Tests automatiques pour l'API FinAPI — Labs 1, 2 et 3."""

from unittest.mock import MagicMock, patch

import pytest

from finapi.app import create_app


@pytest.fixture
def client():
    """Cree un client de test Flask."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Lab 1 tests ───────────────────────────────────────────────────────


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_json(client):
    response = client.get("/health")
    assert response.get_json() == {"status": "ok"}


def test_price_invalid_ticker_returns_404(client):
    response = client.get("/price/ZZZZZZZZZ")
    assert response.status_code == 404


def test_history_invalid_days_returns_400(client):
    response = client.get("/history/AAPL?days=abc")
    assert response.status_code == 400


def test_compare_missing_tickers_returns_400(client):
    response = client.get("/compare")
    assert response.status_code == 400


# ── Lab 3 tests (avec mock — ne charge PAS le vrai modele) ───────────


def make_mock_pipeline(label="positive", score=0.95):
    """Cree un faux pipeline qui renvoie toujours le meme label."""
    mock_pipe = MagicMock()
    mock_pipe.return_value = [{"label": label.upper(), "score": score}]
    return mock_pipe


def test_sentiment_endpoint_positive(client):
    """POST /sentiment avec mock renvoie positive."""
    with patch("finapi.sentiment.get_pipeline") as mock_get:
        mock_get.return_value = make_mock_pipeline("positive", 0.95)
        response = client.post(
            "/sentiment", json={"text": "Apple stock soared after earnings beat expectations."}
        )
    assert response.status_code == 200
    data = response.get_json()
    assert data["label"] == "positive"
    assert "score" in data
    assert "text_preview" in data


def test_sentiment_endpoint_missing_text_returns_400(client):
    """POST /sentiment sans texte renvoie 400."""
    response = client.post("/sentiment", json={})
    assert response.status_code == 400


def test_sentiment_batch_endpoint(client):
    """POST /sentiment/batch avec mock renvoie la bonne structure."""
    mock_pipe = MagicMock()
    mock_pipe.return_value = [
        {"label": "POSITIVE", "score": 0.92},
        {"label": "NEGATIVE", "score": 0.88},
    ]
    with patch("finapi.sentiment.get_pipeline") as mock_get:
        mock_get.return_value = mock_pipe
        response = client.post("/sentiment/batch", json={"texts": ["Good news", "Bad news"]})
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 2
    assert len(data["results"]) == 2


def test_sentiment_batch_too_many_texts_returns_400(client):
    """POST /sentiment/batch avec plus de 100 textes renvoie 400."""
    response = client.post("/sentiment/batch", json={"texts": ["text"] * 101})
    assert response.status_code == 400


def test_sentiment_batch_empty_list_returns_400(client):
    """POST /sentiment/batch avec liste vide renvoie 400."""
    response = client.post("/sentiment/batch", json={"texts": []})
    assert response.status_code == 400
