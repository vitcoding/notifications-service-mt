from fastapi import APIRouter, Depends, Request, Response, Security, status

from core.config import config
from core.logger import log
from tasks.task import task_add

router = APIRouter()

COUNTER = 0


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

    global COUNTER
    task_result = task_add.apply_async(args=["example message", 3, COUNTER])
    COUNTER += 1

    result = {"message": "Some result."}
    log.info(f"response headers: {response.headers.items()}")
    return result
