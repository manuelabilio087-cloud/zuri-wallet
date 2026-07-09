from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionListResponse

router = APIRouter(prefix="/api/v1/transactions", tags=["Histórico"])


@router.get("", response_model=TransactionListResponse)
def list_my_transactions(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    repo = TransactionRepository(db)
    skip = (page - 1) * page_size
    items = repo.list_by_user(current_user.id, skip=skip, limit=page_size)
    total = repo.count_by_user(current_user.id)
    return TransactionListResponse(total=total, page=page, page_size=page_size, items=items)
