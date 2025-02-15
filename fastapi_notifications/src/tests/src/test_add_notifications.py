from http import HTTPStatus

import aiohttp
import pytest

from core.config import service_url
from core.conftest import aiohttp_session
from core.logger import log


@pytest.mark.parametrize(
    "data_json, api_return",
    [
        (
            {
                "user_id": "f98e1eed-9516-4de2-bea1-30e552e48e5c",
                "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "subject": "Title",
                "message": "Text",
                "notification_type": "email",
            },
            HTTPStatus.OK,
        ),
        (
            {
                "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "subject": "Title",
                "message": "Text",
                "notification_type": "email",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {
                "user_id": "f98e1eed-9516-4de2-bea1-30e552e48e5c",
                "subject": "Title",
                "message": "Text",
                "notification_type": "email",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {
                "user_id": "f98e1eed-9516-4de2-bea1-30e552e48e5c",
                "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "message": "Text",
                "notification_type": "email",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {
                "user_id": "f98e1eed-9516-4de2-bea1-30e552e48e5c",
                "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "subject": "Title",
                "notification_type": "email",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {
                "user_id": "f98e1eed-9516-4de2-bea1-30e552e48e5c",
                "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "subject": "Title",
                "message": "Text",
            },
            HTTPStatus.OK,
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_add_notification(
    aiohttp_session: aiohttp.ClientSession, data_json, api_return
) -> None:
    """Add notification test."""

    url = service_url + "/api/v1/notifications/"
    async with aiohttp_session.post(url, json=data_json) as response:
        status = response.status
        log.debug(f"\nResponse: \n{response}.\n")

    assert status == api_return
