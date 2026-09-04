import uuid
import json
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
from app.services.payment_providers.factory import get_payment_provider


def _generate_reference(provider: DepositProvider) -> str:
    prefix = "MP" if provider == DepositProvider.MPESA else "EM"
    return f"{prefix}-{secrets.token_hex(4).upper()}"


class DepositService:
    """
    Orquestra o fluxo de depósito: gera referência, delega ao adaptador do
    provedor certo (M-Pesa/e-Mola/futuros), credita a wallet e regista tudo
    no histórico. Não conhece detalhes de nenhuma API externa — isso vive
    inteiramente dentro de cada adaptador (services/payment_providers/).
    """

    def __init__(self, db: Session):
        self.db = db
        self.deposit_repo = DepositRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.wallet_service = WalletService(db)

    async def create_deposit(self, user_id: uuid.UUID, provider: DepositProvider, amount: Decimal, phone: str) -> Deposit:
        reference_code = _generate_reference(provider)
        adapter = get_payment_provider(provider)

        result = await adapter.create_payment_request(amount, phone, reference_code)

        deposit = Deposit(
            user_id=user_id,
            provider=provider,
            reference_code=reference_code,
            amount=amount,
            currency="MZN",
            status=DepositStatus.PENDING if result.status == "pending" else DepositStatus.FAILED,
            provider_response=json.dumps(result.raw_response)[:1000],
        )
        return self.deposit_repo.create(deposit)

    def confirm_deposit(self, reference_code: str) -> Deposit:
        """
        Confirma um depósito. Chamado só internamente pelo webhook_service
        quando um callback assinado e válido chega — nunca diretamente por
        um utilizador (ver simulate_confirm_deposit para o caminho de dev).
        """
        deposit = self.deposit_repo.get_by_reference(reference_code)
        if deposit is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depósito não encontrado")

        return self._apply_confirmation(deposit)

    def simulate_confirm_deposit(self, user_id: uuid.UUID, reference_code: str) -> Deposit:
        """
        Caminho de DESENVOLVIMENTO apenas — a rota que chama isto só existe
        fora de produção (ver routes/deposit_routes.py). Confirma na mesma
        só o dono do depósito, para não abrir a porta a confirmar depósitos
        de outros utilizadores mesmo em ambiente de testes.
        """
        deposit = self.deposit_repo.get_by_reference(reference_code)
        if deposit is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depósito não encontrado")
        if deposit.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Este depósito não é teu")

        return self._apply_confirmation(deposit)

    def _apply_confirmation(self, deposit: Deposit) -> Deposit:
        if deposit.status == DepositStatus.CONFIRMED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Depósito já confirmado")

        self.wallet_service.credit(deposit.user_id, "MZN", deposit.amount)

        transaction = Transaction(
            user_id=deposit.user_id,
            type=TransactionType.DEPOSIT,
            status=TransactionStatus.COMPLETED,
            amount=deposit.amount,
            currency="MZN",
            notes=f"Depósito via {deposit.provider.value} - ref {deposit.reference_code}",
        )
        transaction = self.transaction_repo.create(transaction)

        deposit.status = DepositStatus.CONFIRMED
        deposit.confirmed_at = datetime.now(timezone.utc)
        deposit.transaction_id = transaction.id
        return self.deposit_repo.update(deposit)

    def list_user_deposits(self, user_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[Deposit]:
        return self.deposit_repo.list_by_user(user_id, skip, limit)
