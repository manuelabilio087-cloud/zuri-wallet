import uuid
import enum
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class DepositProvider(str, enum.Enum):
    MPESA = "mpesa"
    EMOLA = "emola"


class DepositStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"


class Deposit(Base):
    __tablename__ = "deposits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)

    provider = Column(Enum(DepositProvider), nullable=False)
    reference_code = Column(String(50), unique=True, nullable=False, index=True)

    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="MZN")

    status = Column(Enum(DepositStatus), default=DepositStatus.PENDING, nullable=False)

    provider_response = Column(String(1000), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    confirmed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="deposits")
