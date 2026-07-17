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


permission_repository = PermissionRepository()
