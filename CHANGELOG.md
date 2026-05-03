# Changelog

All notable changes to this project are documented in this file.

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
