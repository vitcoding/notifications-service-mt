# rabbitmq
# http://localhost:15672/

# rabbitmq
RBT-DC = rabbitmq/docker-compose-rabbitmq.yml
RBT-NAME = rabbitmq
# ntf (notifications)
NTF-DC = fastapi_notifications/docker-compose-notifications.yml
NTF-NAME = ntf
NTF-SERVICE-NAME = notifications-service

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
destroy:
	make destroy-$(NTF-NAME)
	make destroy-$(RBT-NAME)
	make net-rm

# NTF-NAME = ntf # notifications
up-$(NTF-NAME):
	docker compose -f $(NTF-DC) up -d --build --force-recreate
destroy-$(NTF-NAME):
	docker compose -f $(NTF-DC) down -v
rebuild-$(NTF-NAME):
	docker compose -f $(NTF-DC) stop $(NTF-SERVICE-NAME)
	docker compose -f $(NTF-DC) rm -f $(NTF-SERVICE-NAME)
	docker compose -f $(NTF-DC) build $(NTF-SERVICE-NAME)
	docker compose -f $(NTF-DC) up -d $(NTF-SERVICE-NAME)

# rabbitmq
up-$(RBT-NAME):
	docker compose -f $(RBT-DC) up -d --build --force-recreate
destroy-$(RBT-NAME):
	docker compose -f $(RBT-DC) down -v


# open project (vs code)
ntf-prj:
	code fastapi_notifications/src