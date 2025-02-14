import json
from functools import lru_cache
from typing import Any
from uuid import UUID

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.exceptions import AMQPChannelError, AMQPConnectionError
from aio_pika.pool import Pool
from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from core.config import config
from core.constants import EXCHANGES, QUEUES
from core.logger import log
from db.postgres import get_db_session
from db.redis import get_client
from models.notification import Notification
from schemas.notifications import (
    NotificationCreateDto,
    NotificationDBView,
    NotificationTask,
    NotificationTaskCreate,
    NotificationUpdateDto,
)
from services.broker import BrokerService
from services.cache import CacheService
from services.database import RepositoryDB
from services.pagination import PaginationParams

CACHE_EXPIRE_IN_SECONDS = 60 * 60 * 24


class NotificationsService:
    """A class for work with user notifications."""

    def __init__(
        self,
        # cache_service: CacheService,
    ) -> None:
        self.broker_service = BrokerService()
        self.repository_db = RepositoryDB(Notification)
        self.cache_service = CacheService()

    async def add_notification_task(
        self,
        created_task: NotificationCreateDto,
        exchange_name: str = EXCHANGES.CREATED_TASKS,
        queue_name: str = QUEUES.CREATED_TASKS,
    ) -> NotificationTaskCreate:  # NotificationDBView:
        """Adds a notification task."""

        notification_task_created = NotificationTaskCreate(
            **created_task.model_dump()
        )
        notification_task = NotificationTask(
            **notification_task_created.model_dump()
        )

        # db write
        # notification = await self.create_notification(created_task)

        key = f"{notification_task.notification_id}: created"
        await self.put_to_cache(key, notification_task, NotificationTask)

        # notification_task = NotificationTask(**notification.model_dump())
        await self.broker_service.add_message(
            notification_task, exchange_name, queue_name
        )

        # return notification
        return notification_task

    async def get_from_cache(
        self, key: str, schema: Any, is_list: bool = False
    ) -> Any:
        """Get data from cache."""

        # client = await get_client()
        async for client in get_client():
            data = await self.cache_service.get(client, key)

            if not data:
                return None

            if is_list:
                collection = [
                    schema(**row) for row in json.loads(data.decode())
                ]
                return collection
            return schema.parse_raw(data)

    async def put_to_cache(
        self,
        key: str,
        data: Any,
        schema: Any,
        expire: int = CACHE_EXPIRE_IN_SECONDS,
    ) -> None:
        """Put data in cache."""

        # client = await get_client()
        async for client in get_client():
            if isinstance(data, list):
                serialized_data = json.dumps(
                    [dict(schema(**dict(item))) for item in data]
                )
            else:
                serialized_data = data.json()

            await self.cache_service.set(
                client, key, serialized_data, expire=expire
            )

    async def get_notifications(
        self,
        sort: str,
        pagination: PaginationParams,
    ) -> list[NotificationDBView]:
        """Gets a paginated list of the notifications."""

        async for db_session in get_db_session():
            skip = (pagination.page_number - 1) * pagination.page_size
            limit = pagination.page_size
            notifications_db = await self.repository_db.get_many(
                db_session, sort=sort, skip=skip, limit=limit
            )
        notifications = [
            NotificationDBView(**jsonable_encoder(notification))
            for notification in notifications_db
        ]
        return notifications

    async def get_user_notifications(
        self,
        user_id: str | UUID,
        sort: str,
        pagination: PaginationParams,
    ) -> list[NotificationDBView]:
        """Gets a paginated list of the user notifications."""

        async for db_session in get_db_session():
            skip = (pagination.page_number - 1) * pagination.page_size
            limit = pagination.page_size
            notifications_db = (
                await self.repository_db.get_many_with_condition(
                    db_session,
                    attribute="user_id",
                    value=user_id,
                    sort=sort,
                    skip=skip,
                    limit=limit,
                )
            )
        notifications = [
            NotificationDBView(**jsonable_encoder(notification))
            for notification in notifications_db
        ]
        return notifications

    async def get_notification(
        self,
        notification_id: str | UUID,
    ) -> NotificationDBView:
        """Gets the notification by id."""

        async for db_session in get_db_session():
            notification_db = await self.repository_db.get_one(
                db_session,
                id=notification_id,
            )
            if notification_db is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="An invalid notification id.",
                )

        notification = NotificationDBView(**jsonable_encoder(notification_db))
        return notification

    async def create_notification(
        self,
        notification_data: NotificationCreateDto,
    ) -> NotificationDBView:
        """Creates a notification."""

        async for db_session in get_db_session():
            notification_db = await self.repository_db.create(
                db_session,
                obj_in=notification_data,
            )
        notification = NotificationDBView(**jsonable_encoder(notification_db))
        return notification

    async def update_notification(
        self,
        notification_id: str | UUID,
        notification_data: NotificationUpdateDto,
    ) -> NotificationDBView:
        """Updates the notification by id."""

        async for db_session in get_db_session():
            notification_db = await self.repository_db.get_one(
                db_session,
                id=notification_id,
            )
            if notification_db is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="An invalid notification id.",
                )
            log.debug(
                f"\nnotification_db.as_dict: \n{notification_db.as_dict()}"
            )

            notification_db.user_name = notification_data.user_name
            notification_db.user_email = notification_data.user_email

            updated_notification_db = await self.repository_db.update(
                db_session, db_obj=notification_db
            )
        notification = NotificationDBView(
            **jsonable_encoder(updated_notification_db)
        )
        return notification

    async def delete_notification(
        self,
        notification_id: str | UUID,
    ) -> NotificationDBView:
        """Deletes the notification by id."""

        async for db_session in get_db_session():
            notification_db = await self.repository_db.get_one(
                db_session,
                id=notification_id,
            )
            if notification_db is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="An invalid notification id.",
                )

            log.debug(
                f"\nnotification_db.as_dict: \n{notification_db.as_dict()}"
            )

            result = await self.repository_db.delete(
                db_session, db_obj=notification_db
            )
        return result


@lru_cache()
def get_notifications_service(
    # cache: Redis = Depends(get_redis),
) -> NotificationsService:
    """NotificationsService provider."""
    # cache_service = CacheService(cache)
    return NotificationsService()
    # return NotificationsService(cache_service)
