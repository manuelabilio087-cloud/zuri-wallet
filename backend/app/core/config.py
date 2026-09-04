from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# app/core/config.py -> app/core -> app -> backend -> raiz do projeto (onde está o .env)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Zuri Wallet"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "Zuri Wallet <no-reply@zuriwallet.com>"

    # M-Pesa
    MPESA_API_KEY: str = ""
    MPESA_PUBLIC_KEY: str = ""
    MPESA_ORIGIN: str = ""
    MPESA_ENV: str = "sandbox"

    # e-Mola
    EMOLA_API_KEY: str = ""
    EMOLA_ENV: str = "sandbox"

    # Exchange Rate — câmbio de mercado real (não é a Binance).
    # open.er-api.com é aberto e gratuito, sem chave — atualiza 1x/dia.
    EXCHANGE_RATE_API_URL: str = "https://open.er-api.com/v6"
    EXCHANGE_RATE_API_KEY: str = ""

    # Binance — única via de levantamento (envio de USDT). Não tem relação
    # nenhuma com EXCHANGE_RATE_API_URL, que é o câmbio de mercado real.
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    BINANCE_DEFAULT_NETWORK: str = "BSC"
    WITHDRAWAL_MIN_AMOUNT_USD: float = 10.0

    # Currencies suportadas pela wallet
    SUPPORTED_CURRENCIES: list[str] = ["MZN", "USD", "EUR", "BRL", "GBP", "ZAR"]

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
