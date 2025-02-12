from typing import Any

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.exceptions import AMQPChannelError, AMQPConnectionError
from aio_pika.pool import Pool

from core.config import config
from core.constants import EXCHANGE_NAME, QUEUE_NAME
from core.logger import log
from schemas.notifications import NotificationCreateDto


class BrokerService:
    def __init__(
        self,
    ) -> None:
        self._connection_pool: Pool | None = None

    async def initialize_connection_pool(self) -> None:
        if not self._connection_pool:
            self._connection_pool = Pool(
                lambda: connect_robust(config.broker.connection),
                max_size=10,
            )
            log.info("Broker: Connection pool initialized.")

    async def close_connection_pool(self) -> None:
        if self._connection_pool:
            await self._connection_pool.close()
            log.info("Broker: Connection pool closed.")

    async def add_message(
        self,
        message: Any,
        exchange_name: str = EXCHANGE_NAME,
        queue_name: str = QUEUE_NAME,
    ) -> None:
        try:
            log.info(f"Broker: self._connection_pool: {self._connection_pool}")

            log.debug(
                f"\n\nBroker: message: \n{message}"
                f"\n\nBroker: type(nmessage): \n{type(message)}\n\n"
            )

            await self.initialize_connection_pool()
            async with self._connection_pool.acquire() as connection:
                await self.publish(
                    connection, exchange_name, queue_name, message
                )

            log.info(f"\n[✅] {message}")
        except (AMQPConnectionError, AMQPChannelError) as err:
            log.info(f"Broker: An error connecting to RabbitMQ: {err}")
            raise
        except Exception as err:
            log.info(f"Broker: An unexpected error: {err}")
            raise

    async def publish(
        self, connection, exchange_name, queue_name, notification_task
    ):
        async with connection.channel() as channel:
            exchange = await channel.declare_exchange(
                name=exchange_name, type=ExchangeType.TOPIC
            )
            queue = await channel.declare_queue(queue_name, durable=True)
            await queue.bind(exchange=exchange, routing_key="#")
            message_body = notification_task.model_dump_json().encode("utf-8")
            message = Message(
                message_body,
                delivery_mode=DeliveryMode.PERSISTENT,
            )
            await exchange.publish(message, routing_key="#")
