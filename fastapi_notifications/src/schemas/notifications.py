from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationTask(BaseModel):
    user_id: UUID
    user_name: str
    user_email: str
    template_id: UUID
    subject: str
    message: str
    notification_type: str = Field(default="email")


class NotificationDB(BaseModel):
    id: UUID
    user_id: UUID
    user_name: str
    user_email: str
    template_id: UUID
    subject: str
    message: str
    notification_type: str
    last_sent_at: datetime | None
    created_at: datetime
    updated_at: datetime
