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
Use `backend/.env.template` as the source of truth for required variables.

Security-related environment variables (recommended for production):

- `SECURE_SSL_REDIRECT=True`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_HSTS_SECONDS=31536000`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
- `SECURE_HSTS_PRELOAD=True`
- `SECURE_CONTENT_TYPE_NOSNIFF=True`

## Database backup restore (Docker Postgres)

Latest backups are in `/home/mushfiq/portfolio_backups`. To restore safely without editing backup files:

```bash
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U portfolio -d portfolio_db -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
gzip -dc /home/mushfiq/portfolio_backups/YYYY-MM-DD_04-00-01/db_dump.sql.gz | docker compose exec -T db psql -v ON_ERROR_STOP=1 -U portfolio -d portfolio_db
```

## Notes

- API routes are versioned under `/api/v1/`.
- Public read endpoints remain open for portfolio content (`GET`/safe methods), while write actions on content endpoints are now admin-only.
- Backend logic is intentionally separate from frontend styling work.
- Calendly integration is configured via `CALENDLY_URL` and `CALENDLY_USERNAME` environment variables. The `/api/v1/booking-config/` endpoint exposes these to the frontend for the "Book a Session" button.
- New image uploads for portfolio models are converted to WebP at save time in backend signals. Existing stored `.png/.jpg` paths are kept as-is unless a new image is uploaded.
- Visitor count endpoint now logs admin-only visitor analytics metadata (`ip_address`, country, device type, user-agent, timestamp) in `VisitorAnalytics`.
- Visitor counting is deduplicated per distinct browser via a `visitor_id` UUID (persisted in `localStorage`); every page navigation is logged in `PageVisit` without affecting the count. See `POST /api/v1/visitor-count/` and `POST /api/v1/page-visits/`.
- Chatbot memory now uses the most recent 20 interactions per session (user+assistant pairs) for follow-up continuity.
- Chatbot prompt assembly is centralized in `api/prompt.py` (`build_chatbot_prompt`) so placeholder-like values (e.g. `{x}`, `${NAME}`) are passed safely without formatting errors.
- LLM provider and model are configurable via `LLM_PROVIDER` (default: `gemini`; also supports `openai`), `LLM_CHAT_MODEL` (optional override), and the respective API keys (`GEMINI_API_KEY` / `OPENAI_API_KEY`). See `api/llm_client.py` for the abstraction layer.
- LLM cost tracking is managed via the `LLMCostTracking` model — a single row per chat session or background indexing job that aggregates token usage and costs. Cumulative running totals (`total_chat_cost`, `total_embedding_cost`, `total_cost`, `total_chat_tokens`, `total_embedding_tokens`, `total_tokens`) are recalculated across all records on each write. Costs are stored as precise `Decimal` values with 8 decimal places (e.g., `0.00002100`). Pricing is centralized in `api/pricing.py` and verified against current API provider pricing pages. The admin panel provides a read-only view.
- Chat costs are recorded per `ChatSession`; embedding costs (from RAG queries and content indexing) are recorded per `job_name`. Token counting uses real API `usage_metadata`/`usage` when available, falling back to `tiktoken` estimation (`cl100k_base`). Row-level locking (`select_for_update()`) with `get_or_create` prevents race conditions on per-session/per-job totals.
- Test settings (`core.test_settings`) now use PostgreSQL when `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` are provided (CI behavior), otherwise fallback to local SQLite for safer local test runs.
- See [../docs/CHANGELOG.md](../docs/CHANGELOG.md) for tracked cross-project changes.

## Deployment safety checklist

- Keep migrations in CI and deploy (already configured in `.github/workflows/cicd.yml`).
- Use non-interactive exec (`docker compose exec -T ...`) in automation.
- Rotate credentials immediately if any secret was exposed outside secure secret stores.

## One-time backfill: convert existing images to WebP

For existing DB records pointing to `.jpg/.jpeg/.png`, use the management command below.

1. Dry run (no write):

```bash
docker compose exec backend python manage.py backfill_images_to_webp
```

2. Apply conversion (write DB + media):

```bash
docker compose exec backend python manage.py backfill_images_to_webp --apply
```

3. Optional cleanup of original files after successful conversion:

```bash
docker compose exec backend python manage.py backfill_images_to_webp --apply --delete-old
```

Recommendations:
- Always take DB + media backup before running `--apply` in production.
- Validate pages and admin after conversion.
- Keep `--delete-old` for the final pass after verification.
