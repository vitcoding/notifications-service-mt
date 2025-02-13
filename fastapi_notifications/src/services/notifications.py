from functools import lru_cache
from uuid import UUID

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.exceptions import AMQPChannelError, AMQPConnectionError
from aio_pika.pool import Pool
from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from core.config import config
from core.constants import EXCHANGE_NAME, QUEUE_NAME
from core.logger import log
from db.postgres import get_db_session
from models.notification import Notification
from schemas.notifications import (
    NotificationCreateDto,
    NotificationDBView,
    NotificationUpdateDto,
)
from services.broker import BrokerService
from services.database import RepositoryDB
from services.pagination import PaginationParams


class NotificationsService:
    """A class for work with user notifications."""

    def __init__(
        self,
        # cache_service: CacheService,
    ) -> None:
        self.broker_service = BrokerService()
        self.repository_db = RepositoryDB(Notification)
        # self.cache_service = cache_service

    async def add_notification_task(
        self,
        notification_task: NotificationCreateDto,
        exchange_name: str = EXCHANGE_NAME,
        queue_name: str = QUEUE_NAME,
    ) -> None:
        """Adds a notification task."""

        await self.broker_service.add_message(
            notification_task, exchange_name, queue_name
        )

        # db write
        await self.create_notification(notification_task)

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
