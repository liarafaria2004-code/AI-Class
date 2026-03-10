# Backend

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload
```

## Structure

- `app/main.py` FastAPI app entrypoint
- `app/models/` ORM models
- `app/routes/` API endpoints (`notes`, `query`, `health`)
- `app/services/` tagging/retrieval/LLM services
- `app/db/` DB session and metadata imports
- `alembic/` migration scripts
