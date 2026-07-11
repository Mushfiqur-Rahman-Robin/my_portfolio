# Changelog

All notable changes to this project are documented in this file.

## 2026-07-11

### Fixed
- Added `unique=True` constraint to `LLMCostTracking.job_name` field to enforce database-level uniqueness and prevent accidental cost-row merging from duplicate job names.

## 2026-07-04

### Fixed
- Fixed ChromaDB `WARNING: Number of requested results N is greater than number of elements in index` by capping `n_results` in `query_nodes()` to the actual collection document count before querying. Returns an empty result immediately if the collection contains zero documents.
- Fixed `job_name` collision risk in `index_content` command: timestamp now includes microseconds (`%Y%m%d_%H%M%S_%f`) so two simultaneous runs can never share a name and accidentally merge their cost rows into one `LLMCostTracking` record.
- Fixed `test_concurrent_write_safety_via_select_for_update` test using `order_by("-updated_at")` instead of `order_by("-created_at")` to match `LLMCostTracking.Meta.ordering` and eliminate a sub-millisecond timing fragility.
- Added two new tests for the ChromaDB capping behaviour: `test_query_nodes_caps_n_results_to_collection_size` and `test_query_nodes_returns_empty_when_collection_is_empty`.

## 2026-07-03

### Added
- Refactored `LLMCostTracking` model to consolidate token usage and costs into a single database row per chat session or background indexing job, moving away from per-transaction ledgers.
- Increased financial tracking precision from 4 to 8 decimal places (e.g., `0.00002100`) for precise accounting of small micro-transactions.
- Added `job_name` field to identify background indexing jobs (e.g., `index_content`).
- Added `api/pricing.py` with model-specific pricing constants (Gemini 2.5 Flash, GPT-4.1-mini, gemini-embedding-2, text-embedding-3-small, etc.) and cost calculation helpers using `Decimal` arithmetic for exact monetary precision.
- Integrated cost tracking into `generate_chat_completion` (records chat cost per session) and `generate_embedding` (records embedding cost per job/session).
- Registered read-only `LLMCostTracking` admin view with operation type, model, session total tokens, session cost, running totals, and session/job link.
- Added comprehensive test suite (`LLMCostTrackingTests`) for cost tracking: record creation, session consolidation, chat+embedding mixed tracking, pricing calculations, token estimation, and query count verification.
- Implemented `select_for_update()` row locking with `get_or_create()` in `record_llm_cost` to prevent race conditions when updating session-level totals and recalculating global totals.

### Fixed
- Fixed `int()` conversion in token extraction from Gemini `usage_metadata` and OpenAI `usage` to handle Mock objects in tests.
- Fixed chat completion cost recording to only trigger when a session is provided.
- Fixed pre-existing test assertions for Gemini embedding model name (`gemini-embedding-2`) and embedding dimension (`1536`).
- Switched cost arithmetic from `float` to `Decimal` throughout the pipeline to avoid floating-point precision loss.

## 2026-05-03

### Security
- Restricted write operations on portfolio content APIs to admin users while preserving public read access.
- Kept contact, visitor count, and chatbot endpoints publicly accessible with existing throttling.
- Replaced raw internal exception string in visitor count API responses with a generic error message.
- Added production-focused Django security settings (`SECURE_SSL_REDIRECT`, secure cookies, HSTS, content type nosniff) configurable via environment variables.

### CI/CD
- Added push-trigger coverage for `fix/issues-and-vulnerabilites` and `fix/issues-and-vulnerablities` branches in GitHub Actions.

### Tests
- Updated API tests to authenticate admin users for write operations and added a regression test confirming unauthenticated write requests are rejected.

### Added
- Added automatic conversion of newly uploaded image files to WebP for portfolio image models.
- Added backend tests to verify new image uploads are saved as `.webp` and legacy non-WebP image paths remain unchanged unless re-uploaded.
- Added one-time management command `backfill_images_to_webp` for safely converting existing `.jpg/.jpeg/.png` ImageField files to `.webp` with dry-run/apply modes.
- Added `VisitorAnalytics` tracking for visitor count events, capturing IP, country, device type, user-agent, and visit timestamp for admin-only visibility.
- Added read-only Django admin view for visitor analytics with filter/search support.
- Added backend tests for visitor metadata capture and chatbot memory-window behavior.
- Added `api/prompt.py` to centralize chatbot prompt generation with safe placeholder handling.
- Added extra backend tests for prompt defaults/placeholders and visitor helper behavior.

### Changed
- Updated test settings to use PostgreSQL only when test DB environment variables are provided; otherwise fallback to local SQLite.
- Disabled Chroma sync signal execution in test settings via `ENABLE_CHROMA_SYNC = False` to avoid external-service coupling in unit/API tests.
- Updated chatbot session memory policy to use the most recent 20 interactions (40 messages) instead of character-cap truncation.
- Updated GitHub Actions workflow to newer action versions and removed Node 20 deprecation warning path.

### Fixed
- Fixed local test failures caused by unresolved placeholder test DB credentials in `core.test_settings`.
- Fixed CI test failures returning `301` by disabling `SECURE_SSL_REDIRECT` and secure cookie/HSTS enforcement inside `core.test_settings` (tests now behave consistently when `DEBUG=False`).

## 2026-05-01

### Added
- Added `CHANGELOG.md` to track project updates.
- Added mobile menu scroll lock behavior in navbar (`mobile-menu-open` body state).
- Added consistent image-frame containers for featured and list project cards.
- Added truncation helper for project titles/descriptions to keep card layouts uniform.

### Changed
- Refined responsive navbar behavior for mobile full-width top menu overlay.
- Improved overall UI spacing/typography consistency across home, list, projects, and footer sections.
- Updated `README.md`, `frontend/README.md`, and `backend/README.md` to reflect current run/deploy flow and environment setup.
- Updated project detail page title color to white and improved button spacing/alignment on mobile.
- Standardized project card section sizing (title/image/description/tags/actions) for cleaner alignment.

### Fixed
- Fixed mobile menu overlay so background page does not scroll while menu is open.
- Fixed project list action button text alignment on mobile.
- Fixed inconsistent project detail action-button spacing.
- Fixed small-screen clipping of clamped project text and centered project detail button labels.
- Fixed tag-row clipping by increasing tag-row height allowance in project card layouts.
