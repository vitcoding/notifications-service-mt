from fastapi import APIRouter, Depends, Request, Response, Security, status

from core.config import config
from core.logger import log

router = APIRouter()


@router.get(
    "/",
    # response_model=SomeView,
    status_code=status.HTTP_200_OK,
    summary="Notification",
    description="Notification",
    response_description="Notification",
)
async def create_user(
    request: Request,
    response: Response,
) -> dict:

    log.info(f"config: {config.model_dump()}")

    request_id = request.headers.get("X-Request-Id")
    log.info(f"X-Request-ID: {request_id}")

    result = {"message": "Some result."}
    log.info(f"response headers: \n{response.headers.items()}")
    return result
