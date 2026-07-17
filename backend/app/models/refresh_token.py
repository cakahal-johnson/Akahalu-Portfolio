from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, ReprMixin


if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.user import User


class RefreshToken(BaseModel, ReprMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    token_digest: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    family_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    replaced_by_token_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "refresh_tokens.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="refresh_tokens",
        lazy="joined",
    )

    session: Mapped["Session"] = relationship(
        back_populates="refresh_tokens",
        lazy="joined",
    )

    replacement_token: Mapped["RefreshToken | None"] = relationship(
        remote_side="RefreshToken.id",
        foreign_keys=[replaced_by_token_id],
        lazy="joined",
    )

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None
