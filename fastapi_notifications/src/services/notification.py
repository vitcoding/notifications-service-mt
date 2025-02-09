from functools import lru_cache

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.exceptions import AMQPChannelError, AMQPConnectionError

from core.config import config
from core.constants import EXCHANGE_NAME, QUEUE_NAME
from core.logger import log


class NotificationsService:
    def __init__(self):
        pass

    async def add_notification_task(
        self,
        message: str,
        exchange_name: str = EXCHANGE_NAME,
        queue_name: str = QUEUE_NAME,
    ) -> None:
        try:
            connection = await connect_robust(config.broker.connection)

            async with connection:
                channel = await connection.channel()

                exchange = await channel.declare_exchange(
                    name=exchange_name, type=ExchangeType.TOPIC
                )

                queue = await channel.declare_queue(queue_name, durable=True)
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
    return NotificationsService()
