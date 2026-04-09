# TrustLayer — Behavioral Credit Scoring API

A production-style FastAPI backend that computes a **Trust Score (0–1000)** from a user's digital transaction behavior. Designed for gig economy workers who lack traditional credit history but have rich UPI/digital payment data.

---

## Project Structure

```
trustlayer/
├── app/
│   ├── main.py              # FastAPI app factory + lifespan hooks
│   ├── auth.py              # API key authentication middleware
│   ├── database.py          # PostgreSQL + in-memory fallback
│   └── config.py            # Settings via environment variables
│
├── routes/
│   ├── transactions.py      # POST /upload-transactions
│   ├── scoring.py           # GET  /get-score
│   └── simulation.py        # POST /simulate
│
├── services/
│   ├── feature_engineering.py  # Behavioral feature extraction
│   ├── scoring_engine.py        # Trust Score computation
│   └── simulation_engine.py     # Hypothetical score simulator
│
├── models/
│   ├── transaction_model.py  # Pydantic input schemas
│   └── response_model.py     # Pydantic output schemas
│
├── storage/
│   └── memory_store.py       # In-memory fallback store
│
├── sample_data/
│   └── demo_transactions.json
│
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone and navigate

```bash
git clone <repo-url>
cd trustlayer
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment (optional)

Create a `.env` file in the project root:

```env
# Required in production — change this value
API_KEY=your-secure-api-key-here

# Optional: set to enable PostgreSQL persistence
# Leave blank to use in-memory storage (default)
DATABASE_URL=postgresql://user:password@localhost:5432/trustlayer

DEBUG=false
```

If no `.env` file is provided, the system uses sensible defaults and falls back to in-memory storage.

---

## Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be live at: `http://localhost:8000`

Interactive documentation: `http://localhost:8000/docs`

---

## API Reference

All endpoints (except `/health`) require the header:

```
X-API-KEY: trustlayer-dev-key-change-in-production
```

---

### POST /upload-transactions

Upload a batch of financial transactions for a user.

**Request:**

```bash
curl -X POST http://localhost:8000/upload-transactions \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: trustlayer-dev-key-change-in-production" \
  -d @sample_data/demo_transactions.json
```

**Response:**

```json
{
  "message": "Transactions stored successfully.",
  "user_id": "gig_worker_001",
  "transactions_stored": 34
}
```

---

### GET /get-score

Retrieve the Trust Score for a user.

**Request:**

```bash
curl -X GET "http://localhost:8000/get-score?user_id=gig_worker_001" \
  -H "X-API-KEY: trustlayer-dev-key-change-in-production"
```

**Response:**

```json
{
  "trust_score": 742,
  "risk_level": "low",
  "features": {
    "income_stability": 0.042,
    "spending_consistency": 0.089,
    "savings_ratio": 0.312,
    "transaction_frequency": 5.67,
    "avg_monthly_income": 19583.33,
    "avg_monthly_spending": 13466.67
  },
  "explanation": [
    "Stable and consistent monthly income.",
    "Consistent spending behavior across months.",
    "Consistent savings behavior — strong financial buffer.",
    "Active transaction history provides strong scoring confidence."
  ]
}
```

---

### POST /simulate

Simulate the effect of behavioral changes on the Trust Score.

**Request:**

```bash
curl -X POST http://localhost:8000/simulate \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: trustlayer-dev-key-change-in-production" \
  -d '{
    "user_id": "gig_worker_001",
    "increase_savings": 2000,
    "reduce_spending_percent": 10
  }'
```

**Response:**

```json
{
  "trust_score": 798,
  "risk_level": "low",
  "features": { ... },
  "explanation": [ ... ],
  "original_score": 742,
  "score_delta": 56
}
```

---

### GET /health

Liveness probe — no authentication required.

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "app": "TrustLayer",
  "version": "1.0.0"
}
```

---

## Scoring Logic

| Feature               | Weight | Description                                  |
|-----------------------|--------|----------------------------------------------|
| Income stability      | 30%    | Coefficient of variation of monthly income   |
| Savings ratio         | 30%    | Net savings as a fraction of total income    |
| Spending consistency  | 20%    | Coefficient of variation of monthly spending |
| Transaction frequency | 20%    | Average transactions per month               |

**Risk classification:**

| Trust Score | Risk Level |
|-------------|------------|
| 700 – 1000  | Low        |
| 400 – 699   | Medium     |
| 0 – 399     | High       |

---

## Storage Backends

| Mode          | When active                              | Persistence     |
|---------------|------------------------------------------|-----------------|
| In-memory     | No `DATABASE_URL` set (default)          | Lost on restart |
| PostgreSQL    | `DATABASE_URL` set in environment        | Persistent      |

The system auto-detects which backend to use at startup — no code changes required.

---

## Error Responses

All errors return structured JSON:

```json
{
  "detail": "No transaction history found for user 'xyz'."
}
```

| Status | Meaning                         |
|--------|---------------------------------|
| 401    | Missing X-API-KEY header        |
| 403    | Invalid API key                 |
| 404    | User not found / no data        |
| 422    | Validation error in request body|
| 500    | Internal server error           |
