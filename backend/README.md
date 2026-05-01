# Backend (Django + DRF)

This service exposes the portfolio API used by the React frontend.

## What is here

- `api/`: Models, serializers, viewsets, throttling, chatbot integration.
- `core/`: Django settings, URL routing, WSGI/ASGI entry points.
- `manage.py`: Django management commands.
- `requirements.txt` and `pyproject.toml`: Python dependencies and tooling config.

## Local run with Docker

From repository root:

```bash
docker compose up -d --build backend db redis chromadb
```

Backend URLs:

- API root: `http://127.0.0.1:8000/api/v1/`
- Admin: `http://127.0.0.1:8000/admin/`
- Health: `http://127.0.0.1:8000/health/`

## Environment

Backend reads environment values from `backend/.env` (loaded by `docker-compose.yml`).

## Database backup restore (Docker Postgres)

Latest backups are in `/home/mushfiq/portfolio_backups`. To restore safely without editing backup files:

```bash
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U portfolio -d portfolio_db -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
gzip -dc /home/mushfiq/portfolio_backups/YYYY-MM-DD_04-00-01/db_dump.sql.gz | docker compose exec -T db psql -v ON_ERROR_STOP=1 -U portfolio -d portfolio_db
```

## Notes

- API routes are versioned under `/api/v1/`.
- Backend logic is intentionally separate from frontend styling work.
- See [../CHANGELOG.md](../CHANGELOG.md) for tracked cross-project changes.
