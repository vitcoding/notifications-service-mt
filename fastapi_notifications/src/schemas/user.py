from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class UserAuth(BaseModel):
    id: UUID
    login: str
    first_name: str | None
    last_name: str | None
    about: str | None
    birth_date: date | None
    email: str
    phone_number: str | None
    role: str
    created_at: datetime
    updated_at: datetime
