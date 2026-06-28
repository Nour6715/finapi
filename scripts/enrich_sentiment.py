"""Calcule le sentiment des news qui n'en ont pas encore.
Usage:
    PYTHONPATH=. python scripts/enrich_sentiment.py
"""
import logging
from finapi.db import SessionLocal
from finapi.models import NewsItem
from finapi.finapi.sentiment import analyze_batch


def main(batch_size: int = 32) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    log = logging.getLogger(__name__)

    with SessionLocal() as session:
        # Seulement les news sans sentiment (idempotent)
        rows = (
            session.query(NewsItem)
            .filter(NewsItem.sentiment_label.is_(None))
            .all()
        )
        log.info("News a enrichir : %d", len(rows))

        if not rows:
            log.info("Rien a faire — toutes les news ont deja un sentiment.")
            return 0

        for i in range(0, len(rows), batch_size):
            chunk = rows[i: i + batch_size]
            texts = [(r.title + " " + (r.summary or "")) for r in chunk]
            results = analyze_batch(texts)
            for r, res in zip(chunk, results):
                r.sentiment_label = res.label
                r.sentiment_score = res.score
            session.commit()
            log.info("Batch %d-%d traite", i, i + len(chunk))

    return len(rows)


if __name__ == "__main__":
    n = main()
    print(f"Enrichies : {n}")
    