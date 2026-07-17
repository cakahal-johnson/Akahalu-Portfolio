from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field, SecretStr

from app.schemas.base import SchemaBase
from app.schemas.user import UserRead


class LoginRequest(SchemaBase):
    email: EmailStr
    password: SecretStr = Field(
        min_length=1,
        max_length=128,
    )


class RefreshRequest(SchemaBase):
    refresh_token: SecretStr = Field(
        min_length=32,
        max_length=512,
    )


class LogoutRequest(SchemaBase):
    refresh_token: SecretStr | None = Field(
        default=None,
        min_length=32,
        max_length=512,
    )


class AccessTokenClaims(SchemaBase):
    subject: UUID
    session_id: UUID
    token_id: UUID
    issued_at: datetime
    expires_at: datetime


class TokenPair(SchemaBase):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime


class LoginResponse(SchemaBase):
    user: UserRead
    tokens: TokenPair
