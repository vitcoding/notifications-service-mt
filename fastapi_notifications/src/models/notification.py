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
    user_name = Column(String(255), nullable=False)
    user_email = Column(String(255), nullable=False)
    template_id = Column(UUID, nullable=False)
    message = Column(Text, nullable=False)
    last_send_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(
        self,
        user_id: UUID,
        user_name: str,
        user_email: str,
        template_id: UUID,
        message: str,
        last_send_at: datetime | None = None,
    ) -> None:
        self.user_id = user_id
        self.user_name = user_name
        self.user_email = user_email
        self.template_id = template_id
        self.message = message
        self.last_send_at = last_send_at

    def __repr__(self) -> str:
        return f"<Notification {self.id}>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
