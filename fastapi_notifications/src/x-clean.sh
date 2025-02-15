#!/usr/bin/env bash

rm -f _temp/logs/logs.log celerybeat-schedule

find . | grep -E "__pycache__" | xargs rm -rf
