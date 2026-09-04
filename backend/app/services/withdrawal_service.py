import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.repositories.withdrawal_repository import WithdrawalRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.pin_service import PinService
from app.services.wallet_service import WalletService
from app.services.withdraw_providers.binance import BinanceWithdrawAdapter


class WithdrawalService:
    """
    Orquestra o levantamento: valida o PIN de transação, debita a wallet
    (com lock, para não haver double-spend), pede à Binance para enviar o
    valor, e se a Binance recusar o pedido, devolve o saldo automaticamente.

    Único provedor de saída de fundos: Binance. Não há levantamento por
    M-Pesa/e-Mola/banco nesta fase.
    """

    def __init__(self, db: Session):
        self.db = db
        self.withdrawal_repo = WithdrawalRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.wallet_service = WalletService(db)
        self.pin_service = PinService(db)
        self.provider = BinanceWithdrawAdapter()

    async def create_withdrawal(
        self,
        user: User,
        currency: str,
        amount: Decimal,
        asset: str,
        network: str,
        destination_address: str,
        pin: str,
    ) -> Withdrawal:
        # 1. PIN primeiro — antes de tocar em qualquer saldo. Levanta
        #    HTTPException (400 errado / 423 bloqueado) e para tudo aqui.
        self.pin_service.verify_pin(user, pin)

        # 2. Debita já — se não houver saldo, wallet_service já lança HTTPException aqui.
        self.wallet_service.debit(user.id, currency, amount)

        # 3. Regista o levantamento como PENDING antes de chamar o provedor,
        #    para nunca perder o rasto de dinheiro já saído da wallet.
        withdrawal = Withdrawal(
            user_id=user.id,
            currency=currency,
            amount=amount,
            asset=asset,
            network=network,
            destination_address=destination_address,
            status=WithdrawalStatus.PENDING,
        )
        withdrawal = self.withdrawal_repo.create(withdrawal)

        transaction = Transaction(
            user_id=user.id,
            type=TransactionType.WITHDRAWAL,
            currency=currency,
            amount=amount,
            status=TransactionStatus.PENDING,
            notes=f"Levantamento via Binance para {destination_address[:10]}...",
        )
        transaction = self.transaction_repo.create(transaction)
        withdrawal.transaction_id = transaction.id
        self.withdrawal_repo.update(withdrawal)

        # 4. Chama a Binance. Se falhar por qualquer razão, reembolsa de imediato.
        try:
            result = await self.provider.send_withdrawal(
                amount=amount,
                asset=asset,
                network=network,
                address=destination_address,
                client_reference=str(withdrawal.id),
            )
        except Exception as e:
            self._refund_and_fail(withdrawal, transaction, reason=str(e))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Não foi possível enviar o levantamento à Binance. O valor foi devolvido à tua wallet.",
            )

        if result.status == "failed":
            self._refund_and_fail(withdrawal, transaction, reason="Binance recusou o pedido de saque")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="A Binance recusou o pedido de saque. O valor foi devolvido à tua wallet.",
            )

        withdrawal.status = WithdrawalStatus.PROCESSING
        withdrawal.binance_withdrawal_id = result.provider_withdrawal_id
        withdrawal.provider_response = str(result.raw_response)[:1000]
        self.withdrawal_repo.update(withdrawal)

        transaction.status = TransactionStatus.COMPLETED
        self.transaction_repo.update(transaction)

        return withdrawal

    def _refund_and_fail(self, withdrawal: Withdrawal, transaction: Transaction, reason: str) -> None:
        self.wallet_service.credit(withdrawal.user_id, withdrawal.currency, withdrawal.amount)
        withdrawal.status = WithdrawalStatus.FAILED
        withdrawal.failure_reason = reason[:500]
        self.withdrawal_repo.update(withdrawal)
        transaction.status = TransactionStatus.FAILED
        self.transaction_repo.update(transaction)

    def list_withdrawals(self, user_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[Withdrawal]:
        return self.withdrawal_repo.list_by_user(user_id, skip, limit)

    def get_withdrawal(self, user_id: uuid.UUID, withdrawal_id: uuid.UUID) -> Withdrawal:
        withdrawal = self.withdrawal_repo.get_by_id_for_user(withdrawal_id, user_id)
        if withdrawal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Levantamento não encontrado")
        return withdrawal
