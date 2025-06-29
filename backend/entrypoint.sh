#!/bin/bash
set -e

# Wait for the database to be ready
until pg_isready -h db -p 5432 -U portfolio; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Apply migrations
python manage.py migrate --noinput

# Optionally collect static files if they need runtime updates
python manage.py collectstatic --noinput

# Start Gunicorn (CMD arguments are passed via exec)
exec "$@"
