import asyncio

from aio_pika import connect_robust
from celery import shared_task
from fastapi import Depends

from core.config import config
from core.constants import EXCHANGE_NAME, QUEUE_NAME
from core.logger import log
from schemas.notifications import NotificationTask
from services.notifications import broker_publisher

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
    message_data = {
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "user_name": "UserName",
        "user_email": "email",
        "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "subject": "Title",
        "message": message,
        "notification_type": "email",
    }
    notification_task = NotificationTask(**message_data)
    connection = await connect_robust(config.broker.connection)
    async with connection:
        await broker_publisher(
            connection, exchange_name, queue_name, notification_task
        )


async def former_main() -> None:

    global COUNTER
    task = asyncio.create_task(
        send_notification_task(f"message_example {COUNTER}")
    )
    COUNTER += 1
    await task


@shared_task(bind=True)
def former_task(self, name: str, do_tasks: bool = False) -> None:
    log.info(f"\n{'-'*30}\n{name} launched.\n")

    do_tasks = True
    if do_tasks:
        asyncio.run(former_main())
