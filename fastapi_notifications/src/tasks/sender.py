import asyncio
import sys

from aio_pika import ExchangeType, IncomingMessage, Message, connect_robust
from aio_pika.exceptions import (
    AMQPChannelError,
    AMQPConnectionError,
    QueueEmpty,
)
from celery import shared_task

from core.config import config
from core.logger import log

# from pika import BlockingConnection, ConnectionParameters, PlainCredentials
# from pika.adapters.blocking_connection import BlockingChannel
# from pika.exceptions import AMQPConnectionError
# from pika.exchange_type import ExchangeType
# from pika.spec import Basic, BasicProperties

EXCHANGE_NAME = "topic_notifications"


# @shared_task
# def process_message(message: str):
#     log.info(f"[🎉] the message '{message}' sent.")


async def process_message(message: str) -> None:
    log.info(f"[🎉] the message '{message}' sent.")


async def queue_get_messages():
    try:
        log.info(f"Connecting to RabbitMQ...")

        connection = await connect_robust(config.broker.connection)
        async with connection:
            channel = await connection.channel()
            log.debug(f"Connected successfully to RabbitMQ.")

            exchange_name = EXCHANGE_NAME
            exchange = await channel.declare_exchange(
                name=exchange_name, type=ExchangeType.TOPIC
            )

            queue_name = "notifications"
            log.info(f"\nqueue_name: {queue_name}")
            queue = await channel.declare_queue(name=queue_name, durable=True)
            await queue.bind(exchange, "#")

            batch_size = 1_000
            counter = 0
            while counter < batch_size:
                try:
                    message = await queue.get(timeout=1)
                    message_body = message.body.decode("utf-8")
                    log.info(f"Got a message: {message_body}")

                    # Celery task 'process_message'
                    await process_message(message_body)

                    # Confirmation of receipt of the message
                    await message.ack()
                    counter += 1
                except QueueEmpty:
                    log.info("\nNo messages available.\n")
                    break

        log.info(f"Connection closed.\n\n{'-'*30}\n")
    except (AMQPConnectionError, AMQPChannelError) as err:
        log.info(f"An error connecting to RabbitMQ: {err}")
        raise
    except Exception as err:
        log.info(f"An unexpected error: {err}")
        raise


async def sender_main():
    task = asyncio.create_task(queue_get_messages())
    await task


@shared_task(bind=True)
def sender_task(self, name: str) -> None:
    log.info(f"\n{'-'*30}\n{name} launched.\n")
    asyncio.run(sender_main())
