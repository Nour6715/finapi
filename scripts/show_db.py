"""Affiche un resume textuel de la base de donnees.
Usage:
    python scripts/show_db.py
"""

from finapi.db import SessionLocal, init_db
from finapi.models import NewsItem, PriceRecord


def show_summary() -> None:
    init_db()
    with SessionLocal() as session:
        # Résumé table prices
        prices_total = session.query(PriceRecord).count()
        print("=" * 50)
        print(f"TABLE prices : {prices_total} lignes au total")
        print("-" * 50)

        tickers_prices = session.query(PriceRecord.ticker).distinct().all()
        for (ticker,) in tickers_prices:
            count = session.query(PriceRecord).filter(PriceRecord.ticker == ticker).count()
            latest = (
                session.query(PriceRecord)
                .filter(PriceRecord.ticker == ticker)
                .order_by(PriceRecord.date.desc())
                .first()
            )
            print(
                f"  {ticker:10s} → {count:3d} jours | dernier: {latest.date} | close: {latest.close}"
            )

        # Résumé table news
        news_total = session.query(NewsItem).count()
        print("=" * 50)
        print(f"TABLE news   : {news_total} articles au total")
        print("-" * 50)

        tickers_news = session.query(NewsItem.ticker).distinct().all()
        for (ticker,) in tickers_news:
            count = session.query(NewsItem).filter(NewsItem.ticker == ticker).count()
            latest = (
                session.query(NewsItem)
                .filter(NewsItem.ticker == ticker)
                .order_by(NewsItem.published_at.desc())
                .first()
            )
            print(
                f"  {ticker:10s} → {count:3d} articles | dernier: {latest.published_at.strftime('%Y-%m-%d %H:%M')} | {latest.title[:50]}..."
            )
        print("=" * 50)


if __name__ == "__main__":
    show_summary()
