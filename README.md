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
