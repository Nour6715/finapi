"""Point d'entree HF Spaces.
Pre-remplit la DB si vide, puis lance le dashboard Streamlit.
"""

import os
import sys
from pathlib import Path

# S'assurer que le projet est dans le path
sys.path.insert(0, str(Path(__file__).parent))

from finapi.db import SessionLocal, init_db
from finapi.models import PriceRecord


def bootstrap_data() -> None:
    """Si la DB est vide, lancer un mini ETL au demarrage."""
    init_db()
    with SessionLocal() as session:
        if session.query(PriceRecord).count() > 0:
            print("DB deja remplie, bootstrap ignore.")
            return

    print("DB vide, lancement bootstrap ETL...")

    # Liste de tickers configurable via variable d'environnement (BONUS)
    tickers_env = os.getenv("TICKERS", "AAPL,MSFT,GOOGL,TSLA")
    tickers = [t.strip() for t in tickers_env.split(",")]

    from finapi.etl.news_etl import ingest_news
    from finapi.etl.prices_etl import ingest_prices
    from scripts.enrich_sentiment import main as enrich

    for t in tickers:
        print(f"Ingestion prix: {t}")
        ingest_prices(t, period="1mo")
        print(f"Ingestion news: {t}")
        ingest_news(t)

    print("Enrichissement sentiment...")
    enrich()
    print("Bootstrap termine.")


if os.getenv("BOOTSTRAP", "1") == "1":
    bootstrap_data()

# Lancer le dashboard Streamlit
exec(open(Path(__file__).parent / "dashboard" / "app.py").read())
