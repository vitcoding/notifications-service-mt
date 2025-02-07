#!/usr/bin/env bash

set -e

celery -A main.celery_app worker --loglevel=INFO
