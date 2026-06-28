"""Tests d'integration end-to-end — demarre l'API et l'attaque via HTTP."""

import threading
import time

import pytest
import requests

from finapi.app import create_app


@pytest.fixture(scope="module")
def live_server():
    """Demarre l'API Flask dans un thread separe pour les tests e2e."""
    app = create_app()
    app.config["TESTING"] = True

    server_thread = threading.Thread(
        target=lambda: app.run(port=5099, use_reloader=False),
        daemon=True,
    )
    server_thread.start()
    time.sleep(1)  # Laisse le serveur demarrer
    yield "http://localhost:5099"


def test_e2e_health(live_server):
    """Test e2e: GET /health via HTTP reel."""
    response = requests.get(f"{live_server}/health", timeout=5)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_e2e_invalid_ticker(live_server):
    """Test e2e: ticker invalide renvoie 404 via HTTP reel."""
    response = requests.get(f"{live_server}/price/ZZZZZZZZZ", timeout=5)
    assert response.status_code == 404


def test_e2e_invalid_days(live_server):
    """Test e2e: days invalide renvoie 400 via HTTP reel."""
    response = requests.get(f"{live_server}/history/AAPL?days=abc", timeout=5)
    assert response.status_code == 400


def test_e2e_sentiment_missing_body(live_server):
    """Test e2e: POST /sentiment sans body renvoie 400."""
    response = requests.post(f"{live_server}/sentiment", json={}, timeout=5)
    assert response.status_code == 400
