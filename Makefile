# rabbitmq
# http://localhost:15672/

# rabbitmq
RBT-DC = rabbitmq/docker-compose-rabbitmq.yml
RBT-NAME = rabbitmq

# network
net-create:
	docker network create shared-network
net-rm:
	docker network rm shared-network

# all
up:
	make net-create
	make up-$(RBT-NAME)
destroy:
	make destroy-$(RBT-NAME)
	make net-rm


# rabbitmq
up-$(RBT-NAME):
	docker compose -f $(RBT-DC) up -d --build --force-recreate
destroy-$(RBT-NAME):
	docker compose -f $(RBT-DC) down -v


# open project (vs code)
notifications-prj:
	code notifications