"""Acces aux donnees de marche via yfinance."""
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
import yfinance as yf


class TickerNotFoundError(Exception):
    """Levee lorsqu'aucune donnee n'est trouvee."""


@dataclass
class LatestPrice:
    ticker: str
    date: date
    close: float
    currency: str


@dataclass
class PricePoint:
    date: date
    close: float


@lru_cache(maxsize=128)
def _fetch_history(ticker: str, period: str):
    """
    Fetches raw history from yfinance. Cached to avoid redundant calls.
    Returns a list of (date, close) tuples (tuples are hashable/cacheable).
    """
    yf_ticker = yf.Ticker(ticker)
    history = yf_ticker.history(period=period, auto_adjust=False)
    if history.empty:
        raise TickerNotFoundError(f"Ticker '{ticker}' introuvable")
    return [
        (ts.date(), round(float(close), 2))
        for ts, close in history["Close"].items()
    ]


@lru_cache(maxsize=128)
def _fetch_currency(ticker: str) -> str:
    """Fetches currency for a ticker. Cached."""
    try:
        yf_ticker = yf.Ticker(ticker)
        return (yf_ticker.info.get("currency", "USD") or "USD").upper()
    except Exception:
        return "USD"


def get_latest_price(ticker: str) -> LatestPrice:
    """Renvoie le dernier prix de cloture pour 'ticker'."""
    rows = _fetch_history(ticker.upper(), "5d")
    last_date, last_close = rows[-1]
    currency = _fetch_currency(ticker.upper())
    return LatestPrice(
        ticker=ticker.upper(),
        date=last_date,
        close=last_close,
        currency=currency,
    )


def get_history(ticker: str, days: int) -> list[PricePoint]:
    """Renvoie l'historique des cours de cloture sur N jours."""
    rows = _fetch_history(ticker.upper(), f"{max(days, 1)}d")
    return [PricePoint(date=d, close=c) for d, c in rows]
