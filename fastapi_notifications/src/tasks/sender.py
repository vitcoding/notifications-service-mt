import asyncio
from datetime import datetime

from celery import shared_task

from core.config import config
from core.constants import EXCHANGE_NAME, QUEUE_NAME
from core.logger import log
from services.broker import BrokerService


async def process_message(message: str) -> None:
    log.info(f"[🎉] the message '{message}' sent.")
    with open("./_temp/logs/logs.log", mode="a", encoding="utf-8") as fwa:
        fwa.writelines(f"{datetime.now().isoformat()}: {message}\n")


async def queue_get_messages(
    exchange_name: str = EXCHANGE_NAME, queue_name: str = QUEUE_NAME
) -> None:
    log.info(f"Connecting to RabbitMQ...")

    broker_service = BrokerService()
    await broker_service.get_messages(
        exchange_name, queue_name, process_message
    )


async def sender_main():
    task = asyncio.create_task(queue_get_messages())
    await task


@shared_task(bind=True)
def sender_task(self, name: str) -> None:
    log.info(f"\n{'-'*30}\n{name} launched.\n")

    asyncio.run(sender_main())

    log.info(f"\n\n{'-'*30}\n")
