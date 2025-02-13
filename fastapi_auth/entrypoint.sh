#!/usr/bin/env bash

set -e

 while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
     sleep 0.5
 done

 while ! nc -z $REDIS_HOST $REDIS_PORT; do
     sleep 0.5
 done

alembic upgrade head

python3 create_superuser.py admin admin

gunicorn -c gunicorn.conf.py main:app
