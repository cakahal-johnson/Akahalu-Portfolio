from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role
from app.repositories.permission_repository import (
    permission_repository,
)
from app.repositories.role_repository import role_repository
from app.schemas.role import (
    RoleCreate,
    RolePermissionUpdate,
    RoleUpdate,
)


class RbacError(Exception):
    status_code: int = 400
    error_code: str = "rbac_operation_failed"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class RoleNotFoundError(RbacError):
    status_code = 404
    error_code = "role_not_found"


class RoleAlreadyExistsError(RbacError):
    status_code = 409
    error_code = "role_already_exists"


class InvalidPermissionsError(RbacError):
    status_code = 422
    error_code = "invalid_permissions"


class ProtectedSystemRoleError(RbacError):
    status_code = 409
    error_code = "protected_system_role"


class RbacService:
    async def list_roles(
        self,
        session: AsyncSession,
    ) -> Sequence[Role]:
        roles = await role_repository.list_all(
            session,
        )

        for role in roles:
            role.permissions.sort(
                key=lambda permission: permission.code,
            )

        return roles

    async def list_permissions(
        self,
        session: AsyncSession,
    ) -> Sequence[Permission]:
        return await permission_repository.list_all(
            session,
        )

    async def create_role(
        self,
        session: AsyncSession,
        *,
        payload: RoleCreate,
    ) -> Role:
        normalized_name = payload.name.strip().lower()

        existing_role = await role_repository.get_by_name(
            session,
            normalized_name,
        )

        if existing_role is not None:
            raise RoleAlreadyExistsError("A role with this name already exists.")

        permissions = await self._resolve_permissions(
            session,
            payload.permission_ids,
        )

        role = Role(
            name=normalized_name,
            display_name=payload.display_name,
            description=payload.description,
            is_system=False,
            is_active=payload.is_active,
            permissions=list(permissions),
        )

        session.add(role)

        try:
            await session.flush()
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()

            raise RoleAlreadyExistsError(
                "A role with this name already exists."
            ) from exc
        except Exception:
            await session.rollback()
            raise

        created_role = await role_repository.get_by_id_with_permissions(
            session,
            role.id,
        )

        if created_role is None:
            raise RoleNotFoundError("The created role could not be retrieved.")

        created_role.permissions.sort(
            key=lambda permission: permission.code,
        )

        return created_role

    async def update_role(
        self,
        session: AsyncSession,
        *,
        role_id: UUID,
        payload: RoleUpdate,
    ) -> Role:
        role = await self._get_role(
            session,
            role_id,
        )

        changes = payload.model_dump(
            exclude_unset=True,
        )

        if role.name == "super_admin" and changes.get("is_active") is False:
            raise ProtectedSystemRoleError(
                "The super administrator role cannot be deactivated."
            )

        for field_name, value in changes.items():
            setattr(
                role,
                field_name,
                value,
            )

        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        updated_role = await role_repository.get_by_id_with_permissions(
            session,
            role.id,
        )

        if updated_role is None:
            raise RoleNotFoundError("The updated role could not be retrieved.")

        updated_role.permissions.sort(
            key=lambda permission: permission.code,
        )

        return updated_role

    async def replace_role_permissions(
        self,
        session: AsyncSession,
        *,
        role_id: UUID,
        payload: RolePermissionUpdate,
    ) -> Role:
        role = await self._get_role(
            session,
            role_id,
        )

        if role.name == "super_admin":
            raise ProtectedSystemRoleError(
                "Permissions for the super administrator role cannot be replaced."
            )

        permissions = await self._resolve_permissions(
            session,
            payload.permission_ids,
        )

        role.permissions = list(permissions)

        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        updated_role = await role_repository.get_by_id_with_permissions(
            session,
            role.id,
        )

        if updated_role is None:
            raise RoleNotFoundError("The updated role could not be retrieved.")

        updated_role.permissions.sort(
            key=lambda permission: permission.code,
        )

        return updated_role

    async def _get_role(
        self,
        session: AsyncSession,
        role_id: UUID,
    ) -> Role:
        role = await role_repository.get_by_id_with_permissions(
            session,
            role_id,
        )

        if role is None:
            raise RoleNotFoundError("The requested role was not found.")

        return role

    async def _resolve_permissions(
        self,
        session: AsyncSession,
        permission_ids: Sequence[UUID],
    ) -> Sequence[Permission]:
        if not permission_ids:
            return []

        permissions = await permission_repository.list_active_by_ids(
            session,
            permission_ids,
        )

        requested_ids = set(permission_ids)
        resolved_ids = {permission.id for permission in permissions}

        if resolved_ids != requested_ids:
            raise InvalidPermissionsError(
                "One or more permissions do not exist or are inactive."
            )

        return permissions


rbac_service = RbacService()
