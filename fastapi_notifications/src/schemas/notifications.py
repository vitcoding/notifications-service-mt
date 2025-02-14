from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreateDto(BaseModel):
    user_id: UUID
    template_id: UUID
    subject: str
    message: str
    notification_type: str = Field(default="email")


class NotificationUpdateDto(BaseModel):
    user_name: str
    user_email: str


# class NotificationTaskCreate(BaseModel):
#     notification_id: UUID
#     user_id: UUID
#     user_name: str
#     user_email: str
#     template_id: UUID
#     subject: str
#     message: str
#     notification_type: str
#     user_name: str = Field(default="")
#     user_email: str = Field(default="")
#     notification_id: UUID = Field(default=uuid4())


class NotificationTask(BaseModel):
    # notification_id: UUID
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
