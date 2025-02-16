import asyncio
import json
import os
from datetime import datetime, timezone

from celery import shared_task

from core.config import config
from core.constants import EXCHANGES, QUEUES
from core.logger import log
from schemas.notifications import NotificationTask, NotificationUpdateTimeDto
from services.broker import BrokerService
from services.notifications import NotificationsService


async def process_message(message: str) -> None:
    """Processes a message from the broker."""

    log.info(
        f"\n{__name__}: {process_message.__name__}: "
        f"\n[🎉🎉🎉🎉🎉🎉🎉] \nthe message '{message}' sent."
    )

    file_path = "./_temp/logs/output.log"
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(file_path, mode="a", encoding="utf-8") as fwa:
        fwa.writelines(f"{timestamp}: {message}\n")

    notification_task = NotificationTask(**json.loads(message))
    notification_id = notification_task.id
    notification_update = NotificationUpdateTimeDto(last_sent_at=timestamp)

    notifications_service = NotificationsService()
    await notifications_service.update_notification(
        notification_id, notification_update
    )


async def queue_get_messages(
    exchange_name: str = EXCHANGES.FORMED_TASKS,
    queue_name: str = QUEUES.FORMED_TASKS,
) -> None:
    """Gets messages from the broker."""

    log.info(
        f"\n{__name__}: {queue_get_messages.__name__}: "
        f"Checking for new messages..."
    )

    broker_service = BrokerService()
    await broker_service.get_messages(
        exchange_name, queue_name, process_message
    )


async def sender_main() -> None:
    """The sender main function."""

    task = asyncio.create_task(queue_get_messages())
    await task


@shared_task(bind=True)
def sender_task(self, name: str) -> None:
    """A celery worker sender task."""

    log.info(f"\n{'-'*30}\n{name} launched.\n")

    asyncio.run(sender_main())

    log.info(f"\n\n{'-'*30}\n")
