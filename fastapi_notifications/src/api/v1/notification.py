from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status

from core.config import config
from core.logger import log
from schemas.notifications import (
    NotificationCreateDto,
    NotificationDBView,
    NotificationTask,
    NotificationUpdateDto,
)
from schemas.responses import SimpleResultResponse
from services.notifications import (
    NotificationsService,
    get_notifications_service,
)
from services.pagination import PaginationParams

router = APIRouter()


@router.post(
    "/",
    # response_model=NotificationDBView,
    response_model=NotificationCreateDto,
    status_code=status.HTTP_200_OK,
    summary="Send a notification",
    description="Send a notification",
    response_description="The notification message sent",
)
async def create_notification(
    request: Request,
    response: Response,
    notification_task: NotificationCreateDto,
    notifications_service: NotificationsService = Depends(
        get_notifications_service
    ),
) -> NotificationCreateDto:  # NotificationDBView:

    notification = await notifications_service.add_notification_task(
        notification_task
    )
    notification_response = NotificationCreateDto(**notification.model_dump())
    return notification_response


@router.get(
    "/",
    response_model=list[NotificationDBView],
    status_code=status.HTTP_200_OK,
    summary="A list of the notifications",
    description="A paginated list of the notifications",
    response_description="The notifications data",
)
async def get_notifications(
    request: Request,
    response: Response,
    sort: str | None = Query("-created_at"),
    pagination: PaginationParams = Depends(),
    notifications_service: NotificationsService = Depends(
        get_notifications_service
    ),
) -> list[NotificationDBView]:

    notifications = await notifications_service.get_notifications(
        sort, pagination
    )
    return notifications


@router.get(
    "/{notification_id}",
    response_model=NotificationDBView,
    status_code=status.HTTP_200_OK,
    summary="The notification",
    description="The notification by id",
    response_description="The notification data",
)
async def get_notification(
    request: Request,
    response: Response,
    notification_id: UUID,
    notifications_service: NotificationsService = Depends(
        get_notifications_service
    ),
) -> NotificationDBView:

    notification = await notifications_service.get_notification(
        notification_id
    )
    return notification


@router.put(
    "/{notification_id}",
    response_model=NotificationDBView,
    status_code=status.HTTP_200_OK,
    summary="The notification",
    description="The notification by id",
    response_description="The notification data",
)
async def update_notification(
    request: Request,
    response: Response,
    notification_id: UUID,
    notification_data: NotificationUpdateDto,
    notifications_service: NotificationsService = Depends(
        get_notifications_service
    ),
) -> NotificationDBView:

    notification = await notifications_service.update_notification(
        notification_id, notification_data
    )
    return notification


@router.delete(
    "/{notification_id}",
    response_model=SimpleResultResponse,
    status_code=status.HTTP_200_OK,
    summary="The notification",
    description="The notification by id",
    response_description="The notification data",
)
async def delete_notification(
    request: Request,
    response: Response,
    notification_id: UUID,
    notifications_service: NotificationsService = Depends(
        get_notifications_service
    ),
) -> NotificationDBView:

    result = await notifications_service.delete_notification(notification_id)
    return SimpleResultResponse(message="The notification deleted.")


@router.get(
    "/user/{user_id}",
    response_model=list[NotificationDBView],
    status_code=status.HTTP_200_OK,
    summary="A list of the user notifications",
    description="A paginated list of the user notifications",
    response_description="The notifications data",
)
async def get_user_notifications(
    request: Request,
    response: Response,
    user_id: UUID,
    sort: str | None = Query("-created_at"),
    pagination: PaginationParams = Depends(),
    notifications_service: NotificationsService = Depends(
        get_notifications_service
    ),
) -> list[NotificationDBView]:

    notifications = await notifications_service.get_user_notifications(
        user_id, sort, pagination
    )
    return notifications
