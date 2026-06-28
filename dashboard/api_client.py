"""Client HTTP pour l'API Flask finapi."""
from __future__ import annotations
from typing import Any
import requests

API_BASE = "http://localhost:5000"


class APIError(Exception):
    pass


def _get(path: str, **params) -> dict[str, Any]:
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=10)
    except requests.RequestException as e:
        raise APIError(f"API injoignable : {e}") from e
    if r.status_code != 200:
        raise APIError(f"{r.status_code}: {r.text[:200]}")
    return r.json()


def get_health() -> bool:
    try:
        return _get("/health").get("status") == "ok"
    except APIError:
        return False


def get_db_prices(ticker: str) -> list[dict]:
    return _get(f"/db/prices/{ticker}").get("prices", [])


def get_db_news(ticker: str) -> list[dict]:
    return _get(f"/db/news/{ticker}").get("news", [])


def get_sentiment_summary(ticker: str) -> dict[str, int]:
    return _get(f"/db/sentiment-summary/{ticker}").get("distribution", {})


def get_db_stats() -> dict:
    return _get("/db/stats")


def get_price_history(ticker: str, period: str = "1mo") -> list[dict]:
    """BONUS: recupere l'historique sur une periode donnee via yfinance."""
    try:
        return _get(f"/history/{ticker}", days=_period_to_days(period))
    except APIError:
        return []


def _period_to_days(period: str) -> int:
    """Convertit une periode lisible en nombre de jours."""
    mapping = {
        "7d": 7,
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365,
    }
    return mapping.get(period, 30)
