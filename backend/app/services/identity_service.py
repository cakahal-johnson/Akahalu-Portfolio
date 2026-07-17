from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.repositories.permission_repository import (
    permission_repository,
)
from app.repositories.role_repository import role_repository
from app.repositories.user_repository import user_repository
from app.security.passwords import hash_password


class IdentityService:
    async def ensure_permission(
        self,
        session: AsyncSession,
        *,
        code: str,
        name: str,
        description: str,
    ) -> Permission:
        existing_permission = await permission_repository.get_by_code(
            session,
            code,
        )

        if existing_permission is not None:
            existing_permission.name = name
            existing_permission.description = description
            existing_permission.is_active = True

            return existing_permission

        permission = Permission(
            code=code,
            name=name,
            description=description,
            is_active=True,
        )

        session.add(permission)
        await session.flush()

        return permission

    async def ensure_role(
        self,
        session: AsyncSession,
        *,
        name: str,
        display_name: str,
        description: str,
        is_system: bool,
        permissions: list[Permission],
    ) -> Role:
        existing_role = await role_repository.get_by_name(
            session,
            name,
        )

        if existing_role is not None:
            existing_role.display_name = display_name
            existing_role.description = description
            existing_role.is_system = is_system
            existing_role.is_active = True
            existing_role.permissions = permissions

            return existing_role

        role = Role(
            name=name,
            display_name=display_name,
            description=description,
            is_system=is_system,
            is_active=True,
            permissions=permissions,
        )

        session.add(role)
        await session.flush()

        return role

    async def ensure_super_admin(
        self,
        session: AsyncSession,
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        super_admin_role: Role,
    ) -> tuple[User, bool]:
        existing_user = await user_repository.get_by_email(
            session,
            email,
        )

        if existing_user is not None:
            if super_admin_role not in existing_user.roles:
                existing_user.roles.append(
                    super_admin_role,
                )

            existing_user.is_active = True
            existing_user.is_verified = True
            existing_user.is_superuser = True

            return existing_user, False

        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            display_name=f"{first_name} {last_name}".strip(),
            is_active=True,
            is_verified=True,
            is_superuser=True,
            roles=[super_admin_role],
        )

        session.add(user)
        await session.flush()

        return user, True


identity_service = IdentityService()
