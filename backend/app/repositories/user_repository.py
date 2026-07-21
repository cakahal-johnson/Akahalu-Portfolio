from uuid import UUID

from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.associations import user_roles
from app.models.role import Role
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(
    BaseRepository[User],
):
    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:
        statement = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(
                    Role.permissions,
                ),
            )
            .where(
                User.email == email,
                User.deleted_at.is_(None),
            )
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_id_with_roles(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User | None:
        statement = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(
                    Role.permissions,
                ),
            )
            .where(
                User.id == user_id,
                User.deleted_at.is_(None),
            )
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def has_other_active_administrator(
        self,
        session: AsyncSession,
        *,
        excluded_user_id: UUID,
    ) -> bool:
        super_admin_assignment_exists = exists(
            select(1)
            .select_from(user_roles)
            .join(
                Role,
                Role.id == user_roles.c.role_id,
            )
            .where(
                user_roles.c.user_id == User.id,
                Role.name == "super_admin",
                Role.is_active.is_(True),
                Role.deleted_at.is_(None),
            )
        )

        statement = select(
            exists().where(
                User.id != excluded_user_id,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
                or_(
                    User.is_superuser.is_(True),
                    super_admin_assignment_exists,
                ),
            )
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())


user_repository = UserRepository()
