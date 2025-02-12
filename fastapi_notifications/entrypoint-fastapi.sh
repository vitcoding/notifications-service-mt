#!/usr/bin/env bash

set -e

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 0.5
done


alembic upgrade head

gunicorn -c gunicorn.conf.py main:app
