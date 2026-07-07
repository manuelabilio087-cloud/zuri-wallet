import uuid
from decimal import Decimal

from sqlalchemy import Column, String, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)

    user = relationship("User", back_populates="wallet")
    balances = relationship("WalletBalance", back_populates="wallet", cascade="all, delete-orphan")


class WalletBalance(Base):
    __tablename__ = "wallet_balances"
    __table_args__ = (UniqueConstraint("wallet_id", "currency", name="uq_wallet_currency"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False)
    currency = Column(String(3), nullable=False)  # USD, EUR, BRL, MZN, GBP, ZAR
    balance = Column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))

    wallet = relationship("Wallet", back_populates="balances")
