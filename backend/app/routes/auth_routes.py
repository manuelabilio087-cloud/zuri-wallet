from fastapi import APIRouter, Depends, Request, Response, Cookie, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.schemas.auth import LoginResponse, AccessTokenResponse
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserOut,
    PasswordChange,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])

REFRESH_COOKIE_NAME = "zuri_refresh_token"
REFRESH_COOKIE_PATH = "/api/v1/auth"


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="strict",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path=REFRESH_COOKIE_PATH,
    )


@router.post("/register", response_model=UserOut, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(data)
    return user


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
def login(request: Request, response: Response, data: UserLogin, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.authenticate(data)
    tokens = service.issue_tokens(user)
    _set_refresh_cookie(response, tokens["refresh_token"])
    return {"user": user, "tokens": {"access_token": tokens["access_token"], "token_type": "bearer"}}


@router.post("/refresh", response_model=AccessTokenResponse)
@limiter.limit("20/minute")
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
):
    service = AuthService(db)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão não encontrada")

    tokens = service.refresh_access_token(refresh_token)
    _set_refresh_cookie(response, tokens["refresh_token"])
    return {"access_token": tokens["access_token"], "token_type": "bearer"}


@router.post("/logout", status_code=204)
def logout(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
):
    service = AuthService(db)
    service.logout(refresh_token)
    response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)


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


@router.post("/password-reset/request", status_code=204)
@limiter.limit("3/minute")
def request_password_reset(request: Request, data: PasswordResetRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.request_password_reset(data.email)
    # Resposta é sempre 204, exista ou não a conta — ver comentário em request_password_reset.


@router.post("/password-reset/confirm", status_code=204)
@limiter.limit("5/minute")
def confirm_password_reset(request: Request, data: PasswordResetConfirm, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.confirm_password_reset(data.token, data.new_password)
