from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=12,
        max_length=128,
    )
    first_name: str = Field(
        min_length=1,
        max_length=100,
    )
    last_name: str = Field(
        min_length=1,
        max_length=100,
    )
    display_name: str | None = Field(
        default=None,
        max_length=150,
    )

    @field_validator(
        "first_name",
        "last_name",
        mode="before",
    )
    @classmethod
    def normalize_required_name(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        if not normalized_value:
            raise ValueError("Name cannot be empty.")

        return normalized_value

    @field_validator(
        "display_name",
        mode="before",
    )
    @classmethod
    def normalize_display_name(
        cls,
        value: object,
    ) -> object:
        if value is None:
            return None

        if not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        return normalized_value or None


class RegisteredUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    display_name: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime


class RegisterResponse(BaseModel):
    user: RegisteredUserResponse
    message: str

    # Temporary until email delivery is implemented.
    verification_token: str
    verification_token_expires_at: datetime


class VerifyEmailRequest(BaseModel):
    token: str = Field(
        min_length=1,
        max_length=512,
    )

    @field_validator("token")
    @classmethod
    def normalize_token(
        cls,
        value: str,
    ) -> str:
        normalized_token = value.strip()

        if not normalized_token:
            raise ValueError("Verification token cannot be empty.")

        return normalized_token


class VerifyEmailResponse(BaseModel):
    user: RegisteredUserResponse
    message: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ResendVerificationResponse(BaseModel):
    message: str

    # Temporary until email delivery is implemented.
    verification_token: str | None = None
    verification_token_expires_at: datetime | None = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator(
        "email",
        mode="before",
    )
    @classmethod
    def normalize_email(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, str):
            return value

        return value.strip().lower()


class ForgotPasswordResponse(BaseModel):
    message: str

    # Temporary until email delivery is implemented.
    reset_token: str | None = None
    reset_token_expires_at: datetime | None = None


class ResetPasswordRequest(BaseModel):
    token: str = Field(
        min_length=1,
        max_length=512,
    )
    new_password: str = Field(
        min_length=12,
        max_length=128,
    )

    @field_validator("token")
    @classmethod
    def normalize_token(
        cls,
        value: str,
    ) -> str:
        normalized_token = value.strip()

        if not normalized_token:
            raise ValueError("Password-reset token cannot be empty.")

        return normalized_token


class ResetPasswordResponse(BaseModel):
    message: str
