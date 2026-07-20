from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any, cast


import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.security.passwords import hash_password


TEST_PASSWORD = "StrongRbacPassword123!"

pytestmark = pytest.mark.asyncio


def create_permission(
    code: str,
    *,
    is_active: bool = True,
    is_deleted: bool = False,
) -> Permission:
    permission = Permission(
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
    display_name: str | None = None,
    is_active: bool = True,
    is_deleted: bool = False,
) -> Role:
    role = Role(
        name=name,
        display_name=display_name or name.replace("_", " ").title(),
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
    email: str,
    roles: list[Role] | None = None,
    is_superuser: bool = False,
) -> User:
    return User(
        email=email,
        password_hash=hash_password(TEST_PASSWORD),
        first_name="RBAC",
        last_name="Tester",
        display_name="RBAC Tester",
        is_active=True,
        is_verified=True,
        is_superuser=is_superuser,
        roles=roles or [],
    )


async def login_user(
    client: AsyncClient,
    *,
    email: str,
) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": TEST_PASSWORD,
            "device_name": "RBAC integration test",
        },
        headers={
            "User-Agent": "rbac-integration-tests",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    tokens = cast(
        dict[str, Any],
        payload["tokens"],
    )

    return str(tokens["access_token"])


def authorization_headers(
    access_token: str,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest_asyncio.fixture
async def rbac_records(
    database_session: AsyncSession,
) -> AsyncIterator[dict[str, object]]:
    roles_manage = create_permission(
        "roles.manage",
    )

    projects_read = create_permission(
        "projects.read",
    )

    inactive_permission = create_permission(
        "settings.manage",
        is_active=False,
    )

    deleted_permission = create_permission(
        "messages.manage",
        is_deleted=True,
    )

    manager_role = create_role(
        "role_manager",
        display_name="Role Manager",
        permissions=[
            roles_manage,
            projects_read,
        ],
    )

    viewer_role = create_role(
        "viewer",
        display_name="Viewer",
        permissions=[
            projects_read,
        ],
    )

    inactive_role = create_role(
        "inactive_admin",
        display_name="Inactive Administrator",
        is_active=False,
    )

    deleted_role = create_role(
        "deleted_role",
        display_name="Deleted Role",
        is_deleted=True,
    )

    manager_user = create_user(
        email="rbac-manager@example.com",
        roles=[
            manager_role,
        ],
    )

    viewer_user = create_user(
        email="rbac-viewer@example.com",
        roles=[
            viewer_role,
        ],
    )

    superuser = create_user(
        email="rbac-superuser@example.com",
        is_superuser=True,
    )

    database_session.add_all(
        [
            roles_manage,
            projects_read,
            inactive_permission,
            deleted_permission,
            manager_role,
            viewer_role,
            inactive_role,
            deleted_role,
            manager_user,
            viewer_user,
            superuser,
        ]
    )

    await database_session.flush()

    yield {
        "manager_user": manager_user,
        "viewer_user": viewer_user,
        "superuser": superuser,
    }


async def test_list_roles_rejects_unauthenticated_request(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/rbac/roles",
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == ("invalid_authentication")


async def test_list_roles_rejects_user_without_permission(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    viewer_user = cast(
        User,
        rbac_records["viewer_user"],
    )

    access_token = await login_user(
        client,
        email=viewer_user.email,
    )

    response = await client.get(
        "/api/v1/rbac/roles",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == ("insufficient_permissions")


async def test_list_roles_returns_non_deleted_roles(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        rbac_records["manager_user"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    response = await client.get(
        "/api/v1/rbac/roles",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text

    payload = cast(
        list[dict[str, Any]],
        response.json(),
    )

    role_names = [str(role["name"]) for role in payload]

    assert role_names == [
        "inactive_admin",
        "role_manager",
        "viewer",
    ]

    assert "deleted_role" not in role_names

    inactive_role = next(role for role in payload if role["name"] == "inactive_admin")

    assert inactive_role["is_active"] is False

    manager_role = next(role for role in payload if role["name"] == "role_manager")

    permission_codes = {
        permission["code"] for permission in manager_role["permissions"]
    }

    assert permission_codes == {
        "projects.read",
        "roles.manage",
    }


async def test_superuser_can_list_roles(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    superuser = cast(
        User,
        rbac_records["superuser"],
    )

    access_token = await login_user(
        client,
        email=superuser.email,
    )

    response = await client.get(
        "/api/v1/rbac/roles",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text


async def test_list_permissions_returns_non_deleted_permissions(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        rbac_records["manager_user"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    response = await client.get(
        "/api/v1/rbac/permissions",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text

    payload = cast(
        list[dict[str, Any]],
        response.json(),
    )

    permission_codes = [str(permission["code"]) for permission in payload]

    assert permission_codes == [
        "projects.read",
        "roles.manage",
        "settings.manage",
    ]

    assert "messages.manage" not in permission_codes

    inactive_permission = next(
        permission for permission in payload if permission["code"] == "settings.manage"
    )

    assert inactive_permission["is_active"] is False


async def test_list_permissions_rejects_user_without_permission(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    viewer_user = cast(
        User,
        rbac_records["viewer_user"],
    )

    access_token = await login_user(
        client,
        email=viewer_user.email,
    )

    response = await client.get(
        "/api/v1/rbac/permissions",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == ("insufficient_permissions")


async def test_superuser_can_list_permissions(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    superuser = cast(
        User,
        rbac_records["superuser"],
    )

    access_token = await login_user(
        client,
        email=superuser.email,
    )

    response = await client.get(
        "/api/v1/rbac/permissions",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text
