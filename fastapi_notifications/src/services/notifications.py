from functools import lru_cache

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.exceptions import AMQPChannelError, AMQPConnectionError
from aio_pika.pool import Pool
from fastapi import Depends

from core.config import config
from core.constants import EXCHANGE_NAME, QUEUE_NAME
from core.logger import log
from db.postgres import AsyncSession, get_session
from models.notification import Notification
from schemas.notifications import NotificationTask
from services.database import DBService


class NotificationsService:
    def __init__(
        self,
        db_service: DBService,
        # cache_service: CacheService,
    ) -> None:
        self._connection_pool: Pool | None = None
        self.db_service = db_service
        # self.cache_service = cache_service

    async def initialize_connection_pool(self) -> None:
        if not self._connection_pool:
            self._connection_pool = Pool(
                lambda: connect_robust(config.broker.connection),
                max_size=10,
            )
            log.info("Connection pool initialized.")

    async def close_connection_pool(self) -> None:
        if self._connection_pool:
            await self._connection_pool.close()
            log.info("Connection pool closed.")

    async def add_notification_task(
        self,
        notification_task: NotificationTask,
        exchange_name: str = EXCHANGE_NAME,
        queue_name: str = QUEUE_NAME,
    ) -> None:
        try:
            log.info(f"self._connection_pool: {self._connection_pool}")

            log.debug(
                f"\n\nnotification_task: \n{notification_task}"
                f"\n\ntype(notification_task): \n{type(notification_task)}\n\n"
            )

            await self.initialize_connection_pool()
            async with self._connection_pool.acquire() as connection:
                async with connection.channel() as channel:
                    exchange = await channel.declare_exchange(
                        name=exchange_name, type=ExchangeType.TOPIC
                    )
                    queue = await channel.declare_queue(
                        queue_name, durable=True
                    )
                    await queue.bind(exchange=exchange, routing_key="#")
                    message_body = notification_task.model_dump_json().encode(
                        "utf-8"
                    )
                    message = Message(
                        message_body,
                        delivery_mode=DeliveryMode.PERSISTENT,
                    )
                    await exchange.publish(message, routing_key="#")

                    # db write
                    notification_db = Notification(
                        **notification_task.model_dump()
                    )
                    await self.db_service.put_item(
                        Notification, notification_db
                    )

                    log.info(f"\n[✅] {message_body}")
        except (AMQPConnectionError, AMQPChannelError) as err:
            log.info(f"An error connecting to RabbitMQ: {err}")
            raise
        except Exception as err:
            log.info(f"An unexpected error: {err}")
            raise


@lru_cache()
def get_notifications_service(
    db: AsyncSession = Depends(get_session),
    # cache: Redis = Depends(get_redis),
) -> NotificationsService:
    """NotificationsService provider."""
    db_service = DBService(db)
    # cache_service = CacheService(cache)
    return NotificationsService(db_service)
    # return NotificationsService(db_service, cache_service)
