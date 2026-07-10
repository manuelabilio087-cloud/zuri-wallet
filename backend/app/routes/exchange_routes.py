from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services.exchange_service import ExchangeEngine

router = APIRouter(prefix="/api/v1/exchange", tags=["Câmbio"])


@router.get("/rates")
async def get_current_rates(
    base: str = "MZN",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retorna a taxa de câmbio atual (com cache) de `base` para todas as moedas suportadas."""
    engine = ExchangeEngine(db)
    rates = await engine.get_all_rates(base)
    return {"base": base.upper(), "rates": {k: str(v) for k, v in rates.items()}}
