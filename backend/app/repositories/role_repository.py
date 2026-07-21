from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(
    BaseRepository[Role],
):
    def __init__(self) -> None:
        super().__init__(Role)

    async def get_by_id_with_permissions(
        self,
        session: AsyncSession,
        role_id: UUID,
    ) -> Role | None:
        statement = (
            select(Role)
            .options(
                selectinload(Role.permissions),
            )
            .where(
                Role.id == role_id,
                Role.deleted_at.is_(None),
            )
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        session: AsyncSession,
        name: str,
    ) -> Role | None:
        statement = (
            select(Role)
            .options(
                selectinload(Role.permissions),
            )
            .where(
                Role.name == name,
                Role.deleted_at.is_(None),
            )
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def list_active_by_ids(
        self,
        session: AsyncSession,
        role_ids: Sequence[UUID],
    ) -> Sequence[Role]:
        if not role_ids:
            return []

        statement = (
            select(Role)
            .options(
                selectinload(Role.permissions),
            )
            .where(
                Role.id.in_(role_ids),
                Role.is_active.is_(True),
                Role.deleted_at.is_(None),
            )
            .order_by(
                Role.display_name.asc(),
                Role.name.asc(),
            )
        )

        result = await session.execute(statement)

        return result.scalars().unique().all()

    async def list_all(
        self,
        session: AsyncSession,
    ) -> Sequence[Role]:
        statement = (
            select(Role)
            .options(
                selectinload(Role.permissions),
            )
            .where(
                Role.deleted_at.is_(None),
            )
            .order_by(
                Role.display_name.asc(),
                Role.name.asc(),
            )
        )

        result = await session.execute(statement)

        return result.scalars().unique().all()


role_repository = RoleRepository()
