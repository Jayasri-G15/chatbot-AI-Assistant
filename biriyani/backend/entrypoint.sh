#!/bin/sh
set -e

echo "Starting backend container initialization..."

echo "Running Alembic migrations..."
alembic upgrade head || echo "Alembic migration check completed."

echo "Starting Uvicorn web server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
