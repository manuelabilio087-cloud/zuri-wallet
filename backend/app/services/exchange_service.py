from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.exchange import ExchangeRate, ExchangeRateHistory

# Taxas de fallback (mock) — usadas quando a API externa falha E não há cache válido ainda.
# Base: 1 MZN convertido para cada moeda.
MOCK_RATES_FROM_MZN = {
    "MZN": Decimal("1"),
    "USD": Decimal("0.0157"),
    "EUR": Decimal("0.0146"),
    "BRL": Decimal("0.0870"),
    "GBP": Decimal("0.0124"),
    "ZAR": Decimal("0.2850"),
}

CACHE_TTL_MINUTES = 30


class ExchangeEngine:
    """
    Exchange Engine — responsável exclusivamente pelo câmbio.

    Fluxo de get_rate():
      1. Procura no cache (tabela exchange_rates) — se existir e não estiver
         expirado (CACHE_TTL_MINUTES), usa esse valor sem chamar a API externa.
      2. Se expirado ou inexistente, tenta buscar da API externa.
      3. Se a API falhar, usa a taxa mock como último recurso.
      4. Sempre que obtém uma taxa nova (via API ou mock), atualiza o cache
         E regista uma linha no histórico (exchange_rate_history), que nunca
         é apagado — serve de trilha para gráficos de variação cambial.
    """

    def __init__(self, db: Session):
        self.db = db

    def _get_cached(self, base: str, quote: str) -> ExchangeRate | None:
        return (
            self.db.query(ExchangeRate)
            .filter(ExchangeRate.base_currency == base, ExchangeRate.quote_currency == quote)
            .first()
        )

    def _is_fresh(self, cached: ExchangeRate) -> bool:
        if cached.updated_at is None:
            return False
        age = datetime.now(timezone.utc) - cached.updated_at
        return age < timedelta(minutes=CACHE_TTL_MINUTES)

    def _save_rate(self, base: str, quote: str, rate: Decimal, source: str) -> None:
        cached = self._get_cached(base, quote)
        now = datetime.now(timezone.utc)

        if cached:
            cached.rate = rate
            cached.source = source
            cached.updated_at = now
        else:
            cached = ExchangeRate(base_currency=base, quote_currency=quote, rate=rate, source=source, updated_at=now)
            self.db.add(cached)

        history = ExchangeRateHistory(base_currency=base, quote_currency=quote, rate=rate, source=source, fetched_at=now)
        self.db.add(history)
        self.db.commit()

    async def _fetch_from_api(self, base: str, quote: str) -> Decimal | None:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{settings.EXCHANGE_RATE_API_URL}/latest",
                    params={"base": base, "symbols": quote},
                )
                response.raise_for_status()
                data = response.json()
                return Decimal(str(data["rates"][quote]))
        except Exception:
            return None

    def _mock_rate(self, base: str, quote: str) -> Decimal:
        if base == "MZN":
            return MOCK_RATES_FROM_MZN.get(quote, Decimal("1"))
        if quote == "MZN":
            rate_to_mzn = MOCK_RATES_FROM_MZN.get(base, Decimal("1"))
            return Decimal("1") / rate_to_mzn if rate_to_mzn else Decimal("1")
        from_rate = MOCK_RATES_FROM_MZN.get(base, Decimal("1"))
        to_rate = MOCK_RATES_FROM_MZN.get(quote, Decimal("1"))
        return to_rate / from_rate

    async def get_rate(self, base: str, quote: str) -> Decimal:
        base, quote = base.upper(), quote.upper()

        if base == quote:
            return Decimal("1")

        cached = self._get_cached(base, quote)
        if cached and self._is_fresh(cached):
            return cached.rate

        api_rate = await self._fetch_from_api(base, quote)
        if api_rate is not None:
            self._save_rate(base, quote, api_rate, source="api")
            return api_rate

        # API falhou — usa cache antigo se existir, mesmo expirado, em vez de ir direto pro mock
        if cached:
            return cached.rate

        mock_rate = self._mock_rate(base, quote)
        self._save_rate(base, quote, mock_rate, source="mock")
        return mock_rate

    async def convert(self, base: str, quote: str, amount: Decimal) -> tuple[Decimal, Decimal]:
        """Retorna (valor_convertido, taxa_utilizada), arredondado a 2 casas decimais."""
        rate = await self.get_rate(base, quote)
        converted = (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return converted, rate

    async def get_all_rates(self, base: str = "MZN") -> dict[str, Decimal]:
        """Retorna a taxa de MZN para todas as moedas suportadas — usado no dashboard."""
        rates = {}
        for currency in settings.SUPPORTED_CURRENCIES:
            rates[currency] = await self.get_rate(base, currency)
        return rates
