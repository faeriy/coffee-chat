# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**coffee-chat** is a full-stack chat application with JWT + Google OAuth authentication. Stack: FastAPI (Python 3.12) backend, React 19 + TypeScript frontend, PostgreSQL database, Docker Compose for orchestration.

## Development Commands

### Running the Full Stack

```bash
docker-compose up          # Start all services (postgres, api, frontend)
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# Admin UI: http://localhost:8000/admin
# Default test user: coffee / coffee (auto-created on startup)
```

### Backend (from `backend/`)

```bash
poetry install                          # Install dependencies
poetry run uvicorn app.main:app --reload  # Dev server on :8000
poetry run alembic upgrade head         # Apply DB migrations
poetry run alembic revision --autogenerate -m "description"  # New migration
poetry run pytest                       # Run all tests
poetry run pytest path/to/test.py::test_name  # Run single test
poetry run black .                      # Format code
poetry run isort .                      # Sort imports
poetry run pyright                      # Type check (app/ only)
```

### Frontend (from `frontend/`)

```bash
npm install
npm run dev       # Vite dev server on :5173
npm run build     # Type-check + production build
npm run lint      # ESLint check
npm run preview   # Preview production build
```

### Pre-commit Hooks

```bash
pre-commit install        # Install hooks (run once after cloning)
pre-commit run --all-files  # Run all hooks manually
```

Hooks enforce: Black formatting, isort imports, trailing whitespace, valid YAML/JSON/TOML, no large files.

## Architecture

### Backend (`backend/app/`)

- **`main.py`** — FastAPI app entry, CORS/session middleware, lifespan hook (creates test user), mounts SQLAdmin at `/admin/`
- **`config.py`** — Pydantic Settings loaded from `backend/.env`; all secrets/URLs live here
- **`database.py`** — SQLAlchemy async engine setup; `get_db` dependency for FastAPI routes
- **`models/user.py`** — Single `User` model: `id`, `username`, `email`, `hashed_password` (nullable for OAuth users), `google_id`, `created_at`
- **`routes/auth.py`** — `/auth/login` (JWT), `/auth/register`, `/auth/google` (OAuth redirect), `/auth/google/callback`
- **`api/websocket.py`** — WebSocket endpoint (infrastructure present, not yet fully utilized)
- **`api/routes/files.py`** — S3 file upload endpoint
- **`utils/security.py`** — JWT creation/verification, bcrypt password hashing
- **`services/s3_service.py`** — AWS S3 integration via boto3
- **`admin/`** — SQLAdmin views with custom auth

### Frontend (`frontend/src/`)

- **`App.tsx`** — Root component: reads JWT from `localStorage`, handles Google OAuth redirect (token in URL param), conditionally renders `LoginPage` or `ChatExamplesPage`
- **`LoginPage.tsx`** — Username/password form + Google OAuth button
- **`ChatExamplesPage.tsx`** — Authenticated view; fetches `/users/me` to show current user
- **`apiClient.ts`** — Axios instance; base URL from `VITE_API_URL` env var (default `http://localhost:8000`)
- **`services/websocket.ts`** — Native WebSocket wrapper
- **`services/socketIo.ts`** — Socket.io-client integration

### Auth Flow

1. **JWT**: `POST /auth/login` → JWT stored in `localStorage` → sent as `Authorization: Bearer <token>` header
2. **Google OAuth**: Frontend → `GET /auth/google` → Google → `GET /auth/google/callback` → redirects to frontend with `?token=<jwt>` in URL → `App.tsx` extracts and stores token

### Database Migrations

Migrations live in `backend/alembic/versions/`. Always run `alembic upgrade head` before starting the backend outside Docker (Docker's `entrypoint.sh` does this automatically).

## Environment Configuration

Create `backend/.env` with:

```env
DATABASE_URL=postgresql://coffeechat:coffeechat@localhost:5432/coffeechat
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=          # optional, for Google OAuth
GOOGLE_CLIENT_SECRET=      # optional, for Google OAuth
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
AWS_ACCESS_KEY_ID=         # optional, for S3
AWS_SECRET_ACCESS_KEY=     # optional, for S3
S3_BUCKET_NAME=            # optional, for S3
```

Frontend env vars go in `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Key Conventions

- **Python**: Black (88 chars), isort with black profile, Pyright in basic mode targeting `app/` only
- **TypeScript**: ESLint flat config; React Hooks and React Refresh plugins enforced
- **Ant Design** is the UI component library — use `antd` components for all UI, with primary color `#00b96b`
- **Optional features**: Google OAuth, S3 storage, and WebSockets are all wired up but require environment variables; the app runs without them
- **Admin credentials** for `/admin/` are configured in `backend/app/admin/auth.py`
