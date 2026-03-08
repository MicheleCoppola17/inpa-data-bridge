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

## Public endpoints
- `GET /api/v1/health`
- `GET /api/v1/exams`
- `GET /api/v1/exams/{id}`

Exam payloads include `short_title`, `municipality`, `region`, `province`, `url`, `salary_range`, and `selection_criteria` for cleaner iOS presentation.

### `/api/v1/exams` query params
- `page` (default `0`)
- `size` (default `20`, max `100`)
- `is_expired` (`true|false`)
- `updated_after` (ISO datetime)
- `q` (search over `titolo` and `codice`)
- `sort` (`-data_pubblicazione`, `data_pubblicazione`, `-updated_at`, `updated_at`, `-data_scadenza`, `data_scadenza`)

## Internal sync endpoints
- `GET /api/v1/internal/sync/status`
- `POST /api/v1/internal/sync/run`

## INPA source endpoint
`POST https://portale.inpa.gov.it/concorsi-smart/api/concorso-public-area/search-better?page={page}&size={size}`

## Notes
- Sync uses content hashing for new vs updated detection.
- Scheduler is controlled via `SYNC_ENABLED` and `SYNC_CRON`.
