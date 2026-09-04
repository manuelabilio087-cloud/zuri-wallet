import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.token import Token, TokenType


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, token: Token) -> Token:
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_valid(self, token_value: str, token_type: TokenType) -> Optional[Token]:
        """Devolve o token só se existir, for do tipo certo, não usado e não expirado."""
        token = (
            self.db.query(Token)
            .filter(Token.token_value == token_value, Token.token_type == token_type)
            .first()
        )
        if token is None or token.is_used:
            return None
        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            return None
        return token

    def mark_used(self, token: Token) -> None:
        token.is_used = True
        self.db.commit()

    def invalidate_by_value(self, token_value: str, token_type: TokenType) -> None:
        """Usado no logout: revoga sem exigir que ainda esteja 'válido' (idempotente)."""
        token = (
            self.db.query(Token)
            .filter(Token.token_value == token_value, Token.token_type == token_type)
            .first()
        )
        if token is not None and not token.is_used:
            token.is_used = True
            self.db.commit()
