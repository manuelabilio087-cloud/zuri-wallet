import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class PaymentCallback(Base):
    """
    Registra cada webhook/callback recebido de um provedor de pagamento (M-Pesa, e-Mola, etc.).
    Nunca apagado — serve de trilha de auditoria e proteção contra chamadas duplicadas
    (verificamos external_reference antes de processar de novo).
    """

    __tablename__ = "payment_callbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deposit_id = Column(UUID(as_uuid=True), ForeignKey("deposits.id"), nullable=True)

    provider = Column(String(20), nullable=False)  # "mpesa" | "emola"
    external_reference = Column(String(150), nullable=True, index=True)

    payload = Column(Text, nullable=False)  # JSON bruto recebido, guardado como string
    signature_valid = Column(Boolean, nullable=True)  # null = não verificado (ambiente simulado)

    ip_address = Column(String(50), nullable=True)
    processed = Column(Boolean, default=False, nullable=False)
    processing_error = Column(Text, nullable=True)

    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime(timezone=True), nullable=True)
