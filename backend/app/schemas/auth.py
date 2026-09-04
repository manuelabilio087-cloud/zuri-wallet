from pydantic import BaseModel

from app.schemas.user import UserOut


class TokenPair(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    user: UserOut
    tokens: TokenPair


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
