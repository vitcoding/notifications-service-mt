run:
	gunicorn -c gunicorn.conf.py main:app

debug:
	python -c "from core.logger import configure_logging; \
	configure_logging(); from core.logger import log; import uvicorn; \
	uvicorn.run('main:app', host='0.0.0.0', port=8006, reload=True);"

debug_no_logger:
	uvicorn main:app --host 0.0.0.0 --port 8006 --reload 

# migrations:
# 	alembic revision --autogenerate -m <name>

migrate:
	alembic upgrade head


celery-beat:
	celery -A main.celery_app beat --loglevel=INFO
celery-worker:
	celery -A main.celery_app worker --loglevel=INFO

clean:
	rm -f _temp/logs/logs.log