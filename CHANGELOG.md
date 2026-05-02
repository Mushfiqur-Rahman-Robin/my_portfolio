# Changelog

All notable changes to this project are documented in this file.

## 2026-05-03

### Added
- Added automatic conversion of newly uploaded image files to WebP for portfolio image models.
- Added backend tests to verify new image uploads are saved as `.webp` and legacy non-WebP image paths remain unchanged unless re-uploaded.

### Changed
- Updated test settings to use PostgreSQL only when test DB environment variables are provided; otherwise fallback to local SQLite.
- Disabled Chroma sync signal execution in test settings via `ENABLE_CHROMA_SYNC = False` to avoid external-service coupling in unit/API tests.

### Fixed
- Fixed local test failures caused by unresolved placeholder test DB credentials in `core.test_settings`.

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
