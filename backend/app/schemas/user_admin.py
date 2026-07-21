from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import EmailStr, Field, model_validator

from app.schemas.base import SchemaBase
from app.schemas.role import RoleRead


class UserStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class UserSortField(StrEnum):
    CREATED_AT = "created_at"
    EMAIL = "email"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    DISPLAY_NAME = "display_name"


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


class AdminUserListQuery(SchemaBase):
    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    status: UserStatus | None = None
    is_verified: bool | None = None
    is_superuser: bool | None = None
    include_deleted: bool = False

    sort_by: UserSortField = UserSortField.CREATED_AT
    sort_direction: SortDirection = SortDirection.DESC


class AdminUserSummary(SchemaBase):
    id: UUID
    email: EmailStr

    first_name: str
    last_name: str
    display_name: str | None = None
    avatar_url: str | None = None

    is_active: bool
    is_verified: bool
    is_superuser: bool
    is_deleted: bool

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    roles: list[RoleRead] = Field(
        default_factory=list,
    )


class AdminUserDetail(AdminUserSummary):
    last_login_at: datetime | None = None


class AdminUserListResponse(SchemaBase):
    items: list[AdminUserSummary] = Field(
        default_factory=list,
    )

    page: int = Field(
        ge=1,
    )

    page_size: int = Field(
        ge=1,
    )

    total_items: int = Field(
        ge=0,
    )

    total_pages: int = Field(
        ge=0,
    )

    has_next_page: bool
    has_previous_page: bool


class AdminUserStatusUpdate(SchemaBase):
    is_active: bool
    reason: str | None = Field(
        default=None,
        min_length=3,
        max_length=500,
    )


class AdminUserDeleteRequest(SchemaBase):
    reason: str | None = Field(
        default=None,
        min_length=3,
        max_length=500,
    )


class AdminUserRestoreRequest(SchemaBase):
    activate: bool = True
    reason: str | None = Field(
        default=None,
        min_length=3,
        max_length=500,
    )


class AdminUserProfileUpdate(SchemaBase):
    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
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

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "AdminUserProfileUpdate":
        if all(
            value is None
            for value in (
                self.first_name,
                self.last_name,
                self.display_name,
                self.avatar_url,
            )
        ):
            raise ValueError("At least one profile field must be provided.")

        return self
