from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from sqlalchemy.orm import selectinload

from app.models.email_verification_token import (
    EmailVerificationToken,
)


class EmailVerificationTokenRepository:
    def __init__(self, database_session: AsyncSession) -> None:
        self.database_session = database_session

    async def create(
        self,
        *,
        user_id: UUID,
        token_digest: str,
        expires_at: datetime,
    ) -> EmailVerificationToken:
        token = EmailVerificationToken(
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
    ) -> EmailVerificationToken | None:
        statement = (
            select(EmailVerificationToken)
            .options(
                joinedload(EmailVerificationToken.user),
            )
            .where(
                EmailVerificationToken.token_digest == token_digest,
                EmailVerificationToken.deleted_at.is_(None),
            )
        )

        result = await self.database_session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_digest_for_update(
        self,
        token_digest: str,
    ) -> EmailVerificationToken | None:
        statement = (
            select(EmailVerificationToken)
            .options(
                selectinload(EmailVerificationToken.user),
            )
            .where(
                EmailVerificationToken.token_digest == token_digest,
                EmailVerificationToken.deleted_at.is_(None),
            )
            .with_for_update(
                of=EmailVerificationToken,
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
            update(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.consumed_at.is_(None),
                EmailVerificationToken.revoked_at.is_(None),
                EmailVerificationToken.deleted_at.is_(None),
            )
            .values(
                revoked_at=revoked_at,
            )
            .returning(EmailVerificationToken.id)
        )

        result = await self.database_session.execute(statement)
        revoked_token_ids = result.scalars().all()

        return len(revoked_token_ids)

    async def consume(
        self,
        token: EmailVerificationToken,
        *,
        consumed_at: datetime,
    ) -> EmailVerificationToken:
        token.consumed_at = consumed_at

        await self.database_session.flush()

        return token

    async def revoke(
        self,
        token: EmailVerificationToken,
        *,
        revoked_at: datetime,
    ) -> EmailVerificationToken:
        token.revoked_at = revoked_at

        await self.database_session.flush()

        return token
