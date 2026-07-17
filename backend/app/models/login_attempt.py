from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, ReprMixin


class LoginAttempt(BaseModel, ReprMixin):
    __tablename__ = "login_attempts"

    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        index=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        index=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    was_successful: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    user = relationship(
        "User",
        back_populates="login_attempts",
        lazy="joined",
    )
