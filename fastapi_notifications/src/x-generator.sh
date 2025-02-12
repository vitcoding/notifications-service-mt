#!/usr/bin/env bash

rm -f _temp/logs/logs.log

terminator --title="Messages Generator" -e 'echo Messages Generator; \
            source .venv/bin/activate; \
            python scripts/send_messages.py; \
            exec bash' &
