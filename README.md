---
title: FinSentiment
emoji: 📈
colorFrom: blue
colorTo: yellow
sdk: streamlit
sdk_version: 1.35.0
app_file: dashboard/app.py
pinned: false
license: mit
---

# FinSentiment — API Flask + Dashboard Streamlit

![CI](https://github.com/Nour6715/finapi/actions/workflows/ci.yml/badge.svg)

Dashboard interactif d'analyse de sentiment financier avec Flask, FinBERT et Streamlit.

**URL publique:** https://huggingface.co/spaces/Wiem6715/finsentiment
**Code source:** https://github.com/Nour6715/finapi



# FinAPI — Lab 1 · Foundations Back-End

A REST API built with Flask that returns real-time stock prices using the yfinance library.

**Author:** Wiem Brini
**Course:** Coaching M1/M2 — Finance Quantitative
**Institution:** EPT

---

## Requirements

- Python >= 3.10
- Git

---

## Installation

### 1. Clone the project
```bash
git clone <your-repo-url>
cd finapi
```

### 2. Create and activate the virtual environment

**macOS / Linux (Git Bash):**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows Git Bash:**
```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Running the server

```bash
python -m finapi.app
```

The server runs at: `http://127.0.0.1:5000`

---

## Endpoints

### `GET /health`
Checks that the server is running.

```bash
curl http://localhost:5000/health
```

**Response:**
```json
{"status": "ok"}
```

---

### `GET /price/<ticker>`
Returns the latest closing price for a stock ticker.

```bash
curl http://localhost:5000/price/AAPL
```

**Response:**
```json
{
  "close": 231.41,
  "currency": "USD",
  "date": "2025-06-04",
  "ticker": "AAPL"
}
```

**Error — ticker not found (404):**
```json
{"code": 404, "error": "Ticker 'ZZZZZ' introuvable"}
```

---

### `GET /history/<ticker>?days=N`
Returns the closing price history for N trading days (1 ≤ N ≤ 365, default: 30).

```bash
curl "http://localhost:5000/history/MSFT?days=5"
```

**Response:**
```json
{
  "days_requested": 5,
  "prices": [
    {"close": 418.78, "date": "2025-05-28"},
    {"close": 424.60, "date": "2025-05-29"},
    {"close": 427.51, "date": "2025-06-02"},
    {"close": 428.15, "date": "2025-06-03"},
    {"close": 428.15, "date": "2025-06-04"}
  ],
  "ticker": "MSFT"
}
```

**Error — invalid days parameter (400):**
```json
{"code": 400, "error": "Le parametre 'days' doit etre un entier"}
```

---

## Error codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid parameter) |
| 404 | Ticker not found |
| 500 | Internal server error |

---

## Project structure

```
finapi/
├── .gitignore
├── README.md
├── requirements.txt
├── finapi/
│   ├── __init__.py
│   ├── app.py        ← Flask routes
│   └── prices.py     ← yfinance logic
└── tests/
    └── test_app.py
```
---

## Lab 2 — ETL Pipeline & Base de Données

### Installer les nouvelles dépendances
```bash
pip install sqlalchemy
pip install -r requirements.txt
```

### Initialiser la base de données
```bash
python -c "from finapi.db import init_db; init_db(); print('DB created')"
```

### Lancer le pipeline ETL
```bash
python scripts/run_etl.py AAPL MSFT GOOGL
```

### Afficher un résumé de la base
```bash
python scripts/show_db.py
```

### Nouveaux endpoints

#### Prix depuis la base (rapide, hors-ligne)
GET /db/prices/<ticker>
curl http://localhost:5000/db/prices/AAPL

#### News depuis la base
GET /db/news/<ticker>curl http://localhost:5000/db/news/AAPL

#### Statistiques des tables
GET /db/stats curl http://localhost:5000/db/stats

### Structure mise à jour
finapi/

├── .gitignore

├── README.md

├── requirements.txt

├── data/

│   └── finapi.db          ← base SQLite

├── scripts/

│   ├── run_etl.py         ← pipeline orchestrateur

│   └── show_db.py

├── finapi/

│   ├── init.py

│   ├── app.py             ← routes Flask (mis à jour)

│   ├── prices.py          ← logique yfinance

│   ├── db.py              ← engine SQLAlchemy

│   ├── models.py          ← modèles ORM + index composite

│   └── etl/

│       ├── init.py

│       ├── prices_etl.py  ← ETL prix idempotent

│       └── news_etl.py    ← ETL news avec dédoublonnage

└── tests/

└── test_app.py


cat >> README.md << 'EOF'

---

## Lab 3 — FinBERT & Analyse de Sentiment

### Installer les dépendances
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers
pip install -r requirements.txt
```

### Migration de la base (Lab 3 ajoute 2 colonnes)
```bash
rm data/finapi.db
python -c "from finapi.db import init_db; init_db()"
PYTHONPATH=. python scripts/run_etl.py AAPL MSFT GOOGL
```

### Enrichir les news avec le sentiment
```bash
PYTHONPATH=. python scripts/enrich_sentiment.py
```

### Nouveaux endpoints

#### Sentiment d'un texte unique
POST /sentiment

curl -X POST http://localhost:5000/sentiment

-H "Content-Type: application/json"

-d '{"text": "Apple beat earnings expectations."}'

#### Sentiment batch (max 100 textes)

POST /sentiment/batch

curl -X POST http://localhost:5000/sentiment/batch

-H "Content-Type: application/json"

-d '{"texts": ["Good news", "Bad news"]}'

#### Résumé des sentiments par ticker

GET /db/sentiment-summary/<ticker>

curl http://localhost:5000/db/sentiment-summary/AAPL

#### Benchmark batch vs unitaire (bonus)

POST /sentiment/benchmark

curl -X POST http://localhost:5000/sentiment/benchmark

-H "Content-Type: application/json"

-d '{"texts": ["text1", "text2", ...]}'

### Lancer les tests
```bash
python -m pytest tests/ -v
```
EOF

## Lab 4 — Dashboard Streamlit

### Installer les dépendances
```bash
pip install streamlit plotly requests
pip install -r requirements.txt
```

### Lancer le dashboard (2 terminaux nécessaires)

Terminal 1 — API Flask:
```bash
python -m finapi.app
```

Terminal 2 — Dashboard:
```bash
streamlit run dashboard/app.py
```

Ouvre http://localhost:8501 dans ton navigateur.

### Fonctionnalités
- Sélection de ticker dynamique
- Slider de période (7j / 1mo / 3mo / 6mo / 1an)
- Graphique ligne ou chandelier (OHLC)
- 4 métriques: prix, date, news, % sentiment positif
- Pie chart de distribution des sentiments
- Liste des news colorées par sentiment
- 3 onglets: Vue d'ensemble / News détaillées / Stats
- Bouton refresh manuel
- Mode sombre configurable

### Structure du dashboard

dashboard/

├── init.py

├── app.py          ← page principale

├── api_client.py   ← appels HTTP à Flask

└── charts.py       ← graphiques Plotly

EOF
