from fastapi import APIRouter, Depends, Request, Response, Security, status

from core.config import config
from core.logger import log
from schemas.notifications import Notification
from schemas.responses import SimpleResultMessage
from tasks.scheduler import task_add

router = APIRouter()


@router.post(
    "/",
    response_model=SimpleResultMessage,
    status_code=status.HTTP_200_OK,
    summary="Notification",
    description="Notification",
    response_description="Notification",
)
async def example(
    request: Request,
    response: Response,
    notification: Notification,
) -> SimpleResultMessage:

    log.info(f"config: {config.model_dump()}")

    request_id = request.headers.get("X-Request-Id")
    log.info(f"X-Request-ID: {request_id}")

    message = notification.message
    task_result = task_add.apply_async(args=[message, 1])

    # result = {"message": "The task added."}
    log.info(f"response headers: {response.headers.items()}")
    return SimpleResultMessage(message="The task added.")
