#!/usr/bin/env bash

set -e

celery -A main.scheduler_app worker --loglevel=INFO
