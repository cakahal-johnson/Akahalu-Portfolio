from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, ReprMixin


if TYPE_CHECKING:
    from app.models.user import User


class PasswordResetToken(BaseModel, ReprMixin):
    __tablename__ = "password_reset_tokens"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    token_digest: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    user: Mapped["User"] = relationship(
        back_populates="password_reset_tokens",
        lazy="joined",
    )

    __table_args__ = (
        CheckConstraint(
            "expires_at > created_at",
            name="ck_password_reset_tokens_expiry",
        ),
        Index(
            "ix_password_reset_tokens_user_id",
            "user_id",
        ),
        Index(
            "ix_password_reset_tokens_expires_at",
            "expires_at",
        ),
    )

    @property
    def is_consumed(self) -> bool:
        return self.consumed_at is not None

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def is_expired(self) -> bool:
        return self.expires_at <= datetime.now(timezone.utc)

    @property
    def is_usable(self) -> bool:
        return not self.is_consumed and not self.is_revoked and not self.is_expired
