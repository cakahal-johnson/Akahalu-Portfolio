from pydantic import EmailStr, Field, SecretStr

from app.schemas.base import DatabaseSchema, SchemaBase
from app.schemas.role import RoleRead


class UserBase(SchemaBase):
    email: EmailStr

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

    avatar_url: str | None = Field(
        default=None,
        max_length=2048,
    )


class UserCreate(UserBase):
    password: SecretStr = Field(
        min_length=12,
        max_length=128,
    )


class UserRead(UserBase, DatabaseSchema):
    is_active: bool
    is_verified: bool
    is_superuser: bool

    roles: list[RoleRead] = Field(
        default_factory=list,
    )
