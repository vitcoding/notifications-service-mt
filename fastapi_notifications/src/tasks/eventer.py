import asyncio
from random import randint

from celery import shared_task

from core.config import config
from core.logger import log
from schemas.notifications import NotificationCreateDto
from scripts.generate_events import generate_notifications
from services.notifications import NotificationsService


async def events_generator() -> None:
    """Generates notifications (debug)."""

    notifications_tasks_created = [
        NotificationCreateDto(**ntf_task)
        for ntf_task in generate_notifications(quantity=randint(10, 100))
    ]

    notifications_service = NotificationsService()
    for created_task in notifications_tasks_created:
        await notifications_service.add_notification_task(created_task)


async def get_events() -> None:
    """Gets events."""

    if config.globals.generate_events:
        await events_generator()
    else:
        # kafka consumer or api requests functions
        pass


async def eventer_main() -> None:
    """The eventer main function."""

    task = asyncio.create_task(get_events())
    await task


@shared_task(bind=True)
def eventer_task(self, name: str, do_tasks: bool = False) -> None:
    """A celery worker eventer task."""

    log.info(f"\n{'-'*30}\n{name} launched.\n")

    do_tasks = True  # for debug
    if do_tasks:
        asyncio.run(eventer_main())

    log.info(f"\n\n{'-'*30}\n")
