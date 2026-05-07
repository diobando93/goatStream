# GoatStream

Live sports streaming aggregator. Watch live sports without hunting for working streams.

## Local development

### Prerequisites

- Python 3.11+
- Node 20+
- PostgreSQL 15+

### Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL to your local PostgreSQL instance

# Run migrations
alembic upgrade head

# Start the dev server
uvicorn app.main:app --reload
```

The API is now available at http://localhost:8000.  
Health check: `GET /health` → `{"status": "ok"}`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app is now available at http://localhost:5173.

### CI

GitHub Actions runs on every push (`ruff` lint on the backend, ESLint + Vite build on the frontend).
