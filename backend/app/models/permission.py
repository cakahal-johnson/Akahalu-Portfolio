from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, ReprMixin
from app.models.associations import role_permissions


if TYPE_CHECKING:
    from app.models.role import Role


class Permission(BaseModel, ReprMixin):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permissions,
        back_populates="permissions",
        lazy="selectin",
    )
