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

# Wait for ChromaDB to be ready
echo "Waiting for ChromaDB to be ready..."
until curl -s -o /dev/null -w "%{http_code}" http://chromadb:8000/api/v1/heartbeat | grep -q 200; do
  echo "Waiting for ChromaDB..."
  sleep 2
done

# Index content on chromadb (non-fatal)
python manage.py index_content --reindex || echo "Warning: Content indexing failed, continuing..."

# Start Gunicorn (CMD arguments are passed via exec)
exec "$@"
