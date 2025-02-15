#!/usr/bin/env bash

rm -f _temp/logs/logs.log

terminator --title="FastAPI" -e 'echo FastAPI; \
            source .venv/bin/activate; \
            uvicorn main:app --host 0.0.0.0 --port 8006 --reload; \
            exec bash' &
terminator --title="Worker" -e 'echo Celery Worker; \
            source .venv/bin/activate; \
            celery -A main.celery_app worker --loglevel=INFO; \
            exec bash' &
terminator --title="Scheduler" \
            -e 'echo Celery Scheduler; \
            source .venv/bin/activate; \
            celery -A main.celery_app beat --loglevel=INFO; \
            exec bash' &
