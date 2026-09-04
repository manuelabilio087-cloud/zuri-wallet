from decimal import Decimal

from app.core.config import settings
from app.services.payment_providers.base import (
    PaymentProviderAdapter,
    PaymentRequestResult,
    PaymentStatusResult,
)


class EmolaAdapter(PaymentProviderAdapter):
    """
    Adaptador para e-Mola (Movitel Moçambique).

    ESTADO ATUAL: simulado — não faz nenhuma chamada de rede real.
    Implementação independente do MpesaAdapter (provedores diferentes, APIs
    diferentes, sem código partilhado) — só a interface (base.py) é comum.
    """

    provider_name = "emola"

    def __init__(self):
        self.api_key = settings.EMOLA_API_KEY
        self.env = settings.EMOLA_ENV
        self.is_configured = bool(self.api_key)

    async def create_payment_request(self, amount: Decimal, phone: str, reference: str) -> PaymentRequestResult:
        if not self.is_configured:
            return PaymentRequestResult(
                external_reference=reference,
                status="pending",
                raw_response={
                    "simulated": True,
                    "provider": "emola",
                    "amount": str(amount),
                    "phone": phone,
                    "message": "Ambiente de desenvolvimento — sem credenciais e-Mola configuradas",
                },
            )

        # TODO (produção): chamada real à API da Movitel e-Mola quando disponível
        raise NotImplementedError("Integração real do e-Mola ainda não configurada")

    async def check_status(self, external_reference: str) -> PaymentStatusResult:
        if not self.is_configured:
            return PaymentStatusResult(
                status="pending",
                raw_response={"simulated": True, "message": "Consulta manual necessária em ambiente simulado"},
            )
        raise NotImplementedError("Integração real do e-Mola ainda não configurada")

    def verify_webhook_signature(self, payload: bytes, signature: str | None) -> bool:
        if not self.is_configured:
            # Ver comentário equivalente em mpesa.py — recusar por omissão.
            return False
        raise NotImplementedError("Validação de assinatura e-Mola ainda não configurada")
