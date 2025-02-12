from fastapi import APIRouter

from api.v1 import notification

router = APIRouter()

router.include_router(
    notification.router, prefix="/v1/notifications", tags=["notifications"]
)
