import uuid
import enum
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    CONVERSION = "conversion"
    WITHDRAWAL = "withdrawal"
    ADJUSTMENT = "adjustment"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)

    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), nullable=False)

    exchange_rate = Column(Numeric(18, 6), nullable=True)
    source_currency = Column(String(3), nullable=True)
    source_amount = Column(Numeric(18, 2), nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="transactions")
