from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository

MAX_PIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


class PinService:
    """
    PIN de 4 dígitos, independente da senha da conta, usado só para
    autorizar levantamentos. Guardado com o mesmo hashing da senha
    (nunca em texto simples). Bloqueia temporariamente após tentativas
    falhadas seguidas — protege contra alguém a tentar adivinhar o PIN
    mesmo já tendo roubado uma sessão válida.
    """

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def set_pin(self, user: User, account_password: str, new_pin: str) -> None:
        # Exige a senha da conta para definir/mudar o PIN — evita que quem
        # rouba só o acesso à sessão (ex.: um token) consiga também trocar
        # o PIN e depois esvaziar a wallet à vontade.
        if not verify_password(account_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha da conta incorreta")

        user.transaction_pin_hash = hash_password(new_pin)
        user.pin_failed_attempts = 0
        user.pin_locked_until = None
        self.user_repo.update(user)

    def verify_pin(self, user: User, pin: str) -> None:
        if user.transaction_pin_hash is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ainda não definiste um PIN de levantamento. Define um em Perfil > Segurança.",
            )

        locked_until = user.pin_locked_until
        if locked_until is not None:
            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=timezone.utc)
            if locked_until > datetime.now(timezone.utc):
                minutos = max(1, int((locked_until - datetime.now(timezone.utc)).total_seconds() // 60) + 1)
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"PIN bloqueado por demasiadas tentativas erradas. Tenta novamente em ~{minutos} min.",
                )

        if not verify_password(pin, user.transaction_pin_hash):
            user.pin_failed_attempts += 1
            if user.pin_failed_attempts >= MAX_PIN_ATTEMPTS:
                user.pin_locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
                user.pin_failed_attempts = 0
                self.user_repo.update(user)
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"PIN bloqueado por {LOCKOUT_MINUTES} minutos após várias tentativas erradas.",
                )
            self.user_repo.update(user)
            restantes = MAX_PIN_ATTEMPTS - user.pin_failed_attempts
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PIN incorreto. Tentativas restantes: {restantes}.",
            )

        # PIN certo — repõe o contador.
        if user.pin_failed_attempts != 0:
            user.pin_failed_attempts = 0
            self.user_repo.update(user)
