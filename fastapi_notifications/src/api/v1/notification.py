from fastapi import APIRouter, Depends, Request, Response, Security, status

from core.config import config
from core.logger import log
from tasks.task import task_add

router = APIRouter()


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

    task_result = task_add.apply_async(args=["example message", 3])
    # task_result = task_add.apply_async(args=("example message", 3))

    # Если нужен результат выполнения задачи, можно получить его позже
    # async_result = AsyncResult(task_result.task_id)
    # result = async_result.get(timeout=10)  # Ожидание результата до 10 секунд

    result = {"message": "Some result."}
    log.info(f"response headers: {response.headers.items()}")
    return result
