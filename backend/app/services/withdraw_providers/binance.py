import hashlib
import hmac
import time
from decimal import Decimal
from urllib.parse import urlencode

from app.core.config import settings
from app.services.withdraw_providers.base import WithdrawProviderAdapter, WithdrawalRequestResult


class BinanceWithdrawAdapter(WithdrawProviderAdapter):
    """
    Adaptador de levantamento via Binance — única via de saída de fundos da wallet.

    ESTADO ATUAL: simulado — não faz nenhuma chamada de rede real.
    Quando tiveres a API key/secret da Binance (com permissão de "Enable
    Withdrawals" — nada mais), troca o corpo de send_withdrawal() pela
    chamada HTTP real comentada abaixo. Nada fora deste ficheiro muda.

    IMPORTANTE: a API key usada aqui é o alvo de maior valor de todo o
    sistema. Nunca a partilhes com o serviço público (backend que responde
    a pedidos de utilizadores) sem whitelist de IP fixo e limite de saque
    configurados do lado da própria Binance.
    """

    provider_name = "binance"
    BASE_URL = "https://api.binance.com"

    def __init__(self):
        self.api_key = settings.BINANCE_API_KEY
        self.api_secret = settings.BINANCE_API_SECRET
        self.is_configured = bool(self.api_key and self.api_secret)

    def _sign(self, params: dict) -> str:
        query = urlencode(params)
        return hmac.new(self.api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()

    async def send_withdrawal(
        self, amount: Decimal, asset: str, network: str, address: str, client_reference: str
    ) -> WithdrawalRequestResult:
        if not self.is_configured:
            # Ambiente simulado: aceita sempre, fica "processing" até confirmação manual/simulada.
            return WithdrawalRequestResult(
                provider_withdrawal_id=f"SIMULATED-{client_reference}",
                status="processing",
                raw_response={
                    "simulated": True,
                    "provider": "binance",
                    "amount": str(amount),
                    "asset": asset,
                    "network": network,
                    "address": address,
                    "message": "Ambiente de desenvolvimento — sem credenciais Binance configuradas",
                },
            )

        # TODO (produção): chamada real ao endpoint de saque da Binance.
        # Documentação: https://binance-docs.github.io/apidocs/spot/en/#withdraw-sapi
        #
        # params = {
        #     "coin": asset,
        #     "address": address,
        #     "amount": str(amount),
        #     "network": network,
        #     "withdrawOrderId": client_reference,
        #     "timestamp": int(time.time() * 1000),
        # }
        # params["signature"] = self._sign(params)
        #
        # async with httpx.AsyncClient(timeout=10.0) as client:
        #     response = await client.post(
        #         f"{self.BASE_URL}/sapi/v1/capital/withdraw/apply",
        #         params=params,
        #         headers={"X-MBX-APIKEY": self.api_key},
        #     )
        #     response.raise_for_status()
        #     data = response.json()
        #     return WithdrawalRequestResult(
        #         provider_withdrawal_id=data["id"],
        #         status="processing",
        #         raw_response=data,
        #     )
        raise NotImplementedError("Integração real da Binance ainda não configurada")
