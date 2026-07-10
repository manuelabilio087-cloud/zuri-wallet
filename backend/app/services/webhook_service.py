from datetime import datetime, timezone
import json
from sqlalchemy.orm import Session

from app.models.deposit import DepositProvider
from app.models.payment_callback import PaymentCallback
from app.repositories.deposit_repository import DepositRepository
from app.services.deposit_service import DepositService
from app.services.payment_providers.factory import get_payment_provider


class WebhookService:
    """
    Recebe e processa callbacks (webhooks) dos provedores de pagamento.

    Responsabilidades:
      - Registar todo callback recebido (payload bruto, IP, hora) — nunca apaga.
      - Validar a assinatura via o adaptador do provedor correspondente.
      - Evitar processar o mesmo callback duas vezes (idempotência por external_reference).
      - Confirmar o depósito correspondente quando o callback é válido.
    """

    def __init__(self, db: Session):
        self.db = db
        self.deposit_repo = DepositRepository(db)
        self.deposit_service = DepositService(db)

    def handle_callback(
        self,
        provider: DepositProvider,
        raw_body: bytes,
        signature: str | None,
        ip_address: str | None,
        external_reference: str,
    ) -> PaymentCallback:
        # Idempotência: se já processámos este external_reference com sucesso, não repete.
        existing = (
            self.db.query(PaymentCallback)
            .filter(
                PaymentCallback.external_reference == external_reference,
                PaymentCallback.processed == True,  # noqa: E712
            )
            .first()
        )
        if existing:
            return existing

        adapter = get_payment_provider(provider)
        signature_valid = adapter.verify_webhook_signature(raw_body, signature)

        callback = PaymentCallback(
            provider=provider.value,
            external_reference=external_reference,
            payload=raw_body.decode("utf-8", errors="replace")[:5000],
            signature_valid=signature_valid,
            ip_address=ip_address,
            processed=False,
        )

        if not signature_valid:
            callback.processing_error = "Assinatura inválida — callback rejeitado"
            self.db.add(callback)
            self.db.commit()
            self.db.refresh(callback)
            return callback

        try:
            deposit = self.deposit_repo.get_by_reference(external_reference)
            if deposit is None:
                callback.processing_error = "Nenhum depósito encontrado para esta referência"
            else:
                callback.deposit_id = deposit.id
                self.deposit_service.confirm_deposit(external_reference)
                callback.processed = True
                callback.processed_at = datetime.now(timezone.utc)
        except Exception as e:
            callback.processing_error = str(e)[:500]

        self.db.add(callback)
        self.db.commit()
        self.db.refresh(callback)
        return callback
