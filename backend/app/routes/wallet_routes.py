from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.wallet import WalletOut, ConversionPreviewRequest, ConversionPreviewResponse
from app.services.wallet_service import WalletService
from app.services.exchange_service import ExchangeEngine

router = APIRouter(prefix="/api/v1/wallet", tags=["Wallet"])


@router.get("/me", response_model=WalletOut)
def get_my_wallet(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = WalletService(db)
    return service.get_wallet(current_user.id)


@router.post("/convert-preview", response_model=ConversionPreviewResponse)
async def preview_conversion(
    data: ConversionPreviewRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    exchange_engine = ExchangeEngine(db)
    converted, rate = await exchange_engine.convert(data.from_currency, data.to_currency, data.amount)
    return ConversionPreviewResponse(
        from_currency=data.from_currency.upper(),
        to_currency=data.to_currency.upper(),
        original_amount=data.amount,
        converted_amount=converted,
        exchange_rate=rate,
    )
