from decimal import Decimal

from app.core.config import settings
from app.services.payment_providers.base import (
    PaymentProviderAdapter,
    PaymentRequestResult,
    PaymentStatusResult,
)


class MpesaAdapter(PaymentProviderAdapter):
    """
    Adaptador para M-Pesa (Vodacom Moçambique).

    ESTADO ATUAL: simulado — não faz nenhuma chamada de rede real.
    Quando tiveres as credenciais reais de comerciante M-Pesa, troca o corpo dos
    métodos abaixo por chamadas HTTP reais à API da Vodacom (normalmente via
    "C2B" - Customer to Business). A assinatura dos métodos não muda, então
    nada mais no sistema precisa de ser alterado.
    """

    provider_name = "mpesa"

    def __init__(self):
        self.api_key = settings.MPESA_API_KEY
        self.public_key = settings.MPESA_PUBLIC_KEY
        self.origin = settings.MPESA_ORIGIN
        self.env = settings.MPESA_ENV
        self.is_configured = bool(self.api_key and self.public_key)

    async def create_payment_request(self, amount: Decimal, phone: str, reference: str) -> PaymentRequestResult:
        if not self.is_configured:
            # Ambiente simulado: aceita sempre, fica "pending" até confirmação manual/simulada
            return PaymentRequestResult(
                external_reference=reference,
                status="pending",
                raw_response={
                    "simulated": True,
                    "provider": "mpesa",
                    "amount": str(amount),
                    "phone": phone,
                    "message": "Ambiente de desenvolvimento — sem credenciais M-Pesa configuradas",
                },
            )

        # TODO (produção): chamada real à API C2B do M-Pesa Moçambique
        # Exemplo do formato esperado (a confirmar com a documentação oficial da Vodacom):
        #
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"https://{self.origin}/ipg/v1x/c2bPayment/singleStage/",
        #         headers={"Authorization": f"Bearer {self.api_key}"},
        #         json={
        #             "input_Amount": str(amount),
        #             "input_CustomerMSISDN": phone,
        #             "input_ThirdPartyReference": reference,
        #         },
        #     )
        #     data = response.json()
        #     return PaymentRequestResult(
        #         external_reference=data["output_TransactionID"],
        #         status="pending",
        #         raw_response=data,
        #     )
        raise NotImplementedError("Integração real do M-Pesa ainda não configurada")

    async def check_status(self, external_reference: str) -> PaymentStatusResult:
        if not self.is_configured:
            return PaymentStatusResult(
                status="pending",
                raw_response={"simulated": True, "message": "Consulta manual necessária em ambiente simulado"},
            )
        raise NotImplementedError("Integração real do M-Pesa ainda não configurada")

    def verify_webhook_signature(self, payload: bytes, signature: str | None) -> bool:
        if not self.is_configured:
            # Em ambiente simulado não há assinatura real para validar
            return True
        # TODO (produção): validar assinatura/HMAC conforme especificação do M-Pesa
        raise NotImplementedError("Validação de assinatura M-Pesa ainda não configurada")
