from pydantic import Field

from app.schemas.base import DatabaseSchema, SchemaBase


class PermissionBase(SchemaBase):
    code: str = Field(
        min_length=3,
        max_length=100,
        examples=["projects.create"],
    )

    name: str = Field(
        min_length=2,
        max_length=150,
        examples=["Create projects"],
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    is_active: bool = True


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(PermissionBase, DatabaseSchema):
    pass
