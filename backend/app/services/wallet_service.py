import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.wallet import Wallet
from app.repositories.wallet_repository import WalletRepository


class WalletService:
    def __init__(self, db: Session):
        self.db = db
        self.wallet_repo = WalletRepository(db)

    def create_wallet_for_user(self, user_id: uuid.UUID) -> Wallet:
        return self.wallet_repo.create_for_user(user_id, settings.SUPPORTED_CURRENCIES)

    def get_wallet(self, user_id: uuid.UUID) -> Wallet:
        wallet = self.wallet_repo.get_by_user_id(user_id)
        if wallet is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet não encontrada para este utilizador",
            )
        return wallet

    def credit(self, user_id: uuid.UUID, currency: str, amount: Decimal):
        wallet = self.get_wallet(user_id)
        return self.wallet_repo.credit(wallet.id, currency, amount)

    def debit(self, user_id: uuid.UUID, currency: str, amount: Decimal):
        wallet = self.get_wallet(user_id)
        try:
            return self.wallet_repo.debit(wallet.id, currency, amount)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
