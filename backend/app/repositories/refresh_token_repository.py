from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.refresh_token import RefreshToken
from app.models.role import Role
from app.models.user import User
from app.repositories.base import BaseRepository


class RefreshTokenRepository(
    BaseRepository[RefreshToken],
):
    def __init__(self) -> None:
        super().__init__(RefreshToken)

    async def get_by_digest(
        self,
        session: AsyncSession,
        token_digest: str,
    ) -> RefreshToken | None:
        statement = (
            select(RefreshToken)
            .options(
                selectinload(RefreshToken.session),
                selectinload(RefreshToken.user)
                .selectinload(User.roles)
                .selectinload(Role.permissions),
            )
            .where(
                RefreshToken.token_digest == token_digest,
                RefreshToken.deleted_at.is_(None),
            )
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def revoke_family(
        self,
        session: AsyncSession,
        family_id: UUID,
        *,
        revoked_at: datetime | None = None,
    ) -> int:
        effective_time = revoked_at or datetime.now(UTC)

        statement = (
            update(RefreshToken)
            .where(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.deleted_at.is_(None),
            )
            .values(
                revoked_at=effective_time,
            )
            .returning(RefreshToken.id)
        )

        result = await session.execute(statement)

        return len(result.scalars().all())

    async def revoke_for_session(
        self,
        session: AsyncSession,
        session_id: UUID,
        *,
        revoked_at: datetime | None = None,
    ) -> int:
        effective_time = revoked_at or datetime.now(UTC)

        statement = (
            update(RefreshToken)
            .where(
                RefreshToken.session_id == session_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.deleted_at.is_(None),
            )
            .values(
                revoked_at=effective_time,
            )
            .returning(RefreshToken.id)
        )

        result = await session.execute(statement)

        return len(result.scalars().all())

    async def revoke_all_for_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        *,
        revoked_at: datetime | None = None,
    ) -> int:
        effective_time = revoked_at or datetime.now(UTC)

        statement = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.deleted_at.is_(None),
            )
            .values(
                revoked_at=effective_time,
            )
            .returning(RefreshToken.id)
        )

        result = await session.execute(statement)

        return len(result.scalars().all())


refresh_token_repository = RefreshTokenRepository()
