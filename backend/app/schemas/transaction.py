import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.transaction import TransactionType, TransactionStatus


class TransactionOut(BaseModel):
    id: uuid.UUID
    type: TransactionType
    status: TransactionStatus
    amount: Decimal
    currency: str
    exchange_rate: Optional[Decimal] = None
    source_currency: Optional[str] = None
    source_amount: Optional[Decimal] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TransactionOut]
