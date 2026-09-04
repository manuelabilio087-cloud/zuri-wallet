from abc import ABC, abstractmethod
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class WithdrawalRequestResult:
    """Resultado padronizado ao pedir um levantamento a um provedor."""
    provider_withdrawal_id: str
    status: str  # "processing" | "failed"
    raw_response: dict


class WithdrawProviderAdapter(ABC):
    """
    Interface que todo adaptador de levantamento deve implementar.
    Mesma ideia dos PaymentProviderAdapter (depósitos): trocar de provedor
    no futuro não deve exigir mudar nada fora do adaptador em si.
    """

    provider_name: str

    @abstractmethod
    async def send_withdrawal(
        self, amount: Decimal, asset: str, network: str, address: str, client_reference: str
    ) -> WithdrawalRequestResult:
        """Envia o pedido de saque ao provedor. Retorna o id do saque no provedor e o estado inicial."""
        raise NotImplementedError
