import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.core.config import settings
from app.models.withdrawal import WithdrawalStatus


class WithdrawalCreate(BaseModel):
    currency: str = Field(default="USD", description="Moeda debitada da wallet (por agora, só USD)")
    amount: Decimal = Field(gt=0, description="Valor a levantar, na moeda escolhida")
    destination_address: str = Field(min_length=10, max_length=200, description="Endereço/UID da tua conta Binance")
    network: str = Field(default="", validate_default=True, description="Rede de envio (ex.: BSC, TRX). Se vazio, usa a rede por omissão")
    pin: str = Field(min_length=4, max_length=4, description="O teu PIN de levantamento de 4 dígitos")

    @field_validator("currency")
    @classmethod
    def currency_upper(cls, v: str) -> str:
        v = v.upper()
        if v != "USD":
            raise ValueError("Por agora, levantamento só é suportado em USD")
        return v

    @field_validator("amount")
    @classmethod
    def amount_precision_and_minimum(cls, v: Decimal) -> Decimal:
        v = round(v, 2)
        if v < settings.WITHDRAWAL_MIN_AMOUNT_USD:
            raise ValueError(f"Valor mínimo de levantamento é {settings.WITHDRAWAL_MIN_AMOUNT_USD} USD")
        return v

    @field_validator("network")
    @classmethod
    def network_default(cls, v: str) -> str:
        return v.upper() if v else settings.BINANCE_DEFAULT_NETWORK


class WithdrawalOut(BaseModel):
    id: uuid.UUID
    currency: str
    amount: Decimal
    asset: str
    network: str
    destination_address: str
    status: WithdrawalStatus
    failure_reason: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
