import uuid
import enum
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class WithdrawalStatus(str, enum.Enum):
    PENDING = "pending"       # debitado da wallet, ainda não enviado à Binance
    PROCESSING = "processing"  # pedido de saque aceite pela Binance, a caminho
    COMPLETED = "completed"
    FAILED = "failed"          # falhou — saldo já foi devolvido ao utilizador


class Withdrawal(Base):
    """
    Levantamento: única via de saída de fundos da wallet, sempre através da
    API da Binance (envio de USDT para o endereço/rede que o utilizador indicar).
    Não existe levantamento por M-Pesa/e-Mola/banco nesta fase.
    """

    __tablename__ = "withdrawals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)

    currency = Column(String(3), nullable=False, default="USD")  # moeda debitada da wallet
    amount = Column(Numeric(18, 2), nullable=False)

    asset = Column(String(10), nullable=False, default="USDT")   # ativo enviado na Binance
    network = Column(String(20), nullable=False)                 # ex: "BSC", "TRX"
    destination_address = Column(String(200), nullable=False)

    status = Column(Enum(WithdrawalStatus), default=WithdrawalStatus.PENDING, nullable=False)

    binance_withdrawal_id = Column(String(100), nullable=True, index=True)
    provider_response = Column(String(1000), nullable=True)
    failure_reason = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="withdrawals")
