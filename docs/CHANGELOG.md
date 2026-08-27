# Changelog

All notable changes to this project are documented in this file.

## 2026-08-27

### Added
- **Distinct-visitor tracking + page-visit logging**: The visitor counter now counts each distinct browser once (deduplicated server-side by a `visitor_id` UUID persisted in `localStorage`), and every page navigation is logged in a new `PageVisit` model without affecting the count. Previously only the homepage incremented the counter and deep-links/navigations were missed.
  - `VisitorCountView` accepts optional `visitor_id` + `page`; a returning visitor is not counted again but their page navigation is logged.
  - New `POST /api/v1/page-visits/` endpoint (`PageVisitView`) logs route changes with a lenient `page_visit` throttle (20/min).
  - New read-only `PageVisit` admin view and `visitor_id` column in the `VisitorAnalytics` admin.
  - Frontend: `src/utils/visitor.ts` manages the persistent visitor id; a `VisitorTracker` in `App.tsx` counts the visitor once on load and logs every route change. The old `visitor-count` POST was removed from `Home.tsx`.

### Fixed
- **Chatbot returning "Sorry, I encountered an error"**: Google retired the `gemini-2.5-flash` model (API returned `404 NOT_FOUND` for new users). Updated the default chat model to `gemini-3.6-flash` in `api/llm_client.py`, added its pricing (`$1.50/M input, $7.50/M output`) to `api/pricing.py`, and updated `backend/.env`/tests accordingly. The chatbot now answers correctly (e.g., motto → "Learning is Surviving!").
- **Blank pages on `/projects`, `/experience`, `/publications`, `/about`, `/resume`**: a production regression (introduced by the `01be2b1` `.dockerignore` change) left `VITE_API_URL` **unset at build time**, so Vite baked the literal string `"undefined"` into every API call — the browser then requested `/undefinedprojects/`, `/undefinedresumes/`, etc., nginx answered with the SPA `index.html` instead of JSON, and data-driven pages rendered empty. Fix: `frontend/Dockerfile` now declares `ARG VITE_API_URL` + `ENV VITE_API_URL=$VITE_API_URL`, and `docker-compose.yml` passes it as a build arg (default `https://api.mushfiqurrahmanrobin.com/api/v1/`, overridable per environment). This removes the implicit dependency on `.env.local` being present in the Docker build context, so the value is always baked in correctly regardless of CI or manual deploys.

### Docker / CI
- **Hardened the frontend Docker build**: added `frontend/.dockerignore` (excludes `node_modules`, `dist`, logs, env files) shrinking the build context from ~130 MB to ~3 MB, and switched the build stage from `npm install` to `npm ci` for deterministic, lockfile-exact installs (matching the CI workflow). This resolves transient `ECONNRESET` failures during `docker compose up --build`.

### Performance & Core Web Vitals
- **Self-hosted Poppins font** (weights 400/500/600/700, latin subset, ~31 KiB total) in `frontend/public/fonts/`, replacing the Google Fonts CDN. Eliminates the web-font layout-shift culprit flagged by PageSpeed Insights and removes a third-party render dependency.
- **Removed hero pre-render + inline critical CSS** from `index.html`. The pre-rendered shell was replaced by React on mount, which caused the LCP "element render delay" (2,710 ms mobile / 4,630 ms desktop) and the hero-banner CLS. The app now renders the hero once through React with correctly-split bundles.
- **Removed `deferCssPlugin`** (the `media="print" onload` CSS deferral). The main CSS bundle is only ~14 KB; serving it as a normal render-blocking stylesheet avoids FOUC (flash of unstyled content) that was contributing to CLS.
- **Fixed Vite `manualChunks`**: replaced the object-form config (which silently failed to capture `react-dom/client`) with a function-form splitter. react/react-dom/react-router now live in the immutable `vendor` chunk; the app `index` chunk dropped from **188 KB → ~14 KB**, cutting main-thread parse/execution work.
- **Composited the hero `pulse-glow` animation**: replaced `transform: scale/rotate` (non-composited, main-thread cost) with an opacity-only animation plus `will-change: opacity`.
- **Reserved space for the Calendly "Book a Session" button**: it now renders with `visibility: hidden` until the config loads, instead of appearing asynchronously and shifting the hero layout.
- **Added `res.ok` checks** to the Home page `fetch` calls for visitor-count, booking-config, and featured projects so HTTP error responses are handled deterministically.

### Images
- Generated a proper **1200×630 `og-image.webp`** (was pointing at a 1536×1024 file while declaring 1200×630 — a dimension mismatch) and updated og:/twitter: image meta to reference it.
- Generated a retina-friendly **960×640 `about-profile.webp`** for the About page (was serving a 1536×1024 file for a ~480 px display).
- Added explicit `width`/`height` attributes to the About page image to prevent layout shift.

### Agentic Browsing & Structured Data
- Added **JSON-LD `Person` structured data** (name, URL, image, sameAs social profiles, knowsAbout) to `index.html`, improving schema density and machine readability.
- The mobile **agentic browsing** score (2/3) was failing the `cumulative-layout-shift` audit (0.223 > 0.1 threshold); the CLS fixes above bring it under the threshold (desktop was already passing at 0.012).

### Tests & CI
- Added a **frontend test step** (`npm run test:run`) to the CI/CD pipeline so the Vitest suite (currently 17 tests) runs on every push/PR.
- Updated `index.shell.test.ts` to assert the cleaned `index.html` contract: self-hosted font preloads, no external font hosts, empty `#root`, and matching og:image dimensions.

## 2026-07-15

### Performance & SEO
- Created proper `robots.txt` (plain text) to fix invalid robots.txt error reported by PageSpeed Insights.
- Created `llms.txt` with H1 header and links for AI/LLM crawler discoverability.
- Created `sitemap.xml` listing all public routes with priorities.
- Added SEO meta tags: `<meta name="description">`, Open Graph (`og:title`, `og:description`, `og:type`, `og:url`, `og:site_name`), Twitter Card (`twitter:card`, `twitter:title`, `twitter:description`), and canonical URL.
- Added `<link rel="preconnect">` for `fonts.googleapis.com`, `fonts.gstatic.com`, and `api.mushfiqurrahmanrobin.com` to reduce connection latency.
- Replaced render-blocking Google Fonts CSS `@import` with non-blocking `<link>` pattern (`media="print" onload="this.media='all'"` + `<noscript>` fallback).
- Added `<link rel="preload">` for Google Fonts stylesheet to prioritize critical font loading.
- Added `Cache-Control` headers to nginx config: static assets (1-year immutable cache), robots.txt/llms.txt (1-day cache), HTML (no-cache).
- Added `loading="lazy"` and `decoding="async"` attributes to below-the-fold images for improved LCP.
- Added `decoding="async"` to main project image in ProjectDetail for faster decoding.
- Implemented Vite code splitting: vendor chunk (React/ReactDOM/ReactRouter), axios chunk, and lazy-loaded route chunks.
- Used `React.lazy()` + `Suspense` for all non-Home routes and ChatbotWidget to reduce initial bundle size and unused JavaScript.
- Inlined critical CSS (~1.7 KiB) in `<style>` block for immediate above-fold rendering without waiting for external stylesheet.
- Converted external Vite CSS link to non-blocking pattern (`media="print" onload`) via custom Vite plugin to eliminate render-blocking CSS.
- Fixed color contrast ratio on skill percentage text (`.skill-level`) — replaced `--color-green-accent` with new `--color-green-accent-light` (#22B4D2) meeting WCAG AA 4.5:1 threshold.
- Added unique `aria-label` attributes to "View Live" buttons across Home and ProjectList to fix identical-link accessibility warning.

### Changed
- Vite build now generates separate chunks: vendor (~34 KiB), axios (~42 KiB), app core (~188 KiB), plus per-route lazy chunks (~2-3 KiB each).
- Google Fonts loading moved from CSS `@import` to HTML `<link>` with non-blocking pattern.
- CSS bundle split: critical base styles (~14 KiB) loaded eagerly; component/page CSS loaded on demand via lazy routes.
- External CSS stylesheet now uses non-blocking `media="print" onload` pattern generated by a custom Vite plugin.
- nginx now serves `robots.txt`, `llms.txt`, and `sitemap.xml` from root with explicit location blocks.
- Added `^~` prefix modifiers to nginx proxy locations to prevent regex cache location from intercepting proxied requests.

## 2026-07-11

### Added
- Calendly "Book a Session" integration with backend `CALENDLY_URL`/`CALENDLY_USERNAME` environment variables and `/api/v1/site-config/` endpoint.
- "Book a Session" button on the homepage hero banner (next to "Buy Me a Coffee") with Calendly blue styling and full mobile responsiveness.
- `SiteConfigView` API endpoint returning public site configuration.

### Changed
- Backend Dockerfile now runs as non-root `appuser` with appropriate file ownership.
- Frontend Dockerfile now runs as non-root `nginx` user on port 8080 instead of 80.
- `entrypoint.sh` now uses `pg_isready -U postgres` (PostgreSQL superuser) for database readiness check.
- Frontend nginx config listens on port 8080 to support non-root operation.

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
