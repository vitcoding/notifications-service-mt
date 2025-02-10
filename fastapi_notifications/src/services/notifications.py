import asyncio
from functools import lru_cache

import anyio
from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.exceptions import AMQPChannelError, AMQPConnectionError
from aio_pika.pool import Pool

from core.config import config
from core.constants import EXCHANGE_NAME, QUEUE_NAME
from core.logger import log


class NotificationsService:
    def __init__(self) -> None:
        self._connection_pool: Pool | None = None

    async def initialize_connection_pool(self) -> None:
        if not self._connection_pool:
            self._connection_pool = Pool(
                lambda: connect_robust(config.broker.connection),
                max_size=5,
                # max_size=config.broker.max_connections,
            )
            log.info("Connection pool initialized.")

    async def close_connection_pool(self) -> None:
        if self._connection_pool:
            await self._connection_pool.close()
            log.info("Connection pool closed.")

    async def add_notification_task(
        self,
        message: str,
        exchange_name: str = EXCHANGE_NAME,
        queue_name: str = QUEUE_NAME,
    ) -> None:
        try:
            log.info(f"self._connection_pool: {self._connection_pool}")
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

                    message_body = message.encode("utf-8")
                    message = Message(
                        message_body,
                        delivery_mode=DeliveryMode.PERSISTENT,
                    )

                    await exchange.publish(message, routing_key="#")

                    log.info(f"\n[✅] {message_body}")
        except (AMQPConnectionError, AMQPChannelError) as err:
            log.info(f"An error connecting to RabbitMQ: {err}")
            raise
        except Exception as err:
            log.info(f"An unexpected error: {err}")
            raise


@lru_cache()
def get_notifications_service() -> NotificationsService:
    """NotificationsService provider."""

    service = NotificationsService()
    return service
