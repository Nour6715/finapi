"""Client pour HF Spaces : appel direct des fonctions backend (pas HTTP)."""

from sqlalchemy import func

from finapi.db import SessionLocal, init_db
from finapi.models import NewsItem, PriceRecord


def get_health() -> bool:
    return True  # toujours OK en mode embedded


def get_db_stats() -> dict:
    init_db()
    with SessionLocal() as session:
        n_p = session.query(PriceRecord).count()
        n_n = session.query(NewsItem).count()
        n_e = session.query(NewsItem).filter(NewsItem.sentiment_label.isnot(None)).count()
        tickers = sorted({t for (t,) in session.query(PriceRecord.ticker).distinct()})
    return {
        "prices_count": n_p,
        "news_count": n_n,
        "news_enriched": n_e,
        "tickers": tickers,
    }


def get_db_prices(ticker: str) -> list[dict]:
    with SessionLocal() as session:
        rows = (
            session.query(PriceRecord)
            .filter(PriceRecord.ticker == ticker.upper())
            .order_by(PriceRecord.date.desc())
            .limit(100)
            .all()
        )
    return [{"date": r.date.isoformat(), "close": r.close} for r in rows]


def get_db_news(ticker: str) -> list[dict]:
    with SessionLocal() as session:
        rows = (
            session.query(NewsItem)
            .filter(NewsItem.ticker == ticker.upper())
            .order_by(NewsItem.published_at.desc())
            .limit(20)
            .all()
        )
    return [
        {
            "published_at": r.published_at.isoformat(),
            "title": r.title,
            "publisher": r.publisher,
            "url": r.url,
            "sentiment_label": r.sentiment_label,
            "sentiment_score": r.sentiment_score,
        }
        for r in rows
    ]


def get_sentiment_summary(ticker: str) -> dict[str, int]:
    with SessionLocal() as session:
        rows = (
            session.query(NewsItem.sentiment_label, func.count(NewsItem.id))
            .filter(NewsItem.ticker == ticker.upper())
            .filter(NewsItem.sentiment_label.isnot(None))
            .group_by(NewsItem.sentiment_label)
            .all()
        )
    return {label: count for label, count in rows}
