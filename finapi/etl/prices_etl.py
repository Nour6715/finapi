"""ETL des prix : Extract via yfinance, Load dans SQLite."""
import logging
import yfinance as yf
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from finapi.db import SessionLocal
from finapi.models import PriceRecord

log = logging.getLogger(__name__)


def ingest_prices(ticker: str, period: str = "1mo") -> int:
    """Telecharge et stocke les prix. Idempotent.
    Renvoie le nombre de lignes effectivement inserees
    (les doublons sont silencieusement ignores).
    """
    log.info("ETL prices: fetching %s (period=%s)", ticker, period)
    history = yf.Ticker(ticker).history(period=period, auto_adjust=False)

    if history.empty:
        log.warning("ETL prices: aucune donnee pour %s", ticker)
        return 0

    rows = [
        {
            "ticker": ticker.upper(),
            "date": ts.date(),
            "close": round(float(close), 2),
            "currency": "USD",
        }
        for ts, close in history["Close"].items()
    ]

    with SessionLocal() as session:
        stmt = sqlite_insert(PriceRecord).values(rows)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["ticker", "date"]
        )
        result = session.execute(stmt)
        session.commit()

    inserted = result.rowcount or 0
    log.info("ETL prices: %d lignes inserees pour %s", inserted, ticker)
    return inserted
