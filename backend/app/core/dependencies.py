from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserStatus

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if user.status == UserStatus.BLOCKED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta bloqueada. Contacte o suporte.",
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.status == UserStatus.PENDING_VERIFICATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="É necessário verificar o e-mail antes de continuar.",
        )
    return current_user
