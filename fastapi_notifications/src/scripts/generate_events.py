import asyncio
from random import choice, randint
from typing import Any

import httpx


def get_message_data(message: str, type_: str) -> dict[str, Any]:
    """Creates a random message."""

    message_data = {
        "user_id": choice(
            [
                "00000000-0000-0000-0000-000000000001",
                "00000000-0000-0000-0000-000000000002",
                "00000000-0000-0000-0000-000000000003",
            ]
        ),
        "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "subject": choice(
            [
                "New films",
                "Check bookmarks",
                "New likes",
            ]
        ),
        "message": message,
        "notification_type": type_,
    }

    return message_data


def generate_notifications(
    quantity: int = 1_000, type_: str = "generated"
) -> list[dict[str, Any]]:
    """Generates notifications."""

    notifications = [
        get_message_data(f"Message {i+1}", type_) for i in range(quantity)
    ]
    return notifications


async def send_notification_task(notifications: list[dict[str, Any]]) -> None:
    """Sends notifications."""

    async with httpx.AsyncClient() as client:
        url = "http://localhost:8006/api/v1/notifications/"
        for notification in notifications:
            response = await client.post(url=url, json=notification)


async def main(
    cicles_quantity: int = -1, _min: int = 10, _max: int = 100
) -> None:
    """The main function for generating notifications."""

    counter = 0
    while counter != cicles_quantity:
        notifications_tasks = generate_notifications(randint(_min, _max))
        task = asyncio.create_task(send_notification_task(notifications_tasks))
        await task
        await asyncio.sleep(randint(5, 20))
        counter += 1


if __name__ == "__main__":
    asyncio.run(main(cicles_quantity=1, _min=10, _max=10))
