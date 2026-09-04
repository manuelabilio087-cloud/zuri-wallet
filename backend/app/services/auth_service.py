import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.token import Token, TokenType
from app.models.user import User, UserStatus
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegister, UserLogin
from app.services.email_service import EmailService
from app.services.wallet_service import WalletService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)
        self.wallet_service = WalletService(db)
        self.email_service = EmailService()

    def register(self, data: UserRegister) -> User:
        existing = self.user_repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma conta com este e-mail",
            )

        user = User(
            full_name=data.full_name.strip(),
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            phone=data.phone,
            birth_date=data.birth_date,
            country=data.country,
            city=data.city,
            status=UserStatus.ACTIVE,
        )
        user = self.user_repo.create(user)

        self.wallet_service.create_wallet_for_user(user.id)

        return user

    def authenticate(self, data: UserLogin) -> User:
        user = self.user_repo.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha incorretos",
            )

        if user.status == UserStatus.BLOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conta bloqueada. Contacte o suporte.",
            )

        user.last_login_at = datetime.now(timezone.utc)
        self.user_repo.update(user)
        return user

    def issue_tokens(self, user: User) -> dict:
        """
        Emite o par de tokens. O refresh token é registado na tabela `tokens`
        (pelo jti, não pelo JWT completo) — é isto que torna possível
        revogá-lo depois (logout) e detectar reuso de um token já rodado.
        """
        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        refresh_token, _ = self._issue_refresh_token(user)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    def _issue_refresh_token(self, user: User) -> tuple[str, Token]:
        jti = secrets.token_hex(24)
        refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email, "jti": jti})

        token_row = Token(
            user_id=user.id,
            token_type=TokenType.REFRESH,
            token_value=jti,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )
        token_row = self.token_repo.create(token_row)
        return refresh_token, token_row

    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Valida o refresh token contra a tabela `tokens` (não só a assinatura
        JWT) e faz rotação: o token usado é invalidado e um novo é emitido.
        Isto significa que um refresh token só serve uma vez — se alguém o
        roubar e o usar depois de ti, o teu próximo pedido falha (sinal de
        comprometimento), em vez de ambos continuarem a funcionar em paralelo
        até à expiração de 7 dias.
        """
        invalid = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada ou inválida. Inicia sessão novamente.",
        )

        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh" or not payload.get("jti"):
            raise invalid

        token_row = self.token_repo.get_valid(payload["jti"], TokenType.REFRESH)
        if token_row is None:
            raise invalid

        user = self.user_repo.get_by_id(payload.get("sub"))
        if user is None or user.status == UserStatus.BLOCKED:
            raise invalid

        self.token_repo.mark_used(token_row)
        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        new_refresh_token, _ = self._issue_refresh_token(user)
        return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

    def logout(self, refresh_token: str | None) -> None:
        """Revoga o refresh token atual. Idempotente — chamar sem token válido não é erro."""
        if not refresh_token:
            return
        payload = decode_token(refresh_token)
        if payload and payload.get("jti"):
            self.token_repo.invalidate_by_value(payload["jti"], TokenType.REFRESH)

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta",
            )
        user.password_hash = hash_password(new_password)
        self.user_repo.update(user)

    def request_password_reset(self, email: str) -> None:
        """
        Sempre "sucede" do ponto de vista de quem chama, exista ou não a
        conta — não confirmamos por aqui se um email está registado
        (evita que alguém use isto para descobrir contas existentes).
        """
        user = self.user_repo.get_by_email(email)
        if user is None:
            return

        reset_token = secrets.token_urlsafe(32)
        token_row = Token(
            user_id=user.id,
            token_type=TokenType.PASSWORD_RESET,
            token_value=reset_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        self.token_repo.create(token_row)
        self.email_service.send_password_reset(user.email, reset_token)

    def confirm_password_reset(self, token: str, new_password: str) -> None:
        token_row = self.token_repo.get_valid(token, TokenType.PASSWORD_RESET)
        if token_row is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Link de recuperação inválido ou expirado",
            )

        user = self.user_repo.get_by_id(str(token_row.user_id))
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Utilizador não encontrado")

        user.password_hash = hash_password(new_password)
        self.user_repo.update(user)
        self.token_repo.mark_used(token_row)
