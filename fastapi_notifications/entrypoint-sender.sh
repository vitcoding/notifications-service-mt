#!/usr/bin/env bash

set -e

celery -A main.sender_app worker -B --loglevel=INFO
