from collections.abc import Sequence
from datetime import UTC, datetime
from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.user import User
from app.repositories.refresh_token_repository import (
    refresh_token_repository,
)
from app.repositories.session_repository import (
    session_repository,
)
from app.repositories.user_repository import user_repository
from app.schemas.role import RoleRead
from app.schemas.user_admin import (
    AdminUserDeleteRequest,
    AdminUserDetail,
    AdminUserListQuery,
    AdminUserListResponse,
    AdminUserProfileUpdate,
    AdminUserRestoreRequest,
    AdminUserStatusUpdate,
    AdminUserSummary,
    UserStatus,
)


class UserAdminError(Exception):
    status_code: int = 400
    error_code: str = "user_admin_operation_failed"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class AdminUserNotFoundError(UserAdminError):
    status_code = 404
    error_code = "user_not_found"


class AdminUserAlreadyDeletedError(UserAdminError):
    status_code = 409
    error_code = "user_already_deleted"


class AdminUserNotDeletedError(UserAdminError):
    status_code = 409
    error_code = "user_not_deleted"


class AdminUserDeletedError(UserAdminError):
    status_code = 409
    error_code = "user_deleted"


class SelfAccountModificationError(UserAdminError):
    status_code = 409
    error_code = "self_account_modification_forbidden"


class LastAdministratorError(UserAdminError):
    status_code = 409
    error_code = "last_administrator"


class UserAdminService:
    async def list_users(
        self,
        session: AsyncSession,
        *,
        query: AdminUserListQuery,
    ) -> AdminUserListResponse:
        is_active = None

        if query.status is UserStatus.ACTIVE:
            is_active = True
        elif query.status is UserStatus.INACTIVE:
            is_active = False

        offset = (query.page - 1) * query.page_size

        users, total_items = await user_repository.list_for_admin(
            session,
            offset=offset,
            limit=query.page_size,
            search=query.search,
            is_active=is_active,
            is_verified=query.is_verified,
            is_superuser=query.is_superuser,
            include_deleted=query.include_deleted,
            sort_by=query.sort_by.value,
            sort_direction=query.sort_direction.value,
        )

        total_pages = ceil(total_items / query.page_size) if total_items else 0

        return AdminUserListResponse(
            items=[self._to_summary(user) for user in users],
            page=query.page,
            page_size=query.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next_page=query.page < total_pages,
            has_previous_page=query.page > 1,
        )

    async def get_user(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
        include_deleted: bool = False,
    ) -> AdminUserDetail:
        user = await self._get_user(
            session,
            user_id=user_id,
            include_deleted=include_deleted,
        )

        return self._to_detail(user)

    async def update_profile(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
        payload: AdminUserProfileUpdate,
    ) -> AdminUserDetail:
        user = await self._get_user(
            session,
            user_id=user_id,
        )

        changes = payload.model_dump(exclude_unset=True)

        for field_name, value in changes.items():
            setattr(user, field_name, value)

        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        updated_user = await self._get_user(
            session,
            user_id=user.id,
        )

        return self._to_detail(updated_user)

    async def update_status(
        self,
        session: AsyncSession,
        *,
        actor_user_id: UUID,
        user_id: UUID,
        payload: AdminUserStatusUpdate,
    ) -> AdminUserDetail:
        user = await self._get_user(
            session,
            user_id=user_id,
            include_deleted=True,
        )

        if user.deleted_at is not None:
            raise AdminUserDeletedError(
                "A deleted account must be restored before its status can be changed."
            )

        if user.is_active == payload.is_active:
            return self._to_detail(user)

        if actor_user_id == user.id and not payload.is_active:
            raise SelfAccountModificationError(
                "You cannot deactivate your own account."
            )

        if not payload.is_active:
            await self._ensure_not_last_administrator(
                session,
                user=user,
            )

        user.is_active = payload.is_active

        try:
            if not payload.is_active:
                await self._revoke_user_access(
                    session,
                    user_id=user.id,
                    reason="account_deactivated",
                )

            await session.commit()
        except Exception:
            await session.rollback()
            raise

        updated_user = await self._get_user(
            session,
            user_id=user.id,
        )

        return self._to_detail(updated_user)

    async def delete_user(
        self,
        session: AsyncSession,
        *,
        actor_user_id: UUID,
        user_id: UUID,
        payload: AdminUserDeleteRequest,
    ) -> AdminUserDetail:
        user = await self._get_user(
            session,
            user_id=user_id,
            include_deleted=True,
        )

        if user.deleted_at is not None:
            raise AdminUserAlreadyDeletedError(
                "The requested user account is already deleted."
            )

        if actor_user_id == user.id:
            raise SelfAccountModificationError("You cannot delete your own account.")

        await self._ensure_not_last_administrator(
            session,
            user=user,
        )

        now = datetime.now(UTC)

        user.is_active = False
        user.deleted_at = now

        try:
            await self._revoke_user_access(
                session,
                user_id=user.id,
                reason="account_deleted",
                revoked_at=now,
            )

            await session.commit()
        except Exception:
            await session.rollback()
            raise

        deleted_user = await self._get_user(
            session,
            user_id=user.id,
            include_deleted=True,
        )

        return self._to_detail(deleted_user)

    async def restore_user(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
        payload: AdminUserRestoreRequest,
    ) -> AdminUserDetail:
        user = await self._get_user(
            session,
            user_id=user_id,
            include_deleted=True,
        )

        if user.deleted_at is None:
            raise AdminUserNotDeletedError("The requested user account is not deleted.")

        user.deleted_at = None
        user.is_active = payload.activate

        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        restored_user = await self._get_user(
            session,
            user_id=user.id,
        )

        return self._to_detail(restored_user)

    async def _get_user(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
        include_deleted: bool = False,
    ) -> User:
        user = await user_repository.get_by_id_with_roles(
            session,
            user_id,
            include_deleted=include_deleted,
        )

        if user is None:
            raise AdminUserNotFoundError("The requested user was not found.")

        return user

    async def _ensure_not_last_administrator(
        self,
        session: AsyncSession,
        *,
        user: User,
    ) -> None:
        if not self._is_active_administrator(user):
            return

        has_other_administrator = await user_repository.has_other_active_administrator(
            session,
            excluded_user_id=user.id,
        )

        if not has_other_administrator:
            raise LastAdministratorError(
                "The last active administrator cannot be deactivated or deleted."
            )

    async def _revoke_user_access(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
        reason: str,
        revoked_at: datetime | None = None,
    ) -> None:
        effective_time = revoked_at or datetime.now(UTC)

        await refresh_token_repository.revoke_all_for_user(
            session,
            user_id,
            revoked_at=effective_time,
        )

        await session_repository.revoke_all_for_user(
            session,
            user_id,
            reason=reason,
            revoked_at=effective_time,
        )

    @staticmethod
    def _is_active_administrator(
        user: User,
    ) -> bool:
        if not user.is_active or user.deleted_at is not None:
            return False

        if user.is_superuser:
            return True

        return any(
            role.name.strip().lower() == "super_admin"
            and role.is_active
            and role.deleted_at is None
            for role in user.roles
        )

    @classmethod
    def _to_summary(
        cls,
        user: User,
    ) -> AdminUserSummary:
        return AdminUserSummary(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            is_deleted=user.deleted_at is not None,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
            roles=cls._serialize_roles(user.roles),
        )

    @classmethod
    def _to_detail(
        cls,
        user: User,
    ) -> AdminUserDetail:
        return AdminUserDetail(
            **cls._to_summary(user).model_dump(),
            last_login_at=user.last_login_at,
        )

    @staticmethod
    def _serialize_roles(
        roles: Sequence[Role],
    ) -> list[RoleRead]:
        visible_roles = [role for role in roles if role.deleted_at is None]

        for role in visible_roles:
            role.permissions.sort(
                key=lambda permission: permission.code,
            )

        sorted_roles = sorted(
            visible_roles,
            key=lambda role: (
                role.display_name,
                role.name,
            ),
        )

        return [RoleRead.model_validate(role) for role in sorted_roles]


user_admin_service = UserAdminService()
