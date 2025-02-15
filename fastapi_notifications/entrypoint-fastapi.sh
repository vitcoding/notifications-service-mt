#!/usr/bin/env bash

set -e

echo "Waiting for PostgreSQL to start..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 0.5
done

echo "PostgreSQL started"


alembic upgrade head

gunicorn -c gunicorn.conf.py main:app
