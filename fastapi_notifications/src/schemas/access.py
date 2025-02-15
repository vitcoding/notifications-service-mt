from pydantic import BaseModel


class UserAccess(BaseModel):
    users_access_token: str
