from http import HTTPStatus

import aiohttp
import pytest

from core.config import service_url
from core.conftest import aiohttp_session
from core.logger import log


@pytest.mark.parametrize(
    "user_id, api_return",
    [
        (
            "f98e1eed-9516-4de2-bea1-30e552e48e5c",
            HTTPStatus.OK,
        ),
        (
            "f98e1eed-9516-4de2-bea1-000000000000",
            HTTPStatus.OK,
        ),
        (
            "f98e1eed-9516-4de2-bea1-3",
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            1,
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_get_notifications(
    aiohttp_session: aiohttp.ClientSession, user_id, api_return
) -> None:
    """Get user notifications test."""

    url = service_url + f"/api/v1/notifications/user/{user_id}"
    async with aiohttp_session.get(url) as response:
        status = response.status
        log.info(f"\nResponse: \n{response}.\n")

    assert status == api_return
