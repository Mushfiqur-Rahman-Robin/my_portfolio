# Full-Stack Portfolio: Django, React, and Docker

This is the source code for my personal portfolio, built with a modern, scalable tech stack. It's designed to showcase projects, skills, and experiences effectively.

## Features

-   **Dynamic Portfolio:** Showcase projects with descriptions, images, tags, and links to live demos and source code.
-   **Experience Timeline:** Detail professional experiences and display associated photos.
-   **Skills Overview:** Highlight technical skills and proficiencies.
-   **Credentials Display:** List publications, certifications, and achievements.
-   **Contact Form:** Allow visitors to send messages directly via an integrated contact form with email notifications.
-   **Resume Access:** Provide an easy way to view or download the latest resume.
-   **Visitor Counter:** Track website engagement with a simple visitor counter.
-   **Admin Interface:** Django admin for easy content management.
-   **Responsive Design:** Ensures a good viewing experience across various devices.

## Tech Stack

-   **Backend**: Django & Django REST Framework
    -   Database: PostgreSQL
    -   API Documentation: `drf-spectacular`
-   **Frontend**: React (Vite + TypeScript)
-   **DevOps**: Docker, Docker Compose, GitHub Actions
-   **Tooling**: `uv` (Python package manager), `ruff` (linter), `pytest` (testing), `npm` (Node package manager), `pre-commit`

## Project Structure

The repository is organized as a monorepo with the following main directories:

-   **`backend/`**: Contains the Django REST Framework application.
    -   `api/`: Houses the core API logic, including models, views, serializers, and URLs.
    -   `core/`: Includes Django project settings, ASGI/WSGI configurations, and root URLconf.
    -   `Dockerfile`, `requirements.txt`, `manage.py`: Standard Django and Docker files for the backend.
    -   See [Backend README](backend/README.md) for more details.
-   **`frontend/`**: Contains the React (Vite + TypeScript) application.
    -   `src/`: Main source code directory for React components, pages, assets, and styles.
    -   `public/`: Static assets accessible directly.
    -   `Dockerfile`, `package.json`, `vite.config.ts`: Standard files for the React frontend and its Docker setup.
    -   See [Frontend README](frontend/README.md) for more details.
-   **`.github/workflows/`**: CI/CD pipeline configurations using GitHub Actions.
-   **`docker-compose.yml`**: Defines services, networks, and volumes for local development using Docker Compose.
-   **Root directory**: Contains shared configurations like `.gitignore`, `.pre-commit-config.yaml`, and this `README.md`.

## Running Locally

1.  **Prerequisites**: Docker and Docker Compose must be installed.
2.  **Environment**:
    -   Copy `backend/.env.template` to `backend/.env` and fill in the necessary environment variables.
    -   Copy `frontend/.env.local.template` to `frontend/.env.local` and fill in the necessary environment variables.
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

-   **CI/CD**: The GitHub Actions pipeline in `.github/workflows/cicd.yml` runs tests and linters on every push.
-   **Backend**: Deployed as a Web Service on Render.
-   **Frontend**: Deployed as a static site on Vercel.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these general guidelines:

1.  **Fork the repository.**
2.  **Create a new branch** for your feature or bug fix: `git checkout -b feature-name` or `git checkout -b fix-name`.
3.  **Make your changes** and commit them with clear, descriptive messages.
4.  **Ensure your code adheres to the project's linting standards** (run `pre-commit run --all-files` if configured).
5.  **Push your changes** to your forked repository.
6.  **Open a pull request** to the main repository, detailing the changes you've made.

Please ensure your code is well-tested and documented where appropriate.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
