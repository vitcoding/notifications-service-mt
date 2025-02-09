import random
from time import sleep

from celery import shared_task
from kombu import Connection, Exchange, Queue
from kombu.pools import producers
from kombu.utils.compat import nested
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exceptions import AMQPConnectionError
from pika.exchange_type import ExchangeType

from core.config import config
from core.logger import log

EXCHANGE_NAME = "topic_notifications"
ROUTING_KEYS = [
    "notification.instant.telegram",
    "notification.instant.email",
    "notification.delayed.email",
]


@shared_task(bind=True)
def task_add(self, message: str, delay: int) -> None:
    try:
        with Connection(config.broker.connection) as conn:
            exchange = Exchange(
                name=EXCHANGE_NAME, type="topic", durable=False
            )
            # queue = Queue(name="", exchange=exchange, routing_key="#")
            queue = Queue(
                name="notifications", exchange=exchange, routing_key="#"
            )

            with producers[conn].acquire(block=True) as producer:
                log.info(f"Sleeping for {delay} seconds...")
                sleep(delay)

                routing_key = random.choice(ROUTING_KEYS)
                message_body = (
                    f"Routing key: {routing_key:<30}\nMessage: {message}"
                )
                producer.publish(
                    body=message_body,
                    exchange=exchange.name,
                    routing_key=routing_key,
                    declare=[queue],
                    retry=True,
                )
                log.info(f"\n[✅] {message_body}")
    except AMQPConnectionError as err:
        log.info(f"An error connecting to RabbitMQ: {err}")
        raise
    except Exception as err:
        log.info(f"An unexpected error: {err}")
        raise
