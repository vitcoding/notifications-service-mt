# notifications-service
# http://localhost:8006/api/openapi
# auth url
# http://localhost:8001/api/openapi
# rabbitmq
# http://localhost:15672/
# Auth data: {User: user, Password: password}


# ntf (notifications) service
NTF-DC = fastapi_notifications/docker-compose-notifications.yml
NTF-NAME = ntf
NTF-SERVICE-NAME = notifications-service
NTF-SCHEDULER-NAME = notifications-scheduler
NTF-SENDER-NAME = notifications-sender
# rabbitmq
RBT-DC = rabbitmq/docker-compose-rabbitmq.yml
RBT-NAME = rabbitmq
# auth
AUTH-DC = fastapi_auth/docker-compose-auth.yml
AUTH-NAME = auth
AUTH-SERVICE-NAME = auth-service


# network
net-create:
	docker network create shared-network
net-rm:
	docker network rm shared-network

# all
up:
	make net-create
	make up-$(RBT-NAME)
	make up-$(NTF-NAME)
	make up-$(AUTH-NAME)
destroy:
	make destroy-$(NTF-NAME)
	make destroy-$(AUTH-NAME)
	make destroy-$(RBT-NAME)
	make net-rm
stop:
	make stop-$(NTF-NAME)
	make stop-$(AUTH-NAME)
	make stop-$(RBT-NAME)
start:
	make start-$(NTF-NAME)
	make start-$(AUTH-NAME)
	make start-$(RBT-NAME)


# NTF-NAME = ntf # notifications
up-$(NTF-NAME):
	docker compose -f $(NTF-DC) up -d --build --force-recreate
destroy-$(NTF-NAME):
	docker compose -f $(NTF-DC) down -v
stop-$(NTF-NAME):
	docker compose -f $(NTF-DC) stop
start-$(NTF-NAME):
	docker compose -f $(NTF-DC) start
rebuild-$(NTF-NAME):
	make rebuild-$(NTF-NAME)-service
	make rebuild-$(NTF-NAME)-scheduler
	make rebuild-$(NTF-NAME)-sender

tests-$(NTF-NAME):
	make net-create
	make up-rabbitmq
	docker compose -f fastapi_notifications/src/tests/docker-compose.yml up -d --build --force-recreate
	docker logs -f tests
	docker compose -f fastapi_notifications/src/tests/docker-compose.yml down -v
	make destroy-rabbitmq
	make net-rm

rebuild-$(NTF-NAME)-service:
	docker compose -f $(NTF-DC) stop $(NTF-SERVICE-NAME)
	docker compose -f $(NTF-DC) rm -f $(NTF-SERVICE-NAME)
	docker compose -f $(NTF-DC) build $(NTF-SERVICE-NAME)
	docker compose -f $(NTF-DC) up -d $(NTF-SERVICE-NAME)
rebuild-$(NTF-NAME)-scheduler:
	docker compose -f $(NTF-DC) stop $(NTF-SCHEDULER-NAME)
	docker compose -f $(NTF-DC) rm -f $(NTF-SCHEDULER-NAME)
	docker compose -f $(NTF-DC) build $(NTF-SCHEDULER-NAME)
	docker compose -f $(NTF-DC) up -d $(NTF-SCHEDULER-NAME)
rebuild-$(NTF-NAME)-sender:
	docker compose -f $(NTF-DC) stop $(NTF-SENDER-NAME)
	docker compose -f $(NTF-DC) rm -f $(NTF-SENDER-NAME)
	docker compose -f $(NTF-DC) build $(NTF-SENDER-NAME)
	docker compose -f $(NTF-DC) up -d $(NTF-SENDER-NAME)

# debug-mode (db & cache: docker, fastapi: prj)
up-$(NTF-NAME)-db:
	docker compose -f fastapi_notifications/docker-compose.debug.yml up -d --build --force-recreate
	sleep 2
	make ntf-prj
destroy-$(NTF-NAME)-db:
	docker compose -f fastapi_notifications/docker-compose.debug.yml down -v
stop-$(NTF-NAME)-db:
	docker compose -f fastapi_notifications/docker-compose.debug.yml stop
start-$(NTF-NAME)-db:
	docker compose -f fastapi_notifications/docker-compose.debug.yml start


# rabbitmq
up-$(RBT-NAME):
	docker compose -f $(RBT-DC) up -d --build --force-recreate
destroy-$(RBT-NAME):
	docker compose -f $(RBT-DC) down -v
stop-$(RBT-NAME):
	docker compose -f $(RBT-DC) stop
start-$(RBT-NAME):
	docker compose -f $(RBT-DC) start

# AUTH-NAME = auth
up-$(AUTH-NAME):
	docker compose -f $(AUTH-DC) up -d --build --force-recreate
destroy-$(AUTH-NAME):
	docker compose -f $(AUTH-DC) down -v
rebuild-$(AUTH-NAME):
	docker compose -f $(AUTH-DC) stop $(AUTH-SERVICE-NAME)
	docker compose -f $(AUTH-DC) rm -f $(AUTH-SERVICE-NAME)
	docker compose -f $(AUTH-DC) build $(AUTH-SERVICE-NAME)
	docker compose -f $(AUTH-DC) up -d $(AUTH-SERVICE-NAME)

stop-$(AUTH-NAME):
	docker compose -f $(AUTH-DC) stop
start-$(AUTH-NAME):
	docker compose -f $(AUTH-DC) start


# open project (vs code)
ntf-prj:
	code fastapi_notifications/src
auth-prj:
	code fastapi_auth/src


# other
dc-prune:
	docker system prune -a -f


# all-db (debug)
up-db:
	make net-create
	make up-$(RBT-NAME)
	make up-$(AUTH-NAME)
	make up-$(NTF-NAME)-db
destroy-db:
	make destroy-$(NTF-NAME)-db
	make destroy-$(AUTH-NAME)
	make destroy-$(RBT-NAME)
	make net-rm
stop-db:
	make stop-$(NTF-NAME)-db
	make stop-$(AUTH-NAME)
	make stop-$(RBT-NAME)
start-db:
	make start-$(RBT-NAME)
	make start-$(NTF-NAME)-db
	make start-$(AUTH-NAME)