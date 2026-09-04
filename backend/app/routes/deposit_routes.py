from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.deposit import DepositCreate, DepositConfirm, DepositOut
from app.services.deposit_service import DepositService

router = APIRouter(prefix="/api/v1/deposits", tags=["Depósitos"])

# Router à parte, de propósito: dá para o main.py decidir, com uma linha,
# se este endpoint sequer existe no ambiente atual — nunca fica disponível
# em produção, seja qual for o estado das credenciais dos provedores.
dev_router = APIRouter(prefix="/api/v1/deposits", tags=["Depósitos (dev)"])


@router.post("", response_model=DepositOut, status_code=201)
async def create_deposit(
    data: DepositCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = DepositService(db)
    return await service.create_deposit(current_user.id, data.provider, data.amount, data.phone)


@dev_router.post("/simulate-confirm", response_model=DepositOut)
def simulate_confirm_deposit(
    data: DepositConfirm,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Só existe fora de produção — ver registo condicional em main.py.
    # Em produção, a confirmação só acontece via webhook assinado do provedor.
    service = DepositService(db)
    return service.simulate_confirm_deposit(current_user.id, data.reference_code)


@router.get("", response_model=list[DepositOut])
def list_my_deposits(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = DepositService(db)
    return service.list_user_deposits(current_user.id, skip, limit)
