# Frontend (React + Vite + TypeScript)

This app renders the portfolio UI and consumes the Django API.

## UI direction

- Theme: dark + teal accent (`rgb(8, 145, 178)`).
- Focus: cleaner spacing, stronger visual hierarchy, and mobile-first responsiveness.
- Scope: frontend presentation only (no backend business logic changes).

## Current UI conventions

- Navbar desktop alignment: logo left, nav links right-aligned to match main content boundaries.
- Hero CTA buttons: equal-height button styling for consistent vertical alignment. Includes "Book a Session" (Calendly) and "Buy Me a Coffee" buttons.
- Skills section: unified, compact skill grid (no category headers) with responsive columns.
- Project images (home featured + all projects): fixed-size framed image area with contained fit for consistent card alignment across mixed image sizes.

## Run options

### 1) Vite dev mode (recommended while iterating UI)

```bash
cd frontend
npm install
npm run dev
```

- Frontend URL: `http://localhost:5174`
- Dev proxy forwards `/api/*` and `/media/*` to backend `http://127.0.0.1:8000`

### 2) Docker mode

From repository root:

```bash
docker compose up -d --build frontend backend db redis chromadb
```

- Frontend URL: `http://127.0.0.1:5173`

## Environment

Create `frontend/.env.local` with:

```dotenv
VITE_API_URL=/api/v1/
```

This keeps API calls same-origin in both Docker and local dev proxy mode.

## Changelog

- See [../docs/CHANGELOG.md](../docs/CHANGELOG.md) for tracked UI and project updates.

## Key folders

- `src/components/`: Reusable UI blocks (navbar, footer, project list, skills).
- `src/pages/`: Route-level pages and page-scoped CSS.
- `src/index.css`: Global design tokens and base typography/colors.
- `public/fonts/`: Self-hosted Poppins latin-subset woff2 files (300–700) plus
  the OFL-1.1 `LICENSE.txt`. The font is preloaded and declared with
  `font-display: optional` inline in `index.html` to avoid layout shift.

## Build

```bash
cd frontend
npm run build
```

## Tests

The frontend uses [Vitest](https://vitest.dev) with [jsdom](https://github.com/jsdom/jsdom) and
[@testing-library/react](https://testing-library.com/docs/react-testing-library/intro/).

```bash
cd frontend
npm test          # watch mode
npm run test:run  # one-shot (used in CI)
npm run coverage  # one-shot with v8 coverage report
```

Conventions:

- Test files live next to the code they cover (or under `src/test/`) and match
  `*.{test,spec}.{ts,tsx}`.
- Global matchers (`toBeInTheDocument`, …) and the Vitest globals (`describe`,
  `it`, `expect`, `vi`) are configured in `src/test/setup.ts` and
  `src/test/vitest-env.d.ts`; no per-file imports of those globals are needed.
- Configuration lives in `vitest.config.ts`; the Vite config in `vite.config.ts`
  is untouched so the production build is unaffected.
