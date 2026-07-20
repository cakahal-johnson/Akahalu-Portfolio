from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.api.dependencies.authentication import get_current_user
from app.models.user import User


AuthorizationDependency = Callable[[User], Awaitable[User]]


def authorization_exception(
    *,
    code: str = "insufficient_permissions",
    message: str = "You do not have permission to perform this action.",
) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": code,
            "message": message,
        },
    )


def normalize_authorization_values(
    values: tuple[str, ...],
    *,
    value_name: str,
) -> frozenset[str]:
    normalized_values = frozenset(
        value.strip().lower() for value in values if value.strip()
    )

    if not normalized_values:
        raise ValueError(
            f"At least one {value_name} must be provided.",
        )

    return normalized_values


def get_active_role_names(
    user: User,
) -> frozenset[str]:
    return frozenset(
        role.name.strip().lower()
        for role in user.roles
        if (role.is_active and role.deleted_at is None and role.name.strip())
    )


def get_active_permission_codes(
    user: User,
) -> frozenset[str]:
    permission_codes: set[str] = set()

    for role in user.roles:
        if not role.is_active or role.deleted_at is not None:
            continue

        for permission in role.permissions:
            if not permission.is_active or permission.deleted_at is not None:
                continue

            normalized_code = permission.code.strip().lower()

            if normalized_code:
                permission_codes.add(normalized_code)

    return frozenset(permission_codes)


def user_has_role(
    user: User,
    role_name: str,
) -> bool:
    normalized_role_name = role_name.strip().lower()

    if not normalized_role_name:
        return False

    if user.is_superuser:
        return True

    return normalized_role_name in get_active_role_names(user)


def user_has_any_role(
    user: User,
    role_names: frozenset[str],
) -> bool:
    normalized_role_names = frozenset(
        role_name.strip().lower() for role_name in role_names if role_name.strip()
    )

    if not normalized_role_names:
        return False

    if user.is_superuser:
        return True

    return bool(
        get_active_role_names(user).intersection(
            normalized_role_names,
        )
    )


def user_has_permission(
    user: User,
    permission_code: str,
) -> bool:
    normalized_permission_code = permission_code.strip().lower()

    if not normalized_permission_code:
        return False

    if user.is_superuser:
        return True

    return normalized_permission_code in get_active_permission_codes(
        user,
    )


def user_has_any_permission(
    user: User,
    permission_codes: frozenset[str],
) -> bool:
    normalized_permission_codes = frozenset(
        permission_code.strip().lower()
        for permission_code in permission_codes
        if permission_code.strip()
    )

    if not normalized_permission_codes:
        return False

    if user.is_superuser:
        return True

    return bool(
        get_active_permission_codes(user).intersection(
            normalized_permission_codes,
        )
    )


def require_role(
    role_name: str,
) -> AuthorizationDependency:
    normalized_role_names = normalize_authorization_values(
        (role_name,),
        value_name="role name",
    )

    async def dependency(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
    ) -> User:
        if not user_has_any_role(
            current_user,
            normalized_role_names,
        ):
            raise authorization_exception(
                code="role_required",
                message=(
                    "Your account does not have the required role for this action."
                ),
            )

        return current_user

    return dependency


def require_any_role(
    *role_names: str,
) -> AuthorizationDependency:
    normalized_role_names = normalize_authorization_values(
        role_names,
        value_name="role name",
    )

    async def dependency(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
    ) -> User:
        if not user_has_any_role(
            current_user,
            normalized_role_names,
        ):
            raise authorization_exception(
                code="role_required",
                message=(
                    "Your account does not have any of the required "
                    "roles for this action."
                ),
            )

        return current_user

    return dependency


def require_permission(
    permission_code: str,
) -> AuthorizationDependency:
    normalized_permission_codes = normalize_authorization_values(
        (permission_code,),
        value_name="permission code",
    )

    async def dependency(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
    ) -> User:
        if not user_has_any_permission(
            current_user,
            normalized_permission_codes,
        ):
            raise authorization_exception()

        return current_user

    return dependency


def require_any_permission(
    *permission_codes: str,
) -> AuthorizationDependency:
    normalized_permission_codes = normalize_authorization_values(
        permission_codes,
        value_name="permission code",
    )

    async def dependency(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
    ) -> User:
        if not user_has_any_permission(
            current_user,
            normalized_permission_codes,
        ):
            raise authorization_exception(
                message=(
                    "Your account does not have any of the required "
                    "permissions for this action."
                ),
            )

        return current_user

    return dependency
