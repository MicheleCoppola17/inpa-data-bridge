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

Exam payloads include `short_title`, `short_description`, `sector`, `organization`, `regions`, `provinces`, `url`, `salary_range`, `selection_criteria`, `is_expired`, `published_at`, `expires_at`, `vacancies`, and `position` for cleaner presentation.

### `/api/v1/exams` query params
- `page` (default `0`)
- `size` (default `20`, max `100`)
- `is_expired` (`true|false`)
- `updated_after` (ISO datetime)
- `sector` (e.g. `Amministrativo e Contabile`)
- `region` (e.g. `Lazio`) - Matches if the region is present in the `regions` list.
- `province` (e.g. `Roma`) - Matches if the province is present in the `provinces` list.
- `q` (search over `short_title` and `description`)
- `sort` (`-published_at`, `published_at`, `-updated_at`, `updated_at`, `-expires_at`, `expires_at`)

## Internal sync endpoints
- `GET /api/v1/internal/sync/status`
- `POST /api/v1/internal/sync/run`

## INPA source endpoint
`POST https://portale.inpa.gov.it/concorsi-smart/api/concorso-public-area/search-better?page={page}&size={size}`

## Notes
- **Multi-Region Support**: The service correctly parses the flat `sedi` array from INPA, distinguishing between regions and provinces using a curated list of the 20 Italian regions.
- **Data Structure**: `regions` and `provinces` are stored as JSONB arrays to handle exams spanning multiple locations.
- **Filtering**: Filtering by `region` or `province` uses containment logic (matches if the requested value exists in the respective list).
- Sync uses content hashing for new vs updated detection.
- Automatic Cleanup: Exams that have been expired for more than 14 days are automatically deleted at the end of each sync run.
- Scheduler is controlled via `SYNC_ENABLED` and `SYNC_CRON`.
- Default sync handles up to 50 pages (2500 items) per run to balance load.
