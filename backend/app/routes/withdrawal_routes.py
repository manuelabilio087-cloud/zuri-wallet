import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.schemas.withdrawal import WithdrawalCreate, WithdrawalOut
from app.services.withdrawal_service import WithdrawalService

router = APIRouter(prefix="/api/v1/withdrawals", tags=["Levantamentos"])


@router.post("", response_model=WithdrawalOut, status_code=201)
@limiter.limit("5/minute")
async def create_withdrawal(
    request: Request,
    data: WithdrawalCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = WithdrawalService(db)
    return await service.create_withdrawal(
        user_id=current_user.id,
        currency=data.currency,
        amount=data.amount,
        asset="USDT",
        network=data.network,
        destination_address=data.destination_address,
    )


@router.get("", response_model=list[WithdrawalOut])
def list_my_withdrawals(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = WithdrawalService(db)
    return service.list_withdrawals(current_user.id, skip, limit)


@router.get("/{withdrawal_id}", response_model=WithdrawalOut)
def get_withdrawal(
    withdrawal_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = WithdrawalService(db)
    return service.get_withdrawal(current_user.id, withdrawal_id)
