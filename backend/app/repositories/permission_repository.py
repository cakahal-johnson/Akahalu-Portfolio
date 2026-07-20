from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.repositories.base import BaseRepository


class PermissionRepository(
    BaseRepository[Permission],
):
    def __init__(self) -> None:
        super().__init__(Permission)

    async def get_by_code(
        self,
        session: AsyncSession,
        code: str,
    ) -> Permission | None:
        statement = select(Permission).where(
            Permission.code == code,
            Permission.deleted_at.is_(None),
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def list_all(
        self,
        session: AsyncSession,
    ) -> Sequence[Permission]:
        statement = (
            select(Permission)
            .where(
                Permission.deleted_at.is_(None),
            )
            .order_by(
                Permission.code.asc(),
            )
        )

        result = await session.execute(statement)

        return result.scalars().all()

    async def list_active_by_ids(
        self,
        session: AsyncSession,
        permission_ids: Sequence[UUID],
    ) -> Sequence[Permission]:
        if not permission_ids:
            return []

        statement = (
            select(Permission)
            .where(
                Permission.id.in_(permission_ids),
                Permission.deleted_at.is_(None),
                Permission.is_active.is_(True),
            )
            .order_by(
                Permission.code.asc(),
            )
        )

        result = await session.execute(statement)

        return result.scalars().all()


permission_repository = PermissionRepository()
