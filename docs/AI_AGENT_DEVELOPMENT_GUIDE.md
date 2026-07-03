# AI Agent Development Guide

**Last Updated:** July 3, 2026
**Version:** 1.0
**Purpose:** Comprehensive reference for AI agents to manage portfolio project development, testing, and deployment.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Environment Setup](#environment-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Testing Procedures](#testing-procedures)
6. [Build & Deployment](#build--deployment)
7. [Security Audit](#security-audit)
8. [Troubleshooting](#troubleshooting)
9. [Git Workflow](#git-workflow)
10. [Important Notes](#important-notes)

---

## Project Overview

**Portfolio Project** - Full-stack Django + React web application for displaying professional portfolio.

### Tech Stack
- **Backend:** Django 5.2.3, Django REST Framework 3.16.0, Python 3.12
- **Frontend:** React 19.1, Vite 6.4, TypeScript
- **Database:** PostgreSQL 15 (production), SQLite (local/test)
- **Cache:** Redis 7
- **Vector Store:** ChromaDB 0.4.14
- **LLM Providers:** OpenAI GPT / Google Gemini Flash 2.5 (configurable)
- **Containerization:** Docker Compose

### Key Features
- Portfolio content management (projects, experiences, certifications, publications)
- Public API with role-based access control
- Chatbot with ChromaDB knowledge base integration
- Visitor analytics tracking
- Admin dashboard with CKEditor4 rich text editing

### Repository Structure
```
my_portfolio/
├── backend/                    # Django application
│   ├── core/                   # Settings, routing, WSGI/ASGI
│   ├── api/                    # Models, serializers, views, tests
│   ├── manage.py               # Django management CLI
│   ├── requirements.txt         # Python dependencies
│   ├── pyproject.toml          # Python project metadata
│   ├── pytest.ini              # Pytest configuration
│   ├── .env.template           # Environment variables template
│   └── README.md               # Backend-specific documentation
├── frontend/                   # React application
│   ├── src/                    # React components, pages, utilities
│   ├── public/                 # Static assets
│   ├── package.json            # Node dependencies
│   ├── vite.config.ts          # Vite build configuration
│   └── README.md               # Frontend-specific documentation
├── .github/
│   └── workflows/
│       └── cicd.yml            # GitHub Actions CI/CD pipeline
├── docker-compose.yml          # Container orchestration
├── CHANGELOG.md                # Change log
└── README.md                   # Project overview

```

---

## Environment Setup

### Prerequisites
- Python 3.12 with venv support
- Node.js 20.x with npm
- Docker & Docker Compose
- Git 2.x or later

### Backend Environment Setup

#### 1. Activate Python Virtual Environment
```bash
cd /home/mushfiq/Desktop/my_portfolio/backend
source .venv/bin/activate
```

**Alternative activation commands:**
```bash
# If using different shell
. .venv/bin/activate              # bash/sh
source .venv/bin/activate.fish    # fish shell
.venv\Scripts\activate            # Windows CMD
.venv\Scripts\Activate.ps1        # Windows PowerShell
```

#### 2. Verify Python Environment
```bash
which python                    # Shows Python executable path
python --version               # Should show Python 3.12.x
pip list | grep Django         # Verify Django is installed
```

#### 3. Required Environment Variables
Create `.env` file in `backend/` directory based on `.env.template`:

**Critical Variables (no defaults):**
- `SECRET_KEY` - Django secret key (generate via `openssl rand -hex 32`)
- `DEBUG` - Set to `False` in production
- `ALLOWED_HOSTS` - Comma-separated list of allowed domain names
- `CSRF_TRUSTED_ORIGINS` - CORS/CSRF allowed origins
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string (default: redis://localhost:6379/1)
- `OPENAI_API_KEY` - OpenAI API key for chatbot (required when LLM_PROVIDER=openai)
- `GEMINI_API_KEY` - Google Gemini API key for chatbot (required when LLM_PROVIDER=gemini)
- `LLM_PROVIDER` - Which LLM provider to use: `openai` or `gemini` (default: `gemini`)
- `LLM_CHAT_MODEL` - Optional: override the default chat model for the selected provider

**Security Settings (auto-enabled when DEBUG=False):**
- `SECURE_SSL_REDIRECT` - Redirect HTTP to HTTPS
- `SESSION_COOKIE_SECURE` - Secure session cookies
- `CSRF_COOKIE_SECURE` - Secure CSRF cookies
- `SECURE_HSTS_SECONDS` - HSTS max-age (default: 31536000)
- `SECURE_HSTS_INCLUDE_SUBDOMAINS` - HSTS subdomains
- `SECURE_HSTS_PRELOAD` - HSTS preload header
- `SECURE_CONTENT_TYPE_NOSNIFF` - X-Content-Type-Options header

**Email Configuration:**
- `EMAIL_BACKEND` - Email backend class
- `EMAIL_HOST` - SMTP server hostname
- `EMAIL_PORT` - SMTP port (usually 587)
- `EMAIL_USE_TLS` - Use TLS for email
- `EMAIL_HOST_USER` - SMTP username
- `EMAIL_HOST_PASSWORD` - SMTP password
- `DEFAULT_FROM_EMAIL` - Default "from" address
- `ADMIN_EMAIL` - Admin email for notifications

**Database (PostgreSQL):**
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- `POSTGRES_HOST` - Database hostname (default: localhost)
- `POSTGRES_PORT` - Database port (default: 5432)

### Frontend Environment Setup

#### 1. Install Dependencies
```bash
cd /home/mushfiq/Desktop/my_portfolio/frontend
npm ci                          # Clean install (preferred for CI)
# or
npm install                     # Install with package-lock updates
```

#### 2. Verify Installation
```bash
npm list axios react react-router-dom    # Check key dependencies
npm audit --omit=dev                     # Check for vulnerabilities
```

---

## Development Workflow

### Starting Local Development Environment

#### Option 1: Docker Compose (Recommended)
```bash
cd /home/mushfiq/Desktop/my_portfolio

# Start all services
docker compose up -d --build

# Services URLs:
# Frontend:     http://localhost:5173
# API:          http://localhost:8000/api/v1/
# Admin:        http://localhost:8000/admin/
# Docs:         http://localhost:8000/api/v1/schema/swagger-ui/

# View logs
docker compose logs -f backend    # Backend logs
docker compose logs -f frontend   # Frontend logs

# Stop services
docker compose down
```

#### Option 2: Local Development (Manual)

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=core.settings
export DEBUG=True
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Vite dev server starts at http://localhost:5173
```

### Making Code Changes

**Backend Changes:**
```bash
# Backend automatically reloads on file changes when using runserver
# For database changes: python manage.py makemigrations
# Apply migrations: python manage.py migrate
```

**Frontend Changes:**
```bash
# Frontend automatically reloads with Vite HMR (Hot Module Replacement)
```

### Creating Database Migrations

```bash
cd backend
python manage.py makemigrations api                # Create migration files
python manage.py migrate                           # Apply migrations
python manage.py sqlmigrate api <migration_number> # View SQL
```

### Django Admin Access

1. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. Access admin panel: `http://localhost:8000/admin/`

---

## Testing Procedures

### Backend Testing

#### Run All Tests
```bash
cd backend
source .venv/bin/activate

# Quick test run
pytest api/tests/ -q

# Verbose output
pytest api/tests/ -v

# With coverage report
pytest api/tests/ --cov=api --cov-report=html
```

#### Run Tests in CI-like Environment (DEBUG=False)
```bash
cd backend
source .venv/bin/activate

# This simulates GitHub Actions CI environment
DJANGO_SETTINGS_MODULE=core.test_settings \
DEBUG=False \
SECRET_KEY=test-secret-key \
PYTHONPATH=. \
EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend \
DEFAULT_FROM_EMAIL=test@example.com \
ADMIN_EMAIL=admin@example.com \
pytest api/tests/ -v
```

#### Run Specific Test
```bash
pytest api/tests/test_api_integration.py::APITests::test_create_project_requires_admin -v
```

#### Test Results Expected
- **Total Tests:** 264+
- **Pass Rate:** 100%
- **Duration:** ~25-30 seconds
- **Key Test:** `test_create_project_requires_admin` (validates admin-only write access)

### Frontend Testing

#### Linting
```bash
cd frontend
npm run lint

# Expected: 0 errors, 0 warnings
```

#### Build Verification
```bash
cd frontend
npm run build

# Expected output:
# - dist/index.html: ~0.5 KB
# - dist/assets/*.css: ~40 KB
# - dist/assets/*.js: ~285 KB
```

#### Security Audit
```bash
cd frontend
npm audit --omit=dev

# Expected: 0 vulnerabilities
```

### Django System Checks

```bash
cd backend
python manage.py check           # Development checks
python manage.py check --deploy  # Production readiness checks
```

**Expected in DEBUG=False:**
- 0 CRITICAL errors
- 0 ERRORS
- May have non-critical warnings (CKEditor EOL, drf-spectacular docs)

---

## Build & Deployment

### Docker Build

#### Build All Containers
```bash
cd /home/mushfiq/Desktop/my_portfolio
docker compose build

# Build specific service
docker compose build backend    # Backend only
docker compose build frontend   # Frontend only
```

#### Start Services
```bash
# Start in background
docker compose up -d --build

# Start with logs visible
docker compose up --build

# Health check
docker compose ps
```

### Frontend Build

```bash
cd frontend

# Development build (with source maps)
npm run build

# Built files location: dist/

# Preview production build locally
npm run preview
```

### Deployment Process

#### Full Deployment Flow
```bash
# 1. Ensure all tests pass locally
cd backend && pytest api/tests/ -q
cd frontend && npm run lint && npm run build

# 2. Push to GitHub
git push origin main

# 3. GitHub Actions automatically:
#    a. Runs backend tests (all must pass)
#    b. Runs frontend linting & build
#    c. Deploys to production server (if on main branch)
#    d. Runs migrations on production DB
#    e. Health checks
```

#### Manual Production Deployment (if needed)
```bash
cd /home/mushfiq/Desktop/my_portfolio
git fetch --all --prune
git checkout main
git pull origin main
docker compose up --build -d --no-deps --force-recreate backend frontend
docker compose exec -T backend python manage.py migrate --noinput
docker compose exec -T backend python manage.py check
docker compose ps
```

### Database Backups & Restores

#### Backup Production Database
```bash
docker compose exec -T db pg_dump -U portfolio portfolio_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### Restore from Backup
```bash
# 1. Drop and recreate schema
docker compose exec -T db psql -U portfolio -d portfolio_db \
  -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'

# 2. Restore from backup
gzip -dc backup_20260503_120000.sql.gz | docker compose exec -T db psql -U portfolio -d portfolio_db
```

---

## Security Audit

### Security Checks Performed

#### API Access Control
```bash
# Verify write-access is blocked for anonymous users
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Test"}' \
  -w "\nStatus: %{http_code}\n"
# Expected: 403 Forbidden
```

#### Dependency Vulnerabilities
```bash
# Frontend
cd frontend && npm audit --omit=dev

# Backend
cd backend && pip-audit
```

#### Security Headers
```bash
# Check security headers
curl -I http://localhost:8000/api/v1/projects/
# Look for: X-Frame-Options, X-Content-Type-Options, Referrer-Policy
```

#### Django Security Settings
- `SECURE_SSL_REDIRECT` - Auto-enabled when DEBUG=False
- `SESSION_COOKIE_SECURE` - Auto-enabled when DEBUG=False
- `CSRF_COOKIE_SECURE` - Auto-enabled when DEBUG=False
- `SECURE_HSTS_SECONDS` - Default 31536000 (1 year) when DEBUG=False
- `SECURE_CONTENT_TYPE_NOSNIFF` - Always True

### API Endponts Security Model

**Public Read Endpoints (AllowAny):**
- `GET /api/v1/projects/` - List projects
- `GET /api/v1/resumes/` - List resumes
- `GET /api/v1/experiences/` - List experiences
- `POST /api/v1/contact/` - Submit contact form (throttled)
- `POST /api/v1/visitor-count/` - Track visitor (throttled)
- `POST /api/v1/chatbot/` - Query chatbot (throttled)

**Admin-Only Write Endpoints (IsAdminUser):**
- `POST /api/v1/projects/` - Create project
- `PATCH /api/v1/projects/{id}/` - Update project
- `DELETE /api/v1/projects/{id}/` - Delete project
- `POST /api/v1/resumes/` - Create resume
- `POST /api/v1/experiences/` - Create experience
- `DELETE /api/v1/experiences/` - Delete experience

---

## Troubleshooting

### Common Issues

#### Tests Failing with 301 Status
**Problem:** Tests return HTTP 301 (redirect) when DEBUG=False
**Cause:** Production security settings enabled in test environment
**Solution:**
```bash
# Verify core/test_settings.py has these lines:
# SECURE_SSL_REDIRECT = False
# SESSION_COOKIE_SECURE = False
# CSRF_COOKIE_SECURE = False
# SECURE_HSTS_SECONDS = 0
```

#### PostgreSQL Connection Failed
**Problem:** `psycopg2.OperationalError: connection refused`
**Solution:**
```bash
# Check if PostgreSQL service is running
docker compose ps db

# Ensure DATABASE_URL is correct format:
# postgresql://user:password@localhost:5432/database_name  # pragma: allowlist secret

# Or use SQLite for local testing
export DATABASE_URL=sqlite:///./db.sqlite3
```

#### Redis Connection Failed
**Problem:** `ConnectionError: connection refused`
**Solution:**
```bash
# Start Redis
docker compose up -d redis

# Or use local Redis
redis-server

# Verify connection
redis-cli ping  # Should return PONG
```

#### Frontend Build Errors
**Problem:** `npm run build` fails
**Solution:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm ci

# Check TypeScript
npm run build

# Check for linting errors
npm run lint
```

#### Docker Build Timeout
**Problem:** `docker compose build` takes too long or times out
**Solution:**
```bash
# Increase Docker buildkit timeout
export DOCKER_BUILDKIT=1
docker compose build --no-cache

# Or check available disk space
df -h

# Remove dangling images
docker image prune -f
```

#### Admin Login Not Working
**Problem:** Admin credentials rejected
**Solution:**
```bash
# Reset admin user
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(username='admin').delete()
>>> exit()

# Create new admin
python manage.py createsuperuser
```

---

## Git Workflow

### Branch Naming Conventions
- `main` - Production branch (protected, auto-deploys)
- `fix/issues-and-vulnerabilites` - Feature/security branches (must pass CI)
- `migration/django-react-stack` - Major upgrade branches

### Commit Message Format
```
<type>(<scope>): <subject>

<body (optional)>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Code style (no functional changes)
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Maintenance (dependencies, config)
- `ci:` - CI/CD configuration
- `security:` - Security fixes/hardening
- `perf:` - Performance improvements

**Examples:**
```bash
git commit -m "feat(api): Add admin-only write access control to project endpoints"
git commit -m "fix(ci): prevent 301 redirects in test settings when DEBUG=False"
git commit -m "docs: Update security settings in backend README"
```

### Making Changes

#### Create Feature Branch
```bash
git checkout -b fix/feature-name
```

#### Commit and Push
```bash
git add <files>
git commit -m "feat: Description of changes"
git push origin fix/feature-name
```

#### Merge to Main
```bash
git checkout main
git pull origin main
git merge --no-ff fix/feature-name -m "merge: description"
git push origin main
```

### CI/CD Pipeline
- **Trigger:** Automatic on push to `main` or fix branches
- **Steps:**
  1. Checkout code
  2. Setup Python 3.12 + Node 20
  3. Install dependencies
  4. Run linting (ruff, eslint)
  5. Run backend tests (pytest)
  6. Run frontend build
  7. Run security audit (npm audit)
  8. Deploy to production (only if main branch)

---

## Important Notes

### Security Considerations
- **Never commit secrets** - Use `.env` template and environment variables
- **Test in CI environment** - Run tests with `DEBUG=False` to catch production issues
- **Dependency updates** - Use `npm audit` and `pip-audit` regularly
- **Admin credentials** - Never hardcode passwords in code
- **API authentication** - Only write operations require admin authentication

### Performance Optimization
- Frontend assets cached via Redis
- API responses paginated
- Database query optimization via select_related/prefetch_related
- Image conversion to WebP for smaller file sizes

### Database Considerations
- PostgreSQL recommended for production
- SQLite suitable for local development and testing
- Migrations required before deployment
- Backup database regularly
- Never delete migrations

### Code Quality
- All tests must pass before merge
- Linting errors must be fixed
- Zero npm/pip security vulnerabilities allowed
- Code coverage maintained above 80%
- Type hints required for Python functions

### Documentation Updates
- Update CHANGELOG.md for all significant changes
- Update README.md when behavior changes
- Update this guide for new procedures
- Document security changes thoroughly

---

## Quick Reference Commands

```bash
# Environment
source backend/.venv/bin/activate
cd frontend && npm ci

# Testing
pytest api/tests/ -v                   # Backend tests
npm run lint                           # Frontend linting
npm run build                          # Frontend build
npm audit --omit=dev                   # Security audit

# Development
docker compose up -d                   # Start services
docker compose logs -f backend         # View logs
python manage.py runserver             # Django dev server
npm run dev                            # Vite dev server

# Deployment
git push origin main                   # Trigger CI/CD
docker compose exec -T backend python manage.py migrate
docker compose ps                      # Check services

# Debugging
docker compose exec backend python manage.py shell
docker compose exec -T db psql -U portfolio -d portfolio_db
```

---

**Last Updated:** July 3, 2026
**Maintained by:** AI Development Team
**Questions?** Refer to specific service README.md files in respective directories.
