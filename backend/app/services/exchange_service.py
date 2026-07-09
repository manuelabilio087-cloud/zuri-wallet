from decimal import Decimal, ROUND_HALF_UP

import httpx

from app.core.config import settings

# Taxas de fallback (mock) usadas caso a API externa esteja indisponível durante o desenvolvimento.
# Base: 1 MZN convertido para cada moeda. Ajustar periodicamente ou substituir por fonte real em produção.
MOCK_RATES_FROM_MZN = {
    "MZN": Decimal("1"),
    "USD": Decimal("0.0157"),
    "EUR": Decimal("0.0146"),
    "BRL": Decimal("0.0870"),
    "GBP": Decimal("0.0124"),
    "ZAR": Decimal("0.2850"),
}


class ExchangeService:
    """
    Serviço responsável exclusivamente pelo câmbio.
    Não conhece wallet, usuário ou transação — só converte valores usando uma taxa.
    """

    async def get_rate(self, from_currency: str, to_currency: str) -> Decimal:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            return Decimal("1")

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{settings.EXCHANGE_RATE_API_URL}/latest",
                    params={"base": from_currency, "symbols": to_currency},
                )
                response.raise_for_status()
                data = response.json()
                rate = data["rates"][to_currency]
                return Decimal(str(rate))
        except Exception:
            # Fallback para taxas mock em caso de falha da API externa (ex: sem internet, rate limit)
            return self._mock_rate(from_currency, to_currency)

    def _mock_rate(self, from_currency: str, to_currency: str) -> Decimal:
        if from_currency == "MZN":
            return MOCK_RATES_FROM_MZN.get(to_currency, Decimal("1"))
        if to_currency == "MZN":
            rate_to_mzn = MOCK_RATES_FROM_MZN.get(from_currency, Decimal("1"))
            return Decimal("1") / rate_to_mzn if rate_to_mzn else Decimal("1")

        # Conversão cruzada via MZN como moeda ponte (ex: USD -> EUR passa por MZN)
        from_rate = MOCK_RATES_FROM_MZN.get(from_currency, Decimal("1"))
        to_rate = MOCK_RATES_FROM_MZN.get(to_currency, Decimal("1"))
        return to_rate / from_rate

    async def convert(self, from_currency: str, to_currency: str, amount: Decimal) -> tuple[Decimal, Decimal]:
        """Retorna (valor_convertido, taxa_utilizada), ambos arredondados a 2 casas decimais."""
        rate = await self.get_rate(from_currency, to_currency)
        converted = (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return converted, rate
