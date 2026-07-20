# backend/tests/unit/test_authorization.py

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.dependencies.authorization import (
    get_active_permission_codes,
    get_active_role_names,
    require_any_permission,
    require_any_role,
    require_permission,
    require_role,
    user_has_any_permission,
    user_has_any_role,
    user_has_permission,
    user_has_role,
)
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


def create_permission(
    code: str,
    *,
    is_active: bool = True,
    is_deleted: bool = False,
) -> Permission:
    permission = Permission(
        id=uuid4(),
        code=code,
        name=code.replace(".", " ").title(),
        description=f"Permission for {code}.",
        is_active=is_active,
    )

    if is_deleted:
        permission.deleted_at = datetime.now(UTC)

    return permission


def create_role(
    name: str,
    *,
    permissions: list[Permission] | None = None,
    is_active: bool = True,
    is_deleted: bool = False,
) -> Role:
    role = Role(
        id=uuid4(),
        name=name,
        display_name=name.replace("_", " ").title(),
        description=f"Role for {name}.",
        is_system=False,
        is_active=is_active,
        permissions=permissions or [],
    )

    if is_deleted:
        role.deleted_at = datetime.now(UTC)

    return role


def create_user(
    *,
    roles: list[Role] | None = None,
    is_superuser: bool = False,
) -> User:
    return User(
        id=uuid4(),
        email=f"{uuid4()}@example.com",
        password_hash="unused-password-hash",
        first_name="Authorization",
        last_name="Tester",
        is_active=True,
        is_verified=True,
        is_superuser=is_superuser,
        roles=roles or [],
    )


def test_get_active_role_names_returns_active_roles() -> None:
    user = create_user(
        roles=[
            create_role("admin"),
            create_role("editor"),
        ],
    )

    assert get_active_role_names(user) == frozenset(
        {
            "admin",
            "editor",
        }
    )


def test_get_active_role_names_ignores_inactive_roles() -> None:
    user = create_user(
        roles=[
            create_role(
                "admin",
                is_active=False,
            ),
            create_role("editor"),
        ],
    )

    assert get_active_role_names(user) == frozenset(
        {
            "editor",
        }
    )


def test_get_active_role_names_ignores_deleted_roles() -> None:
    user = create_user(
        roles=[
            create_role(
                "admin",
                is_deleted=True,
            ),
            create_role("viewer"),
        ],
    )

    assert get_active_role_names(user) == frozenset(
        {
            "viewer",
        }
    )


def test_get_active_permission_codes_returns_role_permissions() -> None:
    user = create_user(
        roles=[
            create_role(
                "editor",
                permissions=[
                    create_permission("projects.read"),
                    create_permission("projects.update"),
                ],
            ),
        ],
    )

    assert get_active_permission_codes(user) == frozenset(
        {
            "projects.read",
            "projects.update",
        }
    )


def test_get_active_permission_codes_ignores_inactive_role() -> None:
    user = create_user(
        roles=[
            create_role(
                "editor",
                permissions=[
                    create_permission("projects.update"),
                ],
                is_active=False,
            ),
        ],
    )

    assert get_active_permission_codes(user) == frozenset()


def test_get_active_permission_codes_ignores_deleted_role() -> None:
    user = create_user(
        roles=[
            create_role(
                "editor",
                permissions=[
                    create_permission("projects.update"),
                ],
                is_deleted=True,
            ),
        ],
    )

    assert get_active_permission_codes(user) == frozenset()


def test_get_active_permission_codes_ignores_inactive_permission() -> None:
    user = create_user(
        roles=[
            create_role(
                "editor",
                permissions=[
                    create_permission(
                        "projects.update",
                        is_active=False,
                    ),
                    create_permission("projects.read"),
                ],
            ),
        ],
    )

    assert get_active_permission_codes(user) == frozenset(
        {
            "projects.read",
        }
    )


def test_get_active_permission_codes_ignores_deleted_permission() -> None:
    user = create_user(
        roles=[
            create_role(
                "editor",
                permissions=[
                    create_permission(
                        "projects.update",
                        is_deleted=True,
                    ),
                    create_permission("projects.read"),
                ],
            ),
        ],
    )

    assert get_active_permission_codes(user) == frozenset(
        {
            "projects.read",
        }
    )


def test_get_active_permission_codes_removes_duplicates() -> None:
    shared_permission = create_permission("projects.read")

    user = create_user(
        roles=[
            create_role(
                "admin",
                permissions=[shared_permission],
            ),
            create_role(
                "viewer",
                permissions=[shared_permission],
            ),
        ],
    )

    assert get_active_permission_codes(user) == frozenset(
        {
            "projects.read",
        }
    )


def test_user_has_role_accepts_matching_active_role() -> None:
    user = create_user(
        roles=[
            create_role("editor"),
        ],
    )

    assert user_has_role(user, "editor") is True


def test_user_has_role_normalizes_role_name() -> None:
    user = create_user(
        roles=[
            create_role("editor"),
        ],
    )

    assert user_has_role(user, " EDITOR ") is True


def test_user_has_role_rejects_missing_role() -> None:
    user = create_user(
        roles=[
            create_role("viewer"),
        ],
    )

    assert user_has_role(user, "admin") is False


def test_user_has_any_role_accepts_one_matching_role() -> None:
    user = create_user(
        roles=[
            create_role("editor"),
        ],
    )

    assert (
        user_has_any_role(
            user,
            frozenset(
                {
                    "admin",
                    "editor",
                }
            ),
        )
        is True
    )


def test_user_has_permission_accepts_permission_from_role() -> None:
    user = create_user(
        roles=[
            create_role(
                "editor",
                permissions=[
                    create_permission("projects.update"),
                ],
            ),
        ],
    )

    assert user_has_permission(user, "projects.update") is True


def test_user_has_permission_normalizes_permission_code() -> None:
    user = create_user(
        roles=[
            create_role(
                "editor",
                permissions=[
                    create_permission("projects.update"),
                ],
            ),
        ],
    )

    assert user_has_permission(user, " PROJECTS.UPDATE ") is True


def test_user_has_permission_rejects_missing_permission() -> None:
    user = create_user(
        roles=[
            create_role(
                "viewer",
                permissions=[
                    create_permission("projects.read"),
                ],
            ),
        ],
    )

    assert user_has_permission(user, "projects.delete") is False


def test_user_has_any_permission_accepts_one_permission() -> None:
    user = create_user(
        roles=[
            create_role(
                "editor",
                permissions=[
                    create_permission("projects.update"),
                ],
            ),
        ],
    )

    assert (
        user_has_any_permission(
            user,
            frozenset(
                {
                    "projects.delete",
                    "projects.update",
                }
            ),
        )
        is True
    )


def test_superuser_bypasses_role_checks() -> None:
    user = create_user(
        is_superuser=True,
    )

    assert user_has_role(user, "admin") is True
    assert (
        user_has_any_role(
            user,
            frozenset(
                {
                    "admin",
                    "editor",
                }
            ),
        )
        is True
    )


def test_superuser_bypasses_permission_checks() -> None:
    user = create_user(
        is_superuser=True,
    )

    assert user_has_permission(user, "roles.manage") is True
    assert (
        user_has_any_permission(
            user,
            frozenset(
                {
                    "roles.manage",
                    "users.manage",
                }
            ),
        )
        is True
    )


def test_superuser_does_not_bypass_blank_role_check() -> None:
    user = create_user(
        is_superuser=True,
    )

    assert user_has_role(user, "  ") is False


def test_superuser_does_not_bypass_empty_role_collection() -> None:
    user = create_user(
        is_superuser=True,
    )

    assert (
        user_has_any_role(
            user,
            frozenset(),
        )
        is False
    )


def test_superuser_does_not_bypass_blank_permission_check() -> None:
    user = create_user(
        is_superuser=True,
    )

    assert user_has_permission(user, "  ") is False


def test_superuser_does_not_bypass_empty_permission_collection() -> None:
    user = create_user(
        is_superuser=True,
    )

    assert (
        user_has_any_permission(
            user,
            frozenset(),
        )
        is False
    )


@pytest.mark.asyncio
async def test_require_role_returns_authorized_user() -> None:
    user = create_user(
        roles=[
            create_role("admin"),
        ],
    )

    dependency = require_role("admin")

    assert await dependency(user) is user


@pytest.mark.asyncio
async def test_require_role_rejects_unauthorized_user() -> None:
    user = create_user(
        roles=[
            create_role("viewer"),
        ],
    )

    dependency = require_role("admin")

    with pytest.raises(HTTPException) as exception_info:
        await dependency(user)

    assert exception_info.value.status_code == 403
    assert exception_info.value.detail == {
        "code": "role_required",
        "message": "Your account does not have the required role for this action.",
    }


@pytest.mark.asyncio
async def test_require_any_role_returns_authorized_user() -> None:
    user = create_user(
        roles=[
            create_role("editor"),
        ],
    )

    dependency = require_any_role(
        "admin",
        "editor",
    )

    assert await dependency(user) is user


@pytest.mark.asyncio
async def test_require_permission_returns_authorized_user() -> None:
    user = create_user(
        roles=[
            create_role(
                "editor",
                permissions=[
                    create_permission("projects.update"),
                ],
            ),
        ],
    )

    dependency = require_permission("projects.update")

    assert await dependency(user) is user


@pytest.mark.asyncio
async def test_require_permission_rejects_unauthorized_user() -> None:
    user = create_user(
        roles=[
            create_role(
                "viewer",
                permissions=[
                    create_permission("projects.read"),
                ],
            ),
        ],
    )

    dependency = require_permission("projects.delete")

    with pytest.raises(HTTPException) as exception_info:
        await dependency(user)

    assert exception_info.value.status_code == 403
    assert exception_info.value.detail == {
        "code": "insufficient_permissions",
        "message": "You do not have permission to perform this action.",
    }


@pytest.mark.asyncio
async def test_require_any_permission_returns_authorized_user() -> None:
    user = create_user(
        roles=[
            create_role(
                "editor",
                permissions=[
                    create_permission("blog.update"),
                ],
            ),
        ],
    )

    dependency = require_any_permission(
        "blog.create",
        "blog.update",
    )

    assert await dependency(user) is user


def test_require_role_rejects_empty_role_name() -> None:
    with pytest.raises(
        ValueError,
        match="At least one role name must be provided",
    ):
        require_role("  ")


def test_require_any_role_rejects_empty_collection() -> None:
    with pytest.raises(
        ValueError,
        match="At least one role name must be provided",
    ):
        require_any_role()


def test_require_permission_rejects_empty_permission_code() -> None:
    with pytest.raises(
        ValueError,
        match="At least one permission code must be provided",
    ):
        require_permission("  ")


def test_require_any_permission_rejects_empty_collection() -> None:
    with pytest.raises(
        ValueError,
        match="At least one permission code must be provided",
    ):
        require_any_permission()
