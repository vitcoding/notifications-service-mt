# rabbitmq
# http://localhost:15672/

up:
	docker compose up -d --build --force-recreate
destroy:
	docker compose down -v

app-prj:
	code app