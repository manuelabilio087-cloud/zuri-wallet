from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Exchange Rate
    EXCHANGE_RATE_API_URL: str = "https://api.exchangerate.host"
    EXCHANGE_RATE_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
