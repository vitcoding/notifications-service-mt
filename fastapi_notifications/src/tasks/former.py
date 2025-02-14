import asyncio
import json

import httpx
from aio_pika import connect_robust
from celery import shared_task

from core.config import config
from core.constants import EXCHANGES, QUEUES
from core.logger import log
from schemas.notifications import NotificationTask, NotificationUpdateDto
from schemas.user import UserAuth
from services.broker import BrokerService
from services.notifications import NotificationsService


async def get_access_token():
    """Gets an access token."""

    async with httpx.AsyncClient() as client:
        url = "http://localhost:8001/api/v1/auth/login"
        json_data = {"login": "admin", "password": "admin"}
        response = await client.post(url=url, json=json_data)

        users_access_token = response.cookies.get("users_access_token")
        return users_access_token


async def get_profile_data(
    notification_task: NotificationTask,
) -> NotificationTask:
    """Gets the user profile data."""

    access_token = await get_access_token()
    log.info(
        f"\n{__name__}: {get_profile_data.__name__}: \n"
        f"users_access_token: {access_token}\n"
    )

    user_id = notification_task.user_id
    url = f"http://localhost:8001/api/v1/admin/users/{user_id}"
    admin_cookies = {"users_access_token": access_token}
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, cookies=admin_cookies)
        profile = response.content

    log.info(
        f"\n{__name__}: {get_profile_data.__name__}: \n"
        f"profile: {profile}\n"
    )
    return profile


async def update_profile_data(
    notification_task: NotificationTask,
) -> NotificationTask:
    """Updates notification task with the user profile data."""

    profile_response = await get_profile_data(notification_task)
    profile = UserAuth(**json.loads(profile_response))

    notification_update = NotificationUpdateDto(
        user_name=profile.first_name, user_email=profile.email
    )

    notifications_service = NotificationsService()
    notification = await notifications_service.update_notification(
        notification_task.id, notification_update
    )
    notification_task_updated = NotificationTask(**notification.model_dump())
    return notification_task_updated


async def form_task(message: str) -> None:
    """Forms notification task."""

    log.info(f"\n{__name__}: {form_task.__name__}: \nmessage: {message}\n")
    broker_service_temp = BrokerService()
    connection_temp = await connect_robust(config.broker.connection)
    notification_task_created = NotificationTask(**json.loads(message))

    notification_task_updated = await update_profile_data(
        notification_task_created
    )
    log.info(
        f"\n{__name__}: {form_task.__name__}: \nnotification_task_updated: "
        f"{notification_task_updated.model_dump()}\n"
    )

    async with connection_temp:
        await broker_service_temp.publish(
            connection_temp,
            EXCHANGES.FORMED_TASKS,
            QUEUES.FORMED_TASKS,
            notification_task_updated,
        )


async def form_tasks() -> None:
    """Forms notifications tasks."""

    broker_service = BrokerService()
    await broker_service.get_messages(
        EXCHANGES.CREATED_TASKS,
        QUEUES.CREATED_TASKS,
        form_task,
        batch_size=50,
    )


async def former_main() -> None:
    """The former main function."""

    task = asyncio.create_task(form_tasks())
    await task


@shared_task(bind=True)
def former_task(self, name: str, do_tasks: bool = False) -> None:
    """A celery worker former task."""

    log.info(f"\n{'-'*30}\n{name} launched.\n")

    do_tasks = True
    if do_tasks:
        asyncio.run(former_main())

    log.info(f"\n\n{'-'*30}\n")
