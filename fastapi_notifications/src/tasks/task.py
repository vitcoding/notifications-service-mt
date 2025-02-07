import random
from time import sleep

from celery import shared_task
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exchange_type import ExchangeType

from core.config import config
from core.logger import log

EXCHANGE_NAME = "topic_notifications"
COUNTER = 0


@shared_task()
def task_add(message: str, delay: int) -> None:
    credentials = PlainCredentials("user", "password")
    connection = BlockingConnection(
        ConnectionParameters(host="localhost", credentials=credentials)
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE_NAME, exchange_type=ExchangeType.topic
    )
    global COUNTER
    counter = COUNTER
    routing_key = random.choice(
        [
            "notification.instant.telegram",
            "notification.instant.email",
            "notification.delayed.email",
        ]
    )

    log.info(f"Sleeping for {delay} sec...")
    sleep(delay)

    message_body = (
        f"Routing key: {routing_key=:<30}: {counter}\nMessage: {message}"
    )
    channel.basic_publish(
        exchange=EXCHANGE_NAME, routing_key=routing_key, body=message_body
    )
    COUNTER += 1
    log.info(f"\n[✅] {message_body}")
