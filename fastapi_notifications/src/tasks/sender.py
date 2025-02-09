import sys

from celery import shared_task
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError
from pika.exchange_type import ExchangeType
from pika.spec import Basic, BasicProperties

from core.config import config
from core.logger import log

EXCHANGE_NAME = "topic_notifications"


@shared_task
def process_message(message: str):
    log.info(f"[🎉] the message '{message}' sent.")


@shared_task(bind=True)
def sender_task(self, name: str) -> None:
    try:
        log.info(f"\n{'-'*30}\n{name} launched.\n")
        credentials = PlainCredentials("user", "password")
        connection = BlockingConnection(
            ConnectionParameters(host="localhost", credentials=credentials)
        )
        channel = connection.channel()

        exchange_name = EXCHANGE_NAME
        channel.exchange_declare(
            exchange=exchange_name, exchange_type=ExchangeType.topic
        )
        # queue = channel.queue_declare(queue="", exclusive=True)
        # queue_name = queue.method.queue
        ###
        queue_name = "notifications"
        log.info(f"\nqueue_name: {queue_name}")

        binding_keys = ["#"]
        for binding_key in binding_keys:
            channel.queue_bind(
                exchange=exchange_name,
                queue=queue_name,
                routing_key=binding_key,
            )

        method_frame, header_frame, body = channel.basic_get(queue_name)
        log.info(
            f"\n(method_frame, header_frame, body): \n{(method_frame, header_frame, body)}\n\n"
        )
        if method_frame is not None:
            message_body = body.decode("utf-8")
            log.info(f"Got a message: {message_body}")

            # Celery task 'process_message'
            process_message.delay(message_body)

            # Confirmation of receipt of the message
            channel.basic_ack(method_frame.delivery_tag)

        connection.close()
        log.info(f"Connection closed.\n\n{'-'*30}\n")
    except AMQPConnectionError as err:
        log.info(f"An error connecting to RabbitMQ: {err}")
        raise
    except Exception as err:
        log.info(f"An unexpected error: {err}")
        raise
