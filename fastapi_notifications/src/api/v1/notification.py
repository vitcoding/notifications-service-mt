from fastapi import APIRouter, Depends, Request, Response, status

from core.config import config
from core.logger import log
from schemas.notifications import NotificationTask
from schemas.responses import SimpleResultResponse
from services.notifications import (
    NotificationsService,
    get_notifications_service,
)

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
    notification_task: NotificationTask,
    notifications_service: NotificationsService = Depends(
        get_notifications_service
    ),
) -> SimpleResultResponse:

    await notifications_service.add_notification_task(notification_task)

    return SimpleResultResponse(message="The task added.")
