from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreateDto(BaseModel):
    user_id: UUID
    template_id: UUID
    subject: str
    message: str
    notification_type: str = Field(default="email")


class NotificationUpdateProfileDto(BaseModel):
    user_name: str
    user_email: str


class NotificationUpdateTimeDto(BaseModel):
    last_sent_at: datetime


class NotificationTask(BaseModel):
    id: UUID
    user_id: UUID
    user_name: str
    user_email: str
    template_id: UUID
    subject: str
    message: str
    notification_type: str


class NotificationDBView(BaseModel):
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


class NotificationResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    user_email: str
    template_id: UUID
    subject: str
    message: str
    notification_type: str
    last_sent_at: datetime | None
