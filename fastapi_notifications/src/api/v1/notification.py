from fastapi import APIRouter, Depends, Request, Response, Security, status

from core.config import config
from core.logger import log
from tasks.scheduler import task_add

router = APIRouter()


def generate_messages(quantity: int = 100) -> list[str]:
    messages = [f"Message {i+1}" for i in range(quantity)]
    return messages


@router.get(
    "/",
    # response_model=SomeView,
    status_code=status.HTTP_200_OK,
    summary="Notification",
    description="Notification",
    response_description="Notification",
)
async def example(
    request: Request,
    response: Response,
) -> dict:

    log.info(f"config: {config.model_dump()}")

    request_id = request.headers.get("X-Request-Id")
    log.info(f"X-Request-ID: {request_id}")

    for message in generate_messages(100):
        task_result = task_add.apply_async(args=[message, 1])

    result = {"message": "Some result."}
    log.info(f"response headers: {response.headers.items()}")
    return result
