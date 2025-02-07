run:
	gunicorn -c gunicorn.conf.py main:app

debug:
	python -c "from core.logger import configure_logging; \
	configure_logging(); from core.logger import log; import uvicorn; \
	uvicorn.run('main:app', host='0.0.0.0', port=8006, reload=True);"

debug_no_logger:
	uvicorn main:app --host 0.0.0.0 --port 8006 --reload 

scheduler:
	celery -A main.scheduler_app worker --loglevel=INFO

# # mypy
# mypy:
# 	mypy .

# mypy-service:
# 	mypy . --exclude tests/functional