import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, String, DateTime, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ExchangeRate(Base):
    """
    Cache da taxa de câmbio mais recente para cada par de moedas (base -> quote).
    Uma linha por par — sempre sobrescrita com o valor mais recente.
    Ex: base=MZN, quote=USD, rate=0.0157
    """

    __tablename__ = "exchange_rates"
    __table_args__ = (UniqueConstraint("base_currency", "quote_currency", name="uq_exchange_rate_pair"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    base_currency = Column(String(3), nullable=False)
    quote_currency = Column(String(3), nullable=False)
    rate = Column(Numeric(18, 8), nullable=False)
    source = Column(String(50), nullable=False, default="mock")  # "api" ou "mock"
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ExchangeRateHistory(Base):
    """
    Histórico append-only de cada cotação obtida — nunca é apagado ou sobrescrito.
    Usado para auditoria e para gráficos de variação cambial no futuro.
    """

    __tablename__ = "exchange_rate_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    base_currency = Column(String(3), nullable=False)
    quote_currency = Column(String(3), nullable=False)
    rate = Column(Numeric(18, 8), nullable=False)
    source = Column(String(50), nullable=False, default="mock")
    fetched_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
