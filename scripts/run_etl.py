"""Script principal d'ingestion.
Usage:
    python scripts/run_etl.py AAPL MSFT GOOGL
"""
import logging
import sys
from finapi.db import init_db
from finapi.etl.prices_etl import ingest_prices
from finapi.etl.news_etl import ingest_news


def main(tickers: list[str]) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    init_db()
    for t in tickers:
        ingest_prices(t, period="1mo")
        ingest_news(t)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_etl.py TICKER1 [TICKER2 ...]")
        sys.exit(1)
    main(sys.argv[1:])
