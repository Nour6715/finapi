"""Application Flask exposant les endpoints de prix."""
from flask import Flask, jsonify, request
from finapi.prices import (
    TickerNotFoundError,
    get_history,
    get_latest_price,
)


def create_app() -> Flask:
    app = Flask(__name__)

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
            return jsonify({
                "error": "Aucun ticker valide fourni",
                "code": 400,
            }), 400

        if len(ticker_list) > 10:
            return jsonify({
                "error": "Maximum 10 tickers par requete",
                "code": 400,
            }), 400

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
                errors.append({
                    "ticker": ticker,
                    "error": f"Ticker '{ticker}' introuvable",
                })
            except Exception:
                errors.append({
                    "ticker": ticker,
                    "error": "Erreur interne",
                })

        response = {
            "requested": len(ticker_list),
            "found": len(results),
            "prices": results,
        }
        if errors:
            response["errors"] = errors

        return jsonify(response), 200

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
    