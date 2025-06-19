# Full-Stack Portfolio: Django, React, and Docker

This is the source code for my personal portfolio, built with a modern, scalable tech stack.

## Tech Stack

-   **Backend**: Django & Django REST Framework
-   **Frontend**: React (Vite + TypeScript)
-   **Database**: PostgreSQL
-   **DevOps**: Docker, Docker Compose, GitHub Actions, Pre-commit
-   **Tooling**: `uv`, `ruff`, `pytest`, `npm`

## Running Locally

1.  **Prerequisites**: Docker and Docker Compose must be installed.
2.  **Environment**: Copy `backend/.env.template` to `backend/.env` and `frontend/.env.local.template` to `frontend/.env.local`.
3.  **Build & Run**:
    ```bash
    docker-compose up --build
    ```
4.  **Access**:
    -   **Frontend**: `http://localhost:5173`
    -   **Backend API**: `http://localhost:8000/api/`
    -   **Django Admin**: `http://localhost:8000/admin/`

5.  **Create Superuser** (for admin access):
    ```bash
    docker-compose exec backend python manage.py createsuperuser
    ```

## Deployment

-   **CI/CD**: The GitHub Actions pipeline in `.github/workflows/ci.yml` runs tests and linters on every push.
-   **Backend**: Deployed as a Web Service on Render.
-   **Frontend**: Deployed as a static site on Vercel.
