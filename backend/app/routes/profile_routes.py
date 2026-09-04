from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserOut, UserUpdate, PinSet
from app.services.pin_service import PinService

router = APIRouter(prefix="/api/v1/profile", tags=["Perfil"])


@router.get("", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.patch("", response_model=UserOut)
def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    return repo.update(current_user)


@router.post("/pin", status_code=204)
@limiter.limit("5/minute")
def set_transaction_pin(
    request: Request,
    data: PinSet,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = PinService(db)
    service.set_pin(current_user, data.account_password, data.pin)
