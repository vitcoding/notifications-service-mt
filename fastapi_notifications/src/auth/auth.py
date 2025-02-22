from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt

from core.config import config


def get_token(request: Request) -> str:
    """
    Retrieve the access token from the request cookies or raise an exception if not found.
    """
    token = request.cookies.get("users_access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found"
        )
    return token


async def get_current_user(token: str = Depends(get_token)) -> UUID:
    """
    Get the current user from a JWT token, validating its existence, validity, and expiration.
    """

    try:
        payload = jwt.decode(
            token, config.auth.secret_key, algorithms=[config.auth.algorithm]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The token is not valid!",
        )
    expire = payload.get("exp")
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The token has expired",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The user ID was not found",
        )

    return UUID(user_id)
