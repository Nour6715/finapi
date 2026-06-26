"""Application Flask exposant les endpoints de prix."""
from flask import Flask, jsonify, request
from finapi.prices import (
    TickerNotFoundError,
    get_history,
    get_latest_price,
)
from finapi.db import SessionLocal, init_db
from finapi.models import PriceRecord, NewsItem


def create_app() -> Flask:
    app = Flask(__name__)
    init_db()  # Cree les tables au demarrage si elles n'existent pas

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.get("/price/<ticker>")
    def price(ticker: str):
        try:
            latest = get_latest_price(ticker)
        except TickerNotFoundError as e:
            return jsonify({"error": str(e), "code": 404}), 404
        except Exception:
            return jsonify({"error": "Erreur interne", "code": 500}), 500
        return jsonify({
            "ticker": latest.ticker,
            "date": latest.date.isoformat(),
            "close": latest.close,
            "currency": latest.currency,
        })

    @app.get("/history/<ticker>")
    def history(ticker: str):
        raw_days = request.args.get("days", "30")
        try:
            days = int(raw_days)
        except ValueError:
            return jsonify({
                "error": "Le parametre 'days' doit etre un entier",
                "code": 400,
            }), 400
        if not 1 <= days <= 365:
            return jsonify({
                "error": "Le parametre 'days' doit etre entre 1 et 365",
                "code": 400,
            }), 400
        try:
            points = get_history(ticker, days)
        except TickerNotFoundError as e:
            return jsonify({"error": str(e), "code": 404}), 404
        except Exception:
            return jsonify({"error": "Erreur interne", "code": 500}), 500
        return jsonify({
            "ticker": ticker.upper(),
            "days_requested": days,
            "prices": [
                {"date": p.date.isoformat(), "close": p.close}
                for p in points
            ],
        })

    @app.get("/compare")
    def compare():
        raw = request.args.get("tickers", "")
        if not raw:
            return jsonify({
                "error": "Le parametre 'tickers' est requis. Ex: ?tickers=AAPL,MSFT",
                "code": 400,
            }), 400
        ticker_list = [t.strip().upper() for t in raw.split(",") if t.strip()]
        if len(ticker_list) == 0:
            return jsonify({"error": "Aucun ticker valide fourni", "code": 400}), 400
        if len(ticker_list) > 10:
            return jsonify({"error": "Maximum 10 tickers par requete", "code": 400}), 400
        results = []
        errors = []
        for ticker in ticker_list:
            try:
                latest = get_latest_price(ticker)
                results.append({
                    "ticker": latest.ticker,
                    "date": latest.date.isoformat(),
                    "close": latest.close,
                    "currency": latest.currency,
                })
            except TickerNotFoundError:
                errors.append({"ticker": ticker, "error": f"Ticker '{ticker}' introuvable"})
            except Exception:
                errors.append({"ticker": ticker, "error": "Erreur interne"})
        response = {"requested": len(ticker_list), "found": len(results), "prices": results}
        if errors:
            response["errors"] = errors
        return jsonify(response), 200

    @app.get("/db/prices/<ticker>")
    def db_prices(ticker: str):
        """Lit les prix stockes pour un ticker (les plus recents en premier)."""
        with SessionLocal() as session:
            rows = (
                session.query(PriceRecord)
                .filter(PriceRecord.ticker == ticker.upper())
                .order_by(PriceRecord.date.desc())
                .limit(100)
                .all()
            )
        return jsonify({
            "ticker": ticker.upper(),
            "count": len(rows),
            "prices": [
                {"date": r.date.isoformat(), "close": r.close}
                for r in rows
            ],
        })

    @app.get("/db/news/<ticker>")
    def db_news(ticker: str):
        """Lit les news stockees pour un ticker."""
        with SessionLocal() as session:
            rows = (
                session.query(NewsItem)
                .filter(NewsItem.ticker == ticker.upper())
                .order_by(NewsItem.published_at.desc())
                .limit(20)
                .all()
            )
        return jsonify({
            "ticker": ticker.upper(),
            "count": len(rows),
            "news": [
                {
                    "published_at": r.published_at.isoformat(),
                    "title": r.title,
                    "publisher": r.publisher,
                    "url": r.url,
                }
                for r in rows
            ],
        })

    # ── BONUS: /db/stats ──────────────────────────────────────────────
    @app.get("/db/stats")
    def db_stats():
        """Renvoie le nombre total de lignes par table."""
        with SessionLocal() as session:
            prices_count = session.query(PriceRecord).count()
            news_count = session.query(NewsItem).count()
        return jsonify({
            "tables": {
                "prices": {"total_rows": prices_count},
                "news": {"total_rows": news_count},
            }
        })

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)

