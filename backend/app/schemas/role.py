from uuid import UUID

from pydantic import ConfigDict, Field, field_validator

from app.schemas.base import DatabaseSchema, SchemaBase
from app.schemas.permission import PermissionRead


class RoleBase(SchemaBase):
    name: str = Field(
        min_length=2,
        max_length=100,
        pattern=r"^[a-z][a-z0-9_]*$",
        examples=["super_admin"],
    )

    display_name: str = Field(
        min_length=2,
        max_length=150,
        examples=["Super Administrator"],
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    is_system: bool = False
    is_active: bool = True


class RoleCreate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    name: str = Field(
        min_length=2,
        max_length=100,
        pattern=r"^[a-z][a-z0-9_]*$",
        examples=["content_manager"],
    )

    display_name: str = Field(
        min_length=2,
        max_length=150,
        examples=["Content Manager"],
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    is_active: bool = True

    permission_ids: list[UUID] = Field(
        default_factory=list,
    )

    @field_validator("permission_ids")
    @classmethod
    def validate_permission_ids(
        cls,
        permission_ids: list[UUID],
    ) -> list[UUID]:
        if len(permission_ids) != len(set(permission_ids)):
            raise ValueError("Permission IDs must be unique.")

        return permission_ids


class RoleUpdate(SchemaBase):
    display_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    is_active: bool | None = None


class UserRoleUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    role_ids: list[UUID] = Field(
        default_factory=list,
    )

    @field_validator("role_ids")
    @classmethod
    def validate_role_ids(
        cls,
        role_ids: list[UUID],
    ) -> list[UUID]:
        if len(role_ids) != len(set(role_ids)):
            raise ValueError("Role IDs must be unique.")

        return role_ids


class RolePermissionUpdate(SchemaBase):
    permission_ids: list[UUID] = Field(
        default_factory=list,
    )

    @field_validator("permission_ids")
    @classmethod
    def validate_permission_ids(
        cls,
        permission_ids: list[UUID],
    ) -> list[UUID]:
        if len(permission_ids) != len(set(permission_ids)):
            raise ValueError("Permission IDs must be unique.")

        return permission_ids


class RoleRead(RoleBase, DatabaseSchema):
    permissions: list[PermissionRead] = Field(
        default_factory=list,
    )
