from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID
from app.models.user import User

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role
from app.repositories.permission_repository import (
    permission_repository,
)
from app.repositories.refresh_token_repository import (
    refresh_token_repository,
)
from app.repositories.role_repository import role_repository
from app.repositories.session_repository import (
    session_repository,
)
from app.repositories.user_repository import user_repository
from app.schemas.role import (
    RoleCreate,
    RolePermissionUpdate,
    RoleUpdate,
    UserRoleUpdate,
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


class UserNotFoundError(RbacError):
    status_code = 404
    error_code = "user_not_found"


class InvalidRolesError(RbacError):
    status_code = 422
    error_code = "invalid_roles"


class LastAdministratorError(RbacError):
    status_code = 409
    error_code = "last_administrator"


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

    async def list_user_roles(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
    ) -> Sequence[Role]:
        user = await self._get_user(
            session,
            user_id,
        )

        return self._sort_roles(
            user.roles,
        )

    async def replace_user_roles(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
        payload: UserRoleUpdate,
    ) -> Sequence[Role]:
        user = await self._get_user(
            session,
            user_id,
        )

        roles = await self._resolve_roles(
            session,
            payload.role_ids,
        )

        current_role_ids = {role.id for role in user.roles if role.deleted_at is None}

        requested_role_ids = {role.id for role in roles}

        if current_role_ids == requested_role_ids:
            return self._sort_roles(
                user.roles,
            )

        current_role_names = {
            role.name.strip().lower()
            for role in user.roles
            if (role.is_active and role.deleted_at is None and role.name.strip())
        }

        requested_role_names = {
            role.name.strip().lower() for role in roles if role.name.strip()
        }

        removes_super_admin = (
            "super_admin" in current_role_names
            and "super_admin" not in requested_role_names
        )

        if removes_super_admin and not user.is_superuser:
            has_other_administrator = (
                await user_repository.has_other_active_administrator(
                    session,
                    excluded_user_id=user.id,
                )
            )

            if not has_other_administrator:
                raise LastAdministratorError(
                    "The last active administrator cannot lose administrative access."
                )

        user.roles = list(roles)

        now = datetime.now(UTC)

        try:
            await refresh_token_repository.revoke_all_for_user(
                session,
                user.id,
                revoked_at=now,
            )

            await session_repository.revoke_all_for_user(
                session,
                user.id,
                reason="roles_changed",
                revoked_at=now,
            )

            await session.commit()
        except Exception:
            await session.rollback()
            raise

        updated_user = await user_repository.get_by_id_with_roles(
            session,
            user.id,
        )

        if updated_user is None:
            raise UserNotFoundError("The updated user could not be retrieved.")

        return self._sort_roles(
            updated_user.roles,
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

    async def _get_user(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User:
        user = await user_repository.get_by_id_with_roles(
            session,
            user_id,
        )

        if user is None:
            raise UserNotFoundError("The requested user was not found.")

        return user

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

    async def _resolve_roles(
        self,
        session: AsyncSession,
        role_ids: Sequence[UUID],
    ) -> Sequence[Role]:
        if not role_ids:
            return []

        roles = await role_repository.list_active_by_ids(
            session,
            role_ids,
        )

        requested_ids = set(role_ids)
        resolved_ids = {role.id for role in roles}

        if requested_ids != resolved_ids:
            raise InvalidRolesError("One or more roles do not exist or are inactive.")

        return roles

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

    @staticmethod
    def _sort_roles(
        roles: Sequence[Role],
    ) -> list[Role]:
        visible_roles = [role for role in roles if role.deleted_at is None]

        for role in visible_roles:
            role.permissions.sort(
                key=lambda permission: permission.code,
            )

        return sorted(
            visible_roles,
            key=lambda role: (
                role.display_name,
                role.name,
            ),
        )


rbac_service = RbacService()
