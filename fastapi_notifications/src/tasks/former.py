import asyncio

from celery import shared_task

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
    notifications_service = get_notifications_service()
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
def former_task(self, name: str, do_tasks: bool = False) -> None:
    log.info(f"\n{'-'*30}\n{name} launched.\n")

    # do_tasks = True
    if do_tasks:
        asyncio.run(former_main())
