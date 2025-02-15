import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(UUID, nullable=False)
    user_name = Column(String(255), nullable=False, default="")
    user_email = Column(String(255), nullable=False, default="")
    template_id = Column(UUID, nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(255), nullable=False, default="email")
    last_sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(
        self,
        user_id: UUID,
        template_id: UUID,
        subject: str,
        message: str,
        notification_type: str,
        user_name: str = "",
        user_email: str = "",
        last_sent_at: datetime | None = None,
    ) -> None:
        self.user_id = user_id
        self.user_name = user_name
        self.user_email = user_email
        self.template_id = template_id
        self.subject = subject
        self.message = message
        self.notification_type = notification_type
        self.last_sent_at = last_sent_at

    def __repr__(self) -> str:
        return f"<Notification {self.id}>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
