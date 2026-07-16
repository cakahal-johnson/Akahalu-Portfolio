from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, ReprMixin
from app.models.associations import (
    role_permissions,
    user_roles,
)


if TYPE_CHECKING:
    from app.models.permission import Permission
    from app.models.user import User


class Role(BaseModel, ReprMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    users: Mapped[list["User"]] = relationship(
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin",
    )

    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )
