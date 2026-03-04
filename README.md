# inpa-data-bridge

Backend service that ingests INPA public exam data, normalizes it, stores it in PostgreSQL, and exposes REST endpoints for mobile clients.

## Stack
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Alembic
- APScheduler

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```
3. Copy environment file:
   ```bash
   cp .env.example .env
   ```
4. Run migrations:
   ```bash
   alembic upgrade head
   ```
5. Start API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Health endpoint
- `GET /api/v1/health`

## Notes
- INPA source endpoint:
  - `POST https://portale.inpa.gov.it/concorsi-smart/api/concorso-public-area/search-better?page={page}&size={size}`
- Scheduler is enabled via `SYNC_ENABLED=true` and runs with `SYNC_CRON`.
# inpa-data-bridge
