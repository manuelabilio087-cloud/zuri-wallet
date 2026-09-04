import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.withdrawal import Withdrawal


class WithdrawalRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, withdrawal: Withdrawal) -> Withdrawal:
        self.db.add(withdrawal)
        self.db.commit()
        self.db.refresh(withdrawal)
        return withdrawal

    def get_by_id_for_user(self, withdrawal_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Withdrawal]:
        return (
            self.db.query(Withdrawal)
            .filter(Withdrawal.id == withdrawal_id, Withdrawal.user_id == user_id)
            .first()
        )

    def update(self, withdrawal: Withdrawal) -> Withdrawal:
        self.db.commit()
        self.db.refresh(withdrawal)
        return withdrawal

    def list_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[Withdrawal]:
        return (
            self.db.query(Withdrawal)
            .filter(Withdrawal.user_id == user_id)
            .order_by(Withdrawal.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
