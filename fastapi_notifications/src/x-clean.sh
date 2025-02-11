#!/usr/bin/env bash

rm -f _temp/logs/logs.log celerybeat-schedule

find . | grep -E "__pycache__" | xargs rm -rf

# find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
# find . -name '__pycache__' -type d -exec rm -rf {} \