from uuid import UUID

from pydantic import Field

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


class RoleCreate(RoleBase):
    permission_ids: list[UUID] = Field(
        default_factory=list,
    )


class RoleRead(RoleBase, DatabaseSchema):
    permissions: list[PermissionRead] = Field(
        default_factory=list,
    )
