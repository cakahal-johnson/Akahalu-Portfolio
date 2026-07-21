from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Select, asc, desc, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement

from app.models.associations import user_roles
from app.models.role import Role
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(
    BaseRepository[User],
):
    def __init__(self) -> None:
        super().__init__(User)

    @staticmethod
    def _with_roles(
        statement: Select[tuple[User]],
    ) -> Select[tuple[User]]:
        return statement.options(
            selectinload(User.roles).selectinload(
                Role.permissions,
            ),
        )

    async def get_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:
        statement = self._with_roles(
            select(User).where(
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
        *,
        include_deleted: bool = False,
    ) -> User | None:
        statement = select(User).where(
            User.id == user_id,
        )

        if not include_deleted:
            statement = statement.where(
                User.deleted_at.is_(None),
            )

        result = await session.execute(
            self._with_roles(statement),
        )

        return result.scalar_one_or_none()

    async def list_for_admin(
        self,
        session: AsyncSession,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
        is_superuser: bool | None = None,
        include_deleted: bool = False,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> tuple[Sequence[User], int]:
        filters: list[ColumnElement[bool]] = []

        if not include_deleted:
            filters.append(
                User.deleted_at.is_(None),
            )

        normalized_search = search.strip() if search else None

        if normalized_search:
            search_pattern = f"%{normalized_search}%"

            filters.append(
                or_(
                    User.email.ilike(search_pattern),
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.display_name.ilike(search_pattern),
                )
            )

        if is_active is not None:
            filters.append(
                User.is_active.is_(is_active),
            )

        if is_verified is not None:
            filters.append(
                User.is_verified.is_(is_verified),
            )

        if is_superuser is not None:
            filters.append(
                User.is_superuser.is_(is_superuser),
            )

        sort_columns = {
            "created_at": User.created_at,
            "email": User.email,
            "first_name": User.first_name,
            "last_name": User.last_name,
            "display_name": User.display_name,
        }

        sort_column = sort_columns.get(
            sort_by,
            User.created_at,
        )

        sort_expression = (
            asc(sort_column) if sort_direction.lower() == "asc" else desc(sort_column)
        )

        count_statement = select(
            func.count(User.id),
        ).where(*filters)

        total_result = await session.execute(
            count_statement,
        )

        total = int(
            total_result.scalar_one(),
        )

        statement = (
            select(User)
            .where(*filters)
            .order_by(
                sort_expression,
                User.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(
            self._with_roles(statement),
        )

        return result.scalars().unique().all(), total

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
