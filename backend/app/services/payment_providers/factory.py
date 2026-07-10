from app.models.deposit import DepositProvider
from app.services.payment_providers.base import PaymentProviderAdapter
from app.services.payment_providers.mpesa import MpesaAdapter
from app.services.payment_providers.emola import EmolaAdapter


def get_payment_provider(provider: DepositProvider) -> PaymentProviderAdapter:
    """
    Ponto único de extensão: para adicionar um novo provedor (Binance, PayPal,
    Stripe, outro banco, etc.) no futuro, basta:
      1. Criar um novo enum em DepositProvider (models/deposit.py)
      2. Criar uma nova classe que implemente PaymentProviderAdapter
      3. Adicionar uma linha aqui
    Nenhum outro ficheiro do sistema precisa de ser alterado.
    """
    if provider == DepositProvider.MPESA:
        return MpesaAdapter()
    if provider == DepositProvider.EMOLA:
        return EmolaAdapter()
    raise ValueError(f"Provedor de pagamento não suportado: {provider}")
