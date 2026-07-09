from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.deposit import DepositCreate, DepositConfirm, DepositOut
from app.services.deposit_service import DepositService

router = APIRouter(prefix="/api/v1/deposits", tags=["Depósitos"])


@router.post("", response_model=DepositOut, status_code=201)
def create_deposit(
    data: DepositCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = DepositService(db)
    return service.create_deposit(current_user.id, data.provider, data.amount, data.phone)


@router.post("/confirm", response_model=DepositOut)
def confirm_deposit(
    data: DepositConfirm,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Nesta fase (simulada), o próprio usuário confirma via app.
    # Em produção, isso seria um webhook do provedor M-Pesa/e-Mola, sem depender do usuário.
    service = DepositService(db)
    return service.confirm_deposit(data.reference_code)


@router.get("", response_model=list[DepositOut])
def list_my_deposits(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = DepositService(db)
    return service.list_user_deposits(current_user.id, skip, limit)
