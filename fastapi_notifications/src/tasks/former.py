import asyncio
import json
from uuid import UUID

import httpx
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


async def get_access_token():
    async with httpx.AsyncClient() as client:
        url = "http://localhost:8001/api/v1/auth/login"
        json_data = {"login": "admin", "password": "admin"}
        response = await client.post(url=url, json=json_data)
        return response.cookies.get("users_access_token")


async def get_profile_data(
    notification_task: NotificationTask,
) -> NotificationTask:
    access_token = await get_access_token()
    log.info(f"\nget_profile_data: \nusers_access_token: {access_token}\n")

    async with httpx.AsyncClient() as client:
        user_id = notification_task.user_id
        url = f"http://localhost:8001/api/v1/admin/users/{user_id}"
        admin_cookies = {"users_access_token": access_token}
        response = await client.get(url=url, cookies=admin_cookies)
        log.info(f"\nget_profile_data: \nresponse: {response.content}\n")


async def update_profile_data(
    notification_task: NotificationTask,
) -> NotificationTask:
    await get_profile_data(notification_task)


async def form_task(message: str) -> NotificationTask:
    log.info(f"\nformer: \nmessage: {message}\n")
    broker_service_temp = BrokerService()
    connection_temp = await connect_robust(config.broker.connection)
    notification_task = NotificationTask(**json.loads(message))

    # notification_task.user_name = "login"
    # notification_task.user_email = "email@email"
    await update_profile_data(notification_task)

    async with connection_temp:
        await broker_service_temp.publish(
            connection_temp,
            EXCHANGES.FORMED_TASKS,
            QUEUES.FORMED_TASKS,
            notification_task,
        )


async def form_tasks() -> None:
    broker_service = BrokerService()
    await broker_service.get_messages(
        EXCHANGES.CREATED_TASKS,
        QUEUES.CREATED_TASKS,
        form_task,
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
