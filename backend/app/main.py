from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.middleware.rate_limit import limiter
from app.routes import (
    auth_routes,
    wallet_routes,
    deposit_routes,
    withdrawal_routes,
    transaction_routes,
    profile_routes,
    exchange_routes,
    webhook_routes,
)

app = FastAPI(
    title=settings.APP_NAME,
    description="API da Zuri Wallet - Carteira digital multimoeda",
    version="0.1.0",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Padroniza o formato de erro de todas as respostas da API
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if settings.APP_DEBUG:
        raise exc
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "Erro interno do servidor"},
    )


app.include_router(auth_routes.router)
app.include_router(wallet_routes.router)
app.include_router(deposit_routes.router)
if settings.APP_ENV != "production":
    app.include_router(deposit_routes.dev_router)
app.include_router(withdrawal_routes.router)
app.include_router(transaction_routes.router)
app.include_router(profile_routes.router)
app.include_router(exchange_routes.router)
app.include_router(webhook_routes.router)


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "online", "env": settings.APP_ENV}


@app.get("/health")
def health_check():
    return {"status": "ok"}
