import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Date, DateTime, Boolean, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    PENDING_VERIFICATION = "pending_verification"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150), nullable=False)
    birth_date = Column(Date, nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    country = Column(String(100), nullable=True, default="Mozambique")
    city = Column(String(100), nullable=True)
    document_id = Column(String(50), nullable=True)
    profile_photo_url = Column(String(500), nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)

    # PIN de transação — só usado para autorizar levantamentos, independente
    # da senha da conta. Nulo até o utilizador o definir pela primeira vez.
    transaction_pin_hash = Column(String(255), nullable=True)
    pin_failed_attempts = Column(Integer, default=0, nullable=False)
    pin_locked_until = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def has_transaction_pin(self) -> bool:
        return self.transaction_pin_hash is not None

    wallet = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    deposits = relationship("Deposit", back_populates="user", cascade="all, delete-orphan")
    withdrawals = relationship("Withdrawal", back_populates="user", cascade="all, delete-orphan")
