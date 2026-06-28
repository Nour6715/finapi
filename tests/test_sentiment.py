"""Tests du module sentiment — avec mock de FinBERT."""

from unittest.mock import MagicMock, patch

import pytest

from finapi.sentiment import SentimentResult, analyze, analyze_batch


def make_mock_pipeline(label="positive", score=0.95):
    """Cree un faux pipeline qui renvoie toujours le meme resultat."""
    mock_pipe = MagicMock()
    mock_pipe.return_value = [{"label": label.upper(), "score": score}]
    return mock_pipe


# ── Tests analyze() ───────────────────────────────────────────────────


@patch("finapi.sentiment.get_pipeline")
def test_analyze_positive(mock_get):
    """analyze() doit renvoyer positive avec le bon score."""
    mock_get.return_value = make_mock_pipeline("positive", 0.95)
    result = analyze("Apple beats expectations")
    assert isinstance(result, SentimentResult)
    assert result.label == "positive"
    assert result.score == 0.95


@patch("finapi.sentiment.get_pipeline")
def test_analyze_negative(mock_get):
    """analyze() doit renvoyer negative."""
    mock_get.return_value = make_mock_pipeline("negative", 0.88)
    result = analyze("Tesla missed earnings significantly")
    assert result.label == "negative"
    assert result.score == 0.88


@patch("finapi.sentiment.get_pipeline")
def test_analyze_neutral(mock_get):
    """analyze() doit renvoyer neutral."""
    mock_get.return_value = make_mock_pipeline("neutral", 0.75)
    result = analyze("The Fed kept rates unchanged")
    assert result.label == "neutral"


def test_analyze_empty_raises():
    """analyze() avec texte vide doit lever ValueError."""
    with pytest.raises(ValueError):
        analyze("")


def test_analyze_whitespace_raises():
    """analyze() avec texte vide (espaces) doit lever ValueError."""
    with pytest.raises(ValueError):
        analyze("   ")


@patch("finapi.sentiment.get_pipeline")
def test_analyze_text_preview_truncated(mock_get):
    """text_preview doit etre tronque a 80 caracteres."""
    mock_get.return_value = make_mock_pipeline("positive", 0.9)
    long_text = "A" * 200
    result = analyze(long_text)
    assert len(result.text_preview) <= 83  # 80 + "..."
    assert result.text_preview.endswith("...")


# ── Tests analyze_batch() ─────────────────────────────────────────────


@patch("finapi.sentiment.get_pipeline")
def test_analyze_batch_returns_list(mock_get):
    """analyze_batch() doit renvoyer une liste."""
    mock_pipe = MagicMock()
    mock_pipe.return_value = [
        {"label": "POSITIVE", "score": 0.92},
        {"label": "NEGATIVE", "score": 0.88},
    ]
    mock_get.return_value = mock_pipe
    results = analyze_batch(["Good news", "Bad news"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_analyze_batch_empty_returns_empty():
    """analyze_batch([]) doit renvoyer []."""
    results = analyze_batch([])
    assert results == []


# ── Tests endpoints /sentiment ────────────────────────────────────────


@patch("finapi.sentiment.get_pipeline")
def test_sentiment_endpoint_200(mock_get, client):
    """POST /sentiment doit renvoyer 200."""
    mock_get.return_value = make_mock_pipeline("positive", 0.95)
    response = client.post("/sentiment", json={"text": "Apple stock soared after earnings."})
    assert response.status_code == 200
    data = response.get_json()
    assert "label" in data
    assert "score" in data
    assert "text_preview" in data


def test_sentiment_endpoint_missing_text_returns_400(client):
    """POST /sentiment sans texte doit renvoyer 400."""
    response = client.post("/sentiment", json={})
    assert response.status_code == 400


def test_sentiment_batch_empty_list_returns_400(client):
    """POST /sentiment/batch avec liste vide doit renvoyer 400."""
    response = client.post("/sentiment/batch", json={"texts": []})
    assert response.status_code == 400


def test_sentiment_batch_too_many_returns_400(client):
    """POST /sentiment/batch avec 101 textes doit renvoyer 400."""
    response = client.post("/sentiment/batch", json={"texts": ["text"] * 101})
    assert response.status_code == 400


@patch("finapi.sentiment.get_pipeline")
def test_sentiment_batch_endpoint_200(mock_get, client):
    """POST /sentiment/batch doit renvoyer 200 avec structure correcte."""
    mock_pipe = MagicMock()
    mock_pipe.return_value = [
        {"label": "POSITIVE", "score": 0.92},
        {"label": "NEGATIVE", "score": 0.88},
    ]
    mock_get.return_value = mock_pipe
    response = client.post("/sentiment/batch", json={"texts": ["Good news", "Bad news"]})
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 2
    assert len(data["results"]) == 2
