import asyncio

import httpx


def generate_messages(quantity: int = 100) -> list[str]:
    messages = [f"Message {i+1}" for i in range(quantity)]
    return messages


async def send_messages(messages: list[str]) -> None:
    async with httpx.AsyncClient() as client:
        url = "http://localhost:8006/api/v1/notification/"
        for message in messages:
            response = await client.post(url=url, json={"message": message})


async def main() -> None:
    messages = generate_messages(10)
    task = asyncio.create_task(send_messages(messages))
    await task


if __name__ == "__main__":
    asyncio.run(main())
