import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    full_name: str = Field(min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=30)
    birth_date: Optional[date] = None
    country: Optional[str] = "Mozambique"
    city: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("A senha deve conter pelo menos um número")
        if not any(c.isalpha() for c in v):
            raise ValueError("A senha deve conter pelo menos uma letra")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=3, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=30)
    city: Optional[str] = None
    profile_photo_url: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=100)


class EmailVerificationConfirm(BaseModel):
    token: str


class UserOut(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    country: Optional[str] = None
    city: Optional[str] = None
    profile_photo_url: Optional[str] = None
    status: str
    email_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True
