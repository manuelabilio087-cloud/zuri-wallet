import uuid
from decimal import Decimal

from pydantic import BaseModel


class WalletBalanceOut(BaseModel):
    currency: str
    balance: Decimal

    class Config:
        from_attributes = True


class WalletOut(BaseModel):
    id: uuid.UUID
    balances: list[WalletBalanceOut]

    class Config:
        from_attributes = True


class ConversionPreviewRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: Decimal


class ConversionPreviewResponse(BaseModel):
    from_currency: str
    to_currency: str
    original_amount: Decimal
    converted_amount: Decimal
    exchange_rate: Decimal
