#!/usr/bin/env bash

rm -f _temp/outputs/output_other.log _temp/outputs/output_email.log \
    celerybeat-schedule

find . | grep -E "__pycache__" | xargs rm -rf
