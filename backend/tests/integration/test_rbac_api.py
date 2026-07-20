from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

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
        "roles_manage": roles_manage,
        "projects_read": projects_read,
        "inactive_permission": inactive_permission,
        "deleted_permission": deleted_permission,
        "manager_role": manager_role,
        "viewer_role": viewer_role,
        "inactive_role": inactive_role,
    }


async def test_create_role_succeeds(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        rbac_records["manager_user"],
    )

    projects_read = cast(
        Permission,
        rbac_records["projects_read"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    response = await client.post(
        "/api/v1/rbac/roles",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "content_manager",
            "display_name": "Content Manager",
            "description": "Manages portfolio content.",
            "is_active": True,
            "permission_ids": [
                str(projects_read.id),
            ],
        },
    )

    assert response.status_code == 201, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["name"] == "content_manager"
    assert payload["display_name"] == "Content Manager"
    assert payload["is_system"] is False
    assert payload["is_active"] is True

    assert [permission["code"] for permission in payload["permissions"]] == [
        "projects.read",
    ]


async def test_create_role_rejects_duplicate_name(
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

    response = await client.post(
        "/api/v1/rbac/roles",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "viewer",
            "display_name": "Another Viewer",
            "permission_ids": [],
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == ("role_already_exists")


async def test_create_role_rejects_inactive_permission(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        rbac_records["manager_user"],
    )

    inactive_permission = cast(
        Permission,
        rbac_records["inactive_permission"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    response = await client.post(
        "/api/v1/rbac/roles",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "invalid_permission_role",
            "display_name": "Invalid Permission Role",
            "permission_ids": [
                str(inactive_permission.id),
            ],
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == ("invalid_permissions")


async def test_create_role_rejects_duplicate_permission_ids(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        rbac_records["manager_user"],
    )

    projects_read = cast(
        Permission,
        rbac_records["projects_read"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    response = await client.post(
        "/api/v1/rbac/roles",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "duplicate_permissions",
            "display_name": "Duplicate Permissions",
            "permission_ids": [
                str(projects_read.id),
                str(projects_read.id),
            ],
        },
    )

    assert response.status_code == 422


async def test_create_role_rejects_is_system_input(
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

    response = await client.post(
        "/api/v1/rbac/roles",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "ordinary_role",
            "display_name": "Ordinary Role",
            "is_system": True,
            "permission_ids": [],
        },
    )

    assert response.status_code == 422


async def test_update_role_succeeds(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        rbac_records["manager_user"],
    )

    viewer_role = cast(
        Role,
        rbac_records["viewer_role"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    response = await client.patch(
        f"/api/v1/rbac/roles/{viewer_role.id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "display_name": "Read-only Viewer",
            "description": "Updated viewer description.",
            "is_active": False,
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["name"] == "viewer"
    assert payload["display_name"] == "Read-only Viewer"
    assert payload["description"] == ("Updated viewer description.")
    assert payload["is_active"] is False


async def test_update_role_returns_not_found(
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

    response = await client.patch(
        f"/api/v1/rbac/roles/{uuid4()}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "display_name": "Missing Role",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == ("role_not_found")


async def test_update_rejects_super_admin_deactivation(
    client: AsyncClient,
    database_session: AsyncSession,
    rbac_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        rbac_records["manager_user"],
    )

    super_admin_role = create_role(
        "super_admin",
        display_name="Super Administrator",
    )
    super_admin_role.is_system = True

    database_session.add(super_admin_role)
    await database_session.flush()

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    response = await client.patch(
        f"/api/v1/rbac/roles/{super_admin_role.id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == ("protected_system_role")


async def test_replace_role_permissions_succeeds(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        rbac_records["manager_user"],
    )

    viewer_role = cast(
        Role,
        rbac_records["viewer_role"],
    )

    roles_manage = cast(
        Permission,
        rbac_records["roles_manage"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    response = await client.put(
        f"/api/v1/rbac/roles/{viewer_role.id}/permissions",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "permission_ids": [
                str(roles_manage.id),
            ],
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert [permission["code"] for permission in payload["permissions"]] == [
        "roles.manage",
    ]


async def test_replace_role_permissions_allows_empty_set(
    client: AsyncClient,
    rbac_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        rbac_records["manager_user"],
    )

    viewer_role = cast(
        Role,
        rbac_records["viewer_role"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    response = await client.put(
        f"/api/v1/rbac/roles/{viewer_role.id}/permissions",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "permission_ids": [],
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["permissions"] == []


async def test_replace_permissions_rejects_super_admin(
    client: AsyncClient,
    database_session: AsyncSession,
    rbac_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        rbac_records["manager_user"],
    )

    super_admin_role = create_role(
        "super_admin",
        display_name="Super Administrator",
    )
    super_admin_role.is_system = True

    database_session.add(super_admin_role)
    await database_session.flush()

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    response = await client.put(
        f"/api/v1/rbac/roles/{super_admin_role.id}/permissions",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "permission_ids": [],
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == ("protected_system_role")


async def test_role_management_rejects_user_without_permission(
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

    response = await client.post(
        "/api/v1/rbac/roles",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "unauthorized_role",
            "display_name": "Unauthorized Role",
            "permission_ids": [],
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == ("insufficient_permissions")


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
