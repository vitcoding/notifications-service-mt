from typing import Any, Callable, Coroutine

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.exceptions import (
    AMQPChannelError,
    AMQPConnectionError,
    QueueEmpty,
)
from aio_pika.pool import Pool

from core.config import config
from core.logger import log


class BrokerService:
    def __init__(
        self,
    ) -> None:
        self._connection_pool: Pool | None = None

    async def initialize_connection_pool(self) -> None:
        """Initializes broker connection pool."""

        if not self._connection_pool:
            self._connection_pool = Pool(
                lambda: connect_robust(config.broker.connection),
                max_size=10,
            )
            log.info("Broker: Connection pool initialized.")

    async def close_connection_pool(self) -> None:
        """Closes broker connection pool."""

        if self._connection_pool:
            await self._connection_pool.close()
            log.info("Broker: Connection pool closed.")

    async def add_message(
        self,
        message: Any,
        exchange_name: str,
        queue_name: str,
    ) -> None:
        """Adds messages to a queue."""

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
        self,
        connection: Coroutine,
        exchange_name: str,
        queue_name: str,
        message_data: Any,
    ) -> None:
        """A method for publishing messages."""

        async with connection.channel() as channel:
            exchange = await channel.declare_exchange(
                name=exchange_name, type=ExchangeType.TOPIC
            )
            queue = await channel.declare_queue(queue_name, durable=True)
            await queue.bind(exchange=exchange, routing_key="#")
            message_body = message_data.model_dump_json().encode("utf-8")
            message = Message(
                message_body,
                delivery_mode=DeliveryMode.PERSISTENT,
            )
            await exchange.publish(message, routing_key="#")

    async def get_messages(
        self,
        exchange_name: str,
        queue_name: str,
        async_process_func: Callable | None = None,
    ) -> Any:
        """Gets messages from the queue."""

        try:
            log.info(f"Broker: self._connection_pool: {self._connection_pool}")

            await self.initialize_connection_pool()
            async with self._connection_pool.acquire() as connection:
                await self.consume(
                    connection, exchange_name, queue_name, async_process_func
                )

        except (AMQPConnectionError, AMQPChannelError) as err:
            log.info(f"An error connecting to RabbitMQ: {err}")
            raise
        except Exception as err:
            log.info(f"An unexpected error: {err}")
            raise

    async def consume(
        self,
        connection: Coroutine,
        exchange_name: str,
        queue_name: str,
        async_process_func: Callable | None = None,
    ) -> Any:
        """A method for consuming messages."""

        async with connection:
            channel = await connection.channel()
            log.debug(f"Broker: Connected successfully to RabbitMQ.")

            exchange = await channel.declare_exchange(
                name=exchange_name, type=ExchangeType.TOPIC
            )

            log.info(f"\nqueue_name: {queue_name}")
            queue = await channel.declare_queue(name=queue_name, durable=True)
            await queue.bind(exchange, "#")

            batch_size = 1_000
            counter = 0
            while counter < batch_size:
                try:
                    message = await queue.get(timeout=1)
                    message_body = message.body.decode("utf-8")
                    log.info(f"Got a message: {message_body}")

                    # Process_message function
                    if async_process_func is not None:
                        await async_process_func(message_body)

                    # Confirmation of receipt of the message
                    await message.ack()
                    counter += 1
                except QueueEmpty:
                    log.info("\nNo messages available.\n")
                    break

        log.info(f"Broker: Connection closed.\n")
