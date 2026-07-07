from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="API da Zuri Wallet - Carteira digital multimoeda",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "online", "env": settings.APP_ENV}


@app.get("/health")
def health_check():
    return {"status": "ok"}
