import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.wallet import Wallet, WalletBalance


class WalletRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Wallet]:
        return (
            self.db.query(Wallet)
            .options(joinedload(Wallet.balances))
            .filter(Wallet.user_id == user_id)
            .first()
        )

    def create_for_user(self, user_id: uuid.UUID, currencies: list[str]) -> Wallet:
        wallet = Wallet(user_id=user_id)
        self.db.add(wallet)
        self.db.flush()  # garante wallet.id sem fechar a transação

        for currency in currencies:
            balance = WalletBalance(wallet_id=wallet.id, currency=currency, balance=Decimal("0.00"))
            self.db.add(balance)

        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def get_balance(self, wallet_id: uuid.UUID, currency: str) -> Optional[WalletBalance]:
        return (
            self.db.query(WalletBalance)
            .filter(WalletBalance.wallet_id == wallet_id, WalletBalance.currency == currency)
            .first()
        )

    def credit(self, wallet_id: uuid.UUID, currency: str, amount: Decimal) -> WalletBalance:
        balance = self.get_balance(wallet_id, currency)
        if balance is None:
            balance = WalletBalance(wallet_id=wallet_id, currency=currency, balance=Decimal("0.00"))
            self.db.add(balance)
            self.db.flush()

        balance.balance = balance.balance + amount
        self.db.commit()
        self.db.refresh(balance)
        return balance

    def debit(self, wallet_id: uuid.UUID, currency: str, amount: Decimal) -> WalletBalance:
        balance = self.get_balance(wallet_id, currency)
        if balance is None or balance.balance < amount:
            raise ValueError("Saldo insuficiente")

        balance.balance = balance.balance - amount
        self.db.commit()
        self.db.refresh(balance)
        return balance
