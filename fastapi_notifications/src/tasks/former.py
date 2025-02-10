import asyncio
import random
from time import sleep

from celery import shared_task
from kombu import Connection, Exchange, Queue
from kombu.pools import producers
from kombu.utils.compat import nested
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exceptions import AMQPChannelError, AMQPConnectionError
from pika.exchange_type import ExchangeType

from core.config import config
from core.constants import EXCHANGE_NAME, QUEUE_NAME
from core.logger import log
from services.notifications import (
    NotificationsService,
    get_notifications_service,
)

EXCHANGE_NAME = "topic_notifications"
ROUTING_KEYS = [
    "notification.instant.telegram",
    "notification.instant.email",
    "notification.delayed.email",
]
COUNTER = 1


async def send_notification_task(
    message: str,
    exchange_name: str = EXCHANGE_NAME,
    queue_name: str = QUEUE_NAME,
):
    notifications_service = NotificationsService()
    # await notifications_service.initialize_connection_pool()
    await notifications_service.add_notification_task(
        message, exchange_name, queue_name
    )


async def former_main() -> None:

    global COUNTER
    task = asyncio.create_task(
        send_notification_task(f"message_example {COUNTER}")
    )
    COUNTER += 1
    await task


@shared_task(bind=True)
def former_task(
    self,
    name: str,
) -> None:
    log.info(f"\n{'-'*30}\n{name} launched.\n")

    asyncio.run(former_main())
