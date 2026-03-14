#!/bin/sh
# Entrypoint: run migrations, create test user (coffee/coffee), then start FastAPI.
# Like Django's migrate + createsuperuser + runserver in one go for easy local testing.
set -e

cd /app

echo "Running database migrations..."
poetry run alembic upgrade head

echo "Starting API (test user coffee/coffee is created on first request or at startup)..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
