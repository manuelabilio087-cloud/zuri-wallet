from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.schemas.auth import LoginResponse, RefreshRequest, AccessTokenResponse
from app.schemas.user import UserRegister, UserLogin, UserOut, PasswordChange
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])


@router.post("/register", response_model=UserOut, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(data)
    return user


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.authenticate(data)
    tokens = service.issue_tokens(user)
    return {"user": user, "tokens": tokens}


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    access_token = service.refresh_access_token(data.refresh_token)
    return {"access_token": access_token}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password", status_code=204)
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    service.change_password(current_user, data.current_password, data.new_password)
    return None


@router.post("/logout", status_code=204)
def logout(current_user: User = Depends(get_current_user)):
    # Nesta fase, logout é responsabilidade do cliente (descartar o token).
    # Próxima fase: invalidar refresh token via blocklist no Redis.
    return None
