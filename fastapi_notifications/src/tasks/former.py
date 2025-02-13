import asyncio
import json
from uuid import UUID

from aio_pika import connect_robust
from celery import shared_task

from core.config import config
from core.constants import EXCHANGES, QUEUES
from core.logger import log
from db.postgres import get_db_session
from models.notification import Notification
from schemas.notifications import NotificationTask
from services.broker import BrokerService
from services.database import RepositoryDB


async def get_profile_data(message: str) -> NotificationTask:
    log.info(f"\nformer: \nmessage: {message}\n")
    broker_service_temp = BrokerService()
    connection_temp = await connect_robust(config.broker.connection)
    notification_task = NotificationTask(**json.loads(message))

    notification_task.user_name = "login"
    notification_task.user_email = "email@email"

    async with connection_temp:
        await broker_service_temp.publish(
            connection_temp,
            EXCHANGES.FORMED_TASKS,
            QUEUES.FORMED_TASKS,
            notification_task,
        )


async def publish_notification_task(notification_task):
    broker_service2 = BrokerService()
    connection = await connect_robust(config.broker.connection)
    async with connection:
        await broker_service2.publish(
            connection,
            EXCHANGES.FORMED_TASKS,
            QUEUES.FORMED_TASKS,
            notification_task,
        )


async def form_tasks() -> None:
    broker_service = BrokerService()
    await broker_service.get_messages(
        EXCHANGES.CREATED_TASKS,
        QUEUES.CREATED_TASKS,
        get_profile_data,
        batch_size=1000,
    )


async def former_main() -> None:

    task = asyncio.create_task(form_tasks())
    await task


@shared_task(bind=True)
def former_task(self, name: str, do_tasks: bool = False) -> None:
    log.info(f"\n{'-'*30}\n{name} launched.\n")

    do_tasks = True
    if do_tasks:
        asyncio.run(former_main())

    log.info(f"\n\n{'-'*30}\n")
