from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import raiseload, selectinload

from app.models.role import Role
from app.models.session import Session
from app.models.user import User
from app.repositories.base import BaseRepository


class SessionRepository(
    BaseRepository[Session],
):
    def __init__(self) -> None:
        super().__init__(
            Session,
        )

    async def get_active_by_id(
        self,
        session: AsyncSession,
        session_id: UUID,
    ) -> Session | None:
        """
        Return an active authentication session with only the
        authorization graph required by get_current_user.

        Authentication needs:

        Session
            -> User
                -> Roles
                    -> Permissions

        All unrelated relationships are intentionally blocked to avoid
        loading refresh-token history, other sessions, verification
        tokens, password-reset tokens, login attempts, role users, and
        permission back-references on every protected request.
        """

        now = datetime.now(UTC)

        statement = (
            select(
                Session,
            )
            .options(
                raiseload("*"),
                selectinload(
                    Session.user,
                ).options(
                    raiseload("*"),
                    selectinload(
                        User.roles,
                    ).options(
                        raiseload("*"),
                        selectinload(
                            Role.permissions,
                        ).options(
                            raiseload("*"),
                        ),
                    ),
                ),
            )
            .where(
                Session.id == session_id,
                Session.is_active.is_(True),
                Session.revoked_at.is_(None),
                Session.expires_at > now,
                Session.deleted_at.is_(None),
            )
        )

        result = await session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def revoke(
        self,
        session: AsyncSession,
        authentication_session: Session,
        *,
        reason: str,
        revoked_at: datetime | None = None,
    ) -> Session:
        effective_time = revoked_at or datetime.now(UTC)

        authentication_session.is_active = False
        authentication_session.revoked_at = effective_time
        authentication_session.revocation_reason = reason

        await session.flush()

        return authentication_session

    async def revoke_all_for_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        *,
        reason: str,
        exclude_session_id: UUID | None = None,
        revoked_at: datetime | None = None,
    ) -> int:
        effective_time = revoked_at or datetime.now(UTC)

        conditions = [
            Session.user_id == user_id,
            Session.is_active.is_(True),
            Session.revoked_at.is_(None),
            Session.deleted_at.is_(None),
        ]

        if exclude_session_id is not None:
            conditions.append(
                Session.id != exclude_session_id,
            )

        statement = (
            update(
                Session,
            )
            .where(
                *conditions,
            )
            .values(
                is_active=False,
                revoked_at=effective_time,
                revocation_reason=reason,
            )
        )

        result = await session.execute(
            statement.returning(
                Session.id,
            )
        )

        return len(result.scalars().all())


session_repository = SessionRepository()
