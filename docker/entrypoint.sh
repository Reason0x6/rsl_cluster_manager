#!/bin/bash
set -e

echo "Current directory: $(pwd)"
echo "Listing directory contents:"
ls -la

# Wait for postgres
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
    sleep 1
done
echo "PostgreSQL started"

# Run migrations
echo "Running database migrations..."
python /app/manage.py migrate

# Start Django development server
echo "Starting Django server..."
exec python /app/manage.py runserver 0.0.0.0:8000