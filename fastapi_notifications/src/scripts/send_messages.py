import asyncio
from typing import Any

import httpx


def get_message_data(message: str) -> dict[str, Any]:
    message_data = {
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "user_name": "UserName",
        "user_email": "email",
        "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "subject": "Title",
        "message": message,
        "notification_type": "email",
    }

    return message_data


def generate_notifications(quantity: int = 100) -> list[dict[str, Any]]:
    notifications = [
        get_message_data(f"Message {i+1}") for i in range(quantity)
    ]
    return notifications


async def send_notification_task(notifications: list[dict[str, Any]]) -> None:
    async with httpx.AsyncClient() as client:
        url = "http://localhost:8006/api/v1/notification/"
        for notification in notifications:
            response = await client.post(url=url, json=notification)


async def main() -> None:
    notifications_tasks = generate_notifications(10)
    task = asyncio.create_task(send_notification_task(notifications_tasks))
    await task


if __name__ == "__main__":
    asyncio.run(main())
