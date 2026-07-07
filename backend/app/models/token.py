import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class TokenType(str, enum.Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    REFRESH = "refresh"


class Token(Base):
    __tablename__ = "tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    token_type = Column(Enum(TokenType), nullable=False)
    token_value = Column(String(500), unique=True, nullable=False, index=True)

    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(300), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
