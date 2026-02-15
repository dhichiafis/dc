#!/bin/sh
# migrate-entrypoint.sh

echo "Waiting for database to be ready..."
# Replace "db" with your service name in docker-compose.yml
while ! nc -z db 5432; do
  sleep 1
done

echo "Database is up! Running Alembic migrations..."
python -m alembic upgrade head

echo "Migrations complete!"
