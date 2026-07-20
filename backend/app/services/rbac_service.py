from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role
from app.repositories.permission_repository import (
    permission_repository,
)
from app.repositories.role_repository import role_repository


class RbacService:
    async def list_roles(
        self,
        session: AsyncSession,
    ) -> Sequence[Role]:
        return await role_repository.list_all(
            session,
        )

    async def list_permissions(
        self,
        session: AsyncSession,
    ) -> Sequence[Permission]:
        return await permission_repository.list_all(
            session,
        )


rbac_service = RbacService()
