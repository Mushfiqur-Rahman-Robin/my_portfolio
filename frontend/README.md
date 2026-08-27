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

> **Docker builds do NOT read `.env.local`.** `frontend/.dockerignore` excludes
> `.env*` from the build context, so the container build receives `VITE_API_URL` as
> an explicit build ARG declared in `frontend/Dockerfile` and wired up in
> `docker-compose.yml` (default `https://api.mushfiqurrahmanrobin.com/api/v1/`,
> override with `VITE_API_URL=/api/v1/`). Forgetting this produced `undefined`
> API URLs and blank pages in production (see `docs/CHANGELOG.md`).

## Changelog

- See [../docs/CHANGELOG.md](../docs/CHANGELOG.md) for tracked UI and project updates.

## Key folders

- `src/components/`: Reusable UI blocks (navbar, footer, project list, skills).
- `src/pages/`: Route-level pages and page-scoped CSS.
- `src/index.css`: Global design tokens and base typography/colors.

## Build

```bash
cd frontend
npm run build
```

## Performance notes

- **Fonts**: Poppins is self-hosted (latin subset, weights 400/500/600/700) under `public/fonts/` and preloaded via `<link rel="preload">`. This removes the Google Fonts third-party dependency and eliminates font-swap layout shift.
- **Bundle splitting**: `vite.config.ts` uses a function-form `manualChunks` so react/react-dom/react-router live in a cacheable `vendor` chunk and the app `index` chunk stays small (~14 KB).
- **index.html**: kept minimal (meta/SEO tags, API preconnect, font preloads, JSON-LD Person schema, empty `#root`). The hero and all content are rendered by React — no pre-rendered shell or duplicated critical CSS, which previously caused LCP delay and CLS.

## Tests

```bash
cd frontend
npm run test:run
```
