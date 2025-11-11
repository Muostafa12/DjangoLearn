#!/bin/bash
# Docker entrypoint script to ensure database is ready and migrations are run

set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; do
  sleep 1
done
echo "✓ PostgreSQL is ready"

echo "Waiting for Redis..."
while ! redis-cli -h $REDIS_HOST -p $REDIS_PORT ping > /dev/null 2>&1; do
  sleep 1
done
echo "✓ Redis is ready"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✓ Setup complete"

# Execute the main command
exec "$@"
