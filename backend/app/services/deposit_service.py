import uuid
import secrets
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.deposit import Deposit, DepositProvider, DepositStatus
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.repositories.deposit_repository import DepositRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.wallet_service import WalletService


def _generate_reference(provider: DepositProvider) -> str:
    prefix = "MP" if provider == DepositProvider.MPESA else "EM"
    return f"{prefix}-{secrets.token_hex(4).upper()}"


class DepositService:
    """
    Depósitos entram sempre em MZN (moeda local via M-Pesa/e-Mola).
    Nesta fase, a confirmação é simulada — em produção, isso viria de um webhook
    do provedor (M-Pesa/e-Mola), que chamaria confirm_deposit() automaticamente.
    """

    def __init__(self, db: Session):
        self.db = db
        self.deposit_repo = DepositRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.wallet_service = WalletService(db)

    def create_deposit(self, user_id: uuid.UUID, provider: DepositProvider, amount: Decimal, phone: str) -> Deposit:
        deposit = Deposit(
            user_id=user_id,
            provider=provider,
            reference_code=_generate_reference(provider),
            amount=amount,
            currency="MZN",
            status=DepositStatus.PENDING,
        )
        return self.deposit_repo.create(deposit)

    def confirm_deposit(self, reference_code: str) -> Deposit:
        deposit = self.deposit_repo.get_by_reference(reference_code)
        if deposit is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depósito não encontrado")

        if deposit.status == DepositStatus.CONFIRMED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Depósito já confirmado")

        # 1. Credita o saldo em MZN na wallet
        self.wallet_service.credit(deposit.user_id, "MZN", deposit.amount)

        # 2. Registra a transação no histórico (nunca apagado)
        transaction = Transaction(
            user_id=deposit.user_id,
            type=TransactionType.DEPOSIT,
            status=TransactionStatus.COMPLETED,
            amount=deposit.amount,
            currency="MZN",
            notes=f"Depósito via {deposit.provider.value} - ref {deposit.reference_code}",
        )
        transaction = self.transaction_repo.create(transaction)

        # 3. Atualiza o depósito como confirmado
        deposit.status = DepositStatus.CONFIRMED
        deposit.confirmed_at = datetime.now(timezone.utc)
        deposit.transaction_id = transaction.id
        return self.deposit_repo.update(deposit)

    def list_user_deposits(self, user_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[Deposit]:
        return self.deposit_repo.list_by_user(user_id, skip, limit)
