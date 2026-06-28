"""Tests du pipeline ETL — avec mock de yfinance."""

from unittest.mock import patch

import pandas as pd

from finapi.etl.prices_etl import ingest_prices


def make_mock_history():
    """Cree un faux DataFrame yfinance."""
    import pandas as pd

    dates = pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"])
    df = pd.DataFrame({"Close": [150.0, 152.5, 148.0]}, index=dates)
    df.index.name = "Date"
    return df


@patch("finapi.etl.prices_etl.yf.Ticker")
def test_ingest_prices_returns_int(mock_ticker):
    """ingest_prices doit renvoyer un entier."""
    mock_ticker.return_value.history.return_value = make_mock_history()
    result = ingest_prices("AAPL", period="5d")
    assert isinstance(result, int)


@patch("finapi.etl.prices_etl.yf.Ticker")
def test_ingest_prices_empty_returns_zero(mock_ticker):
    """ingest_prices avec historique vide doit renvoyer 0."""
    mock_ticker.return_value.history.return_value = pd.DataFrame()
    result = ingest_prices("ZZZZZ", period="5d")
    assert result == 0
