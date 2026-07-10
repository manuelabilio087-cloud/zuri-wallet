from abc import ABC, abstractmethod
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class PaymentRequestResult:
    """Resultado padronizado ao criar um pedido de pagamento, seja qual for o provedor."""
    external_reference: str
    status: str  # "pending" | "failed"
    raw_response: dict


@dataclass
class PaymentStatusResult:
    """Resultado padronizado ao consultar o estado de um pagamento."""
    status: str  # "pending" | "confirmed" | "failed" | "expired"
    raw_response: dict


class PaymentProviderAdapter(ABC):
    """
    Interface que todo adaptador de provedor de pagamento deve implementar.

    Isto permite trocar M-Pesa/e-Mola por implementações reais (ou adicionar
    Binance, PayPal, Stripe, etc. no futuro) sem alterar nenhuma lógica da wallet,
    dos depósitos ou das rotas — só é preciso criar uma nova classe que implemente
    esta interface e registá-la na factory (payment_providers/factory.py).
    """

    provider_name: str

    @abstractmethod
    async def create_payment_request(self, amount: Decimal, phone: str, reference: str) -> PaymentRequestResult:
        """Inicia um pedido de pagamento junto ao provedor. Retorna a referência externa e o estado inicial."""
        raise NotImplementedError

    @abstractmethod
    async def check_status(self, external_reference: str) -> PaymentStatusResult:
        """Consulta ativamente o estado de um pagamento junto ao provedor (usado como fallback ao webhook)."""
        raise NotImplementedError

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str | None) -> bool:
        """Valida a assinatura de um callback recebido, para garantir que veio mesmo do provedor."""
        raise NotImplementedError
