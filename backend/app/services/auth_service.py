from datetime import datetime, timezone

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
from app.models.user import User, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegister, UserLogin
from app.services.wallet_service import WalletService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.wallet_service = WalletService(db)

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
        payload = {"sub": str(user.id), "email": user.email}
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "token_type": "bearer",
        }

    def refresh_access_token(self, refresh_token: str) -> str:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado",
            )

        user = self.user_repo.get_by_id(payload.get("sub"))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilizador não encontrado",
            )

        new_payload = {"sub": str(user.id), "email": user.email}
        return create_access_token(new_payload)

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta",
            )
        user.password_hash = hash_password(new_password)
        self.user_repo.update(user)