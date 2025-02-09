from fastapi import APIRouter, Depends, Request, Response, Security, status

from core.config import config
from core.logger import log
from schemas.notifications import Notification
from schemas.responses import SimpleResultResponse
from services.notifications import (
    NotificationsService,
    get_notifications_service,
)
from tasks.scheduler import task_add

router = APIRouter()


@router.post(
    "/",
    response_model=SimpleResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a notification",
    description="Send a notification",
    response_description="The notification message sent",
)
async def send_notification(
    request: Request,
    response: Response,
    notification: Notification,
    notifications_service: NotificationsService = Depends(
        get_notifications_service
    ),
) -> SimpleResultResponse:

    # log.info(f"config: {config.model_dump()}")

    message = notification.message

    await notifications_service.add_notification_task(message)
    # task_result = task_add.apply_async(args=[message, 1])

    return SimpleResultResponse(message="The task added.")
