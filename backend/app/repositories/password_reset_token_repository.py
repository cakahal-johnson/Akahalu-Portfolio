from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    def __init__(
        self,
        database_session: AsyncSession,
    ) -> None:
        self.database_session = database_session

    async def create(
        self,
        *,
        user_id: UUID,
        token_digest: str,
        expires_at: datetime,
    ) -> PasswordResetToken:
        token = PasswordResetToken(
            user_id=user_id,
            token_digest=token_digest,
            expires_at=expires_at,
        )

        self.database_session.add(token)
        await self.database_session.flush()

        return token

    async def get_by_digest(
        self,
        token_digest: str,
    ) -> PasswordResetToken | None:
        statement = (
            select(PasswordResetToken)
            .options(
                joinedload(PasswordResetToken.user),
            )
            .where(
                PasswordResetToken.token_digest == token_digest,
                PasswordResetToken.deleted_at.is_(None),
            )
        )

        result = await self.database_session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_digest_for_update(
        self,
        token_digest: str,
    ) -> PasswordResetToken | None:
        statement = (
            select(PasswordResetToken)
            .where(
                PasswordResetToken.token_digest == token_digest,
                PasswordResetToken.deleted_at.is_(None),
            )
            .with_for_update(
                of=PasswordResetToken,
            )
        )

        result = await self.database_session.execute(statement)

        return result.scalar_one_or_none()

    async def revoke_active_for_user(
        self,
        *,
        user_id: UUID,
        revoked_at: datetime,
    ) -> int:
        statement = (
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.consumed_at.is_(None),
                PasswordResetToken.revoked_at.is_(None),
                PasswordResetToken.deleted_at.is_(None),
            )
            .values(
                revoked_at=revoked_at,
            )
            .returning(PasswordResetToken.id)
        )

        result = await self.database_session.execute(statement)
        revoked_token_ids = result.scalars().all()

        return len(revoked_token_ids)

    async def consume(
        self,
        token: PasswordResetToken,
        *,
        consumed_at: datetime,
    ) -> PasswordResetToken:
        token.consumed_at = consumed_at

        await self.database_session.flush()

        return token

    async def revoke(
        self,
        token: PasswordResetToken,
        *,
        revoked_at: datetime,
    ) -> PasswordResetToken:
        token.revoked_at = revoked_at

        await self.database_session.flush()

        return token
