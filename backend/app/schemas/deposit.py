import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.deposit import DepositProvider, DepositStatus


class DepositCreate(BaseModel):
    provider: DepositProvider
    amount: Decimal = Field(gt=0, description="Valor deve ser maior que zero")
    phone: str = Field(min_length=9, max_length=20, description="Número usado no M-Pesa/e-Mola")

    @field_validator("amount")
    @classmethod
    def amount_precision(cls, v: Decimal) -> Decimal:
        return round(v, 2)


class DepositConfirm(BaseModel):
    reference_code: str


class DepositOut(BaseModel):
    id: uuid.UUID
    provider: DepositProvider
    reference_code: str
    amount: Decimal
    currency: str
    status: DepositStatus
    created_at: datetime
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
