import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.deposit import Deposit


class DepositRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, deposit: Deposit) -> Deposit:
        self.db.add(deposit)
        self.db.commit()
        self.db.refresh(deposit)
        return deposit

    def get_by_reference(self, reference_code: str) -> Optional[Deposit]:
        return self.db.query(Deposit).filter(Deposit.reference_code == reference_code).first()

    def update(self, deposit: Deposit) -> Deposit:
        self.db.commit()
        self.db.refresh(deposit)
        return deposit

    def list_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[Deposit]:
        return (
            self.db.query(Deposit)
            .filter(Deposit.user_id == user_id)
            .order_by(Deposit.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
