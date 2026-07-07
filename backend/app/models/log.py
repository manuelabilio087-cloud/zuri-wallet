import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)

    action = Column(String(150), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
