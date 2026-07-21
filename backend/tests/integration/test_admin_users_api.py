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


TEST_PASSWORD = "StrongAdminUserPassword123!"

pytestmark = pytest.mark.asyncio


def create_permission(code: str) -> Permission:
    return Permission(
        code=code,
        name=code.replace(".", " ").title(),
        description=f"Permission for {code}.",
        is_active=True,
    )


def create_role(
    name: str,
    *,
    permissions: list[Permission] | None = None,
) -> Role:
    return Role(
        name=name,
        display_name=name.replace("_", " ").title(),
        description=f"Role for {name}.",
        is_system=False,
        is_active=True,
        permissions=permissions or [],
    )


def create_user(
    *,
    email: str,
    first_name: str,
    last_name: str,
    roles: list[Role] | None = None,
    is_active: bool = True,
    is_verified: bool = True,
    is_superuser: bool = False,
    deleted_at: datetime | None = None,
) -> User:
    return User(
        email=email,
        password_hash=hash_password(TEST_PASSWORD),
        first_name=first_name,
        last_name=last_name,
        display_name=f"{first_name} {last_name}",
        is_active=is_active,
        is_verified=is_verified,
        is_superuser=is_superuser,
        deleted_at=deleted_at,
        roles=roles or [],
    )


async def login_user_with_tokens(
    client: AsyncClient,
    *,
    email: str,
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": TEST_PASSWORD,
            "device_name": "Admin users integration test",
        },
        headers={
            "User-Agent": "admin-users-integration-tests",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(dict[str, Any], response.json())
    return cast(dict[str, Any], payload["tokens"])


async def login_user(
    client: AsyncClient,
    *,
    email: str,
) -> str:
    tokens = await login_user_with_tokens(
        client,
        email=email,
    )
    return str(tokens["access_token"])


def authorization_headers(access_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest_asyncio.fixture
async def admin_user_records(
    database_session: AsyncSession,
) -> AsyncIterator[dict[str, object]]:
    users_manage = create_permission("users.manage")
    projects_read = create_permission("projects.read")

    manager_role = create_role(
        "user_manager",
        permissions=[users_manage],
    )
    viewer_role = create_role(
        "viewer",
        permissions=[projects_read],
    )

    manager_user = create_user(
        email="admin-users-manager@example.com",
        first_name="Morgan",
        last_name="Manager",
        roles=[manager_role],
    )
    viewer_user = create_user(
        email="admin-users-viewer@example.com",
        first_name="Victor",
        last_name="Viewer",
        roles=[viewer_role],
    )
    active_user = create_user(
        email="active-user@example.com",
        first_name="Alice",
        last_name="Active",
        roles=[viewer_role],
    )
    second_active_user = create_user(
        email="bravo-user@example.com",
        first_name="Bravo",
        last_name="Builder",
    )
    inactive_user = create_user(
        email="inactive-user@example.com",
        first_name="Ian",
        last_name="Inactive",
        is_active=False,
        is_verified=False,
    )
    deleted_user = create_user(
        email="deleted-user@example.com",
        first_name="Della",
        last_name="Deleted",
        is_active=False,
        deleted_at=datetime.now(UTC),
    )
    superuser = create_user(
        email="admin-users-superuser@example.com",
        first_name="Sally",
        last_name="Superuser",
        is_superuser=True,
    )

    database_session.add_all(
        [
            users_manage,
            projects_read,
            manager_role,
            viewer_role,
            manager_user,
            viewer_user,
            active_user,
            second_active_user,
            inactive_user,
            deleted_user,
            superuser,
        ]
    )
    await database_session.flush()

    yield {
        "manager_user": manager_user,
        "viewer_user": viewer_user,
        "active_user": active_user,
        "inactive_user": inactive_user,
        "deleted_user": deleted_user,
        "superuser": superuser,
    }


async def test_list_users_rejects_unauthenticated_request(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/admin/users")

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "invalid_authentication"


async def test_list_users_rejects_user_without_permission(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    viewer_user = cast(User, admin_user_records["viewer_user"])
    access_token = await login_user(client, email=viewer_user.email)

    response = await client.get(
        "/api/v1/admin/users",
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_list_users_returns_paginated_non_deleted_users(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    access_token = await login_user(client, email=manager_user.email)

    response = await client.get(
        "/api/v1/admin/users",
        params={
            "page": 1,
            "page_size": 3,
            "sort_by": "email",
            "sort_direction": "asc",
        },
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 200, response.text

    payload = cast(dict[str, Any], response.json())

    assert payload["page"] == 1
    assert payload["page_size"] == 3
    assert payload["total_items"] == 6
    assert payload["total_pages"] == 2
    assert payload["has_next_page"] is True
    assert payload["has_previous_page"] is False
    assert len(payload["items"]) == 3

    emails = [
        str(item["email"]) for item in cast(list[dict[str, Any]], payload["items"])
    ]

    assert emails == sorted(emails)
    assert "deleted-user@example.com" not in emails


async def test_list_users_supports_search_and_filters(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    access_token = await login_user(client, email=manager_user.email)

    search_response = await client.get(
        "/api/v1/admin/users",
        params={"search": "Bravo"},
        headers=authorization_headers(access_token),
    )
    inactive_response = await client.get(
        "/api/v1/admin/users",
        params={
            "status": "inactive",
            "is_verified": "false",
        },
        headers=authorization_headers(access_token),
    )

    assert search_response.status_code == 200, search_response.text
    assert inactive_response.status_code == 200, inactive_response.text

    search_payload = cast(dict[str, Any], search_response.json())
    inactive_payload = cast(dict[str, Any], inactive_response.json())

    assert search_payload["total_items"] == 1
    assert search_payload["items"][0]["email"] == "bravo-user@example.com"

    assert inactive_payload["total_items"] == 1
    assert inactive_payload["items"][0]["email"] == "inactive-user@example.com"
    assert inactive_payload["items"][0]["is_active"] is False


async def test_list_users_can_include_deleted_accounts(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    access_token = await login_user(client, email=manager_user.email)

    response = await client.get(
        "/api/v1/admin/users",
        params={
            "include_deleted": "true",
            "search": "deleted-user@example.com",
        },
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 200, response.text
    payload = cast(dict[str, Any], response.json())

    assert payload["total_items"] == 1
    assert payload["items"][0]["is_deleted"] is True
    assert payload["items"][0]["deleted_at"] is not None


async def test_superuser_can_list_users_without_explicit_permission(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    superuser = cast(User, admin_user_records["superuser"])
    access_token = await login_user(client, email=superuser.email)

    response = await client.get(
        "/api/v1/admin/users",
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 200, response.text


async def test_get_user_returns_detail(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    active_user = cast(User, admin_user_records["active_user"])
    access_token = await login_user(client, email=manager_user.email)

    response = await client.get(
        f"/api/v1/admin/users/{active_user.id}",
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 200, response.text
    payload = cast(dict[str, Any], response.json())

    assert payload["id"] == str(active_user.id)
    assert payload["email"] == active_user.email
    assert payload["first_name"] == "Alice"
    assert payload["is_active"] is True
    assert payload["is_deleted"] is False
    assert payload["roles"][0]["name"] == "viewer"
    assert "last_login_at" in payload


async def test_get_user_returns_not_found_for_unknown_user(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    access_token = await login_user(client, email=manager_user.email)

    response = await client.get(
        f"/api/v1/admin/users/{uuid4()}",
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "user_not_found"


async def test_get_deleted_user_requires_include_deleted(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    deleted_user = cast(User, admin_user_records["deleted_user"])
    access_token = await login_user(client, email=manager_user.email)

    hidden_response = await client.get(
        f"/api/v1/admin/users/{deleted_user.id}",
        headers=authorization_headers(access_token),
    )
    visible_response = await client.get(
        f"/api/v1/admin/users/{deleted_user.id}",
        params={"include_deleted": "true"},
        headers=authorization_headers(access_token),
    )

    assert hidden_response.status_code == 404
    assert hidden_response.json()["detail"]["code"] == "user_not_found"
    assert visible_response.status_code == 200, visible_response.text
    assert visible_response.json()["is_deleted"] is True


async def test_deactivate_user_revokes_existing_tokens(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    active_user = cast(User, admin_user_records["active_user"])

    manager_token = await login_user(client, email=manager_user.email)
    target_tokens = await login_user_with_tokens(
        client,
        email=active_user.email,
    )

    response = await client.patch(
        f"/api/v1/admin/users/{active_user.id}/status",
        headers=authorization_headers(manager_token),
        json={
            "is_active": False,
            "reason": "Administrative security review.",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["is_active"] is False

    me_response = await client.get(
        "/api/v1/auth/me",
        headers=authorization_headers(str(target_tokens["access_token"])),
    )
    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": str(target_tokens["refresh_token"]),
        },
    )

    assert me_response.status_code == 401
    assert refresh_response.status_code == 401


async def test_activate_inactive_user_succeeds(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    inactive_user = cast(User, admin_user_records["inactive_user"])
    access_token = await login_user(client, email=manager_user.email)

    response = await client.patch(
        f"/api/v1/admin/users/{inactive_user.id}/status",
        headers=authorization_headers(access_token),
        json={"is_active": True},
    )

    assert response.status_code == 200, response.text
    assert response.json()["is_active"] is True


async def test_user_manager_cannot_deactivate_own_account(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    access_token = await login_user(client, email=manager_user.email)

    response = await client.patch(
        f"/api/v1/admin/users/{manager_user.id}/status",
        headers=authorization_headers(access_token),
        json={"is_active": False},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == ("self_account_modification_forbidden")


async def test_deleted_user_status_cannot_be_changed(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    deleted_user = cast(User, admin_user_records["deleted_user"])
    access_token = await login_user(client, email=manager_user.email)

    response = await client.patch(
        f"/api/v1/admin/users/{deleted_user.id}/status",
        headers=authorization_headers(access_token),
        json={"is_active": True},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "user_deleted"


async def test_delete_user_soft_deletes_account_and_revokes_tokens(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    active_user = cast(User, admin_user_records["active_user"])

    manager_token = await login_user(client, email=manager_user.email)
    target_tokens = await login_user_with_tokens(
        client,
        email=active_user.email,
    )

    response = await client.request(
        "DELETE",
        f"/api/v1/admin/users/{active_user.id}",
        headers=authorization_headers(manager_token),
        json={
            "reason": "User requested account deletion.",
        },
    )

    assert response.status_code == 200, response.text
    payload = cast(dict[str, Any], response.json())

    assert payload["is_active"] is False
    assert payload["is_deleted"] is True
    assert payload["deleted_at"] is not None

    me_response = await client.get(
        "/api/v1/auth/me",
        headers=authorization_headers(str(target_tokens["access_token"])),
    )
    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": str(target_tokens["refresh_token"]),
        },
    )

    assert me_response.status_code == 401
    assert refresh_response.status_code == 401


async def test_user_manager_cannot_delete_own_account(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    access_token = await login_user(client, email=manager_user.email)

    response = await client.request(
        "DELETE",
        f"/api/v1/admin/users/{manager_user.id}",
        headers=authorization_headers(access_token),
        json={},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == ("self_account_modification_forbidden")


async def test_deleting_already_deleted_user_is_rejected(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    deleted_user = cast(User, admin_user_records["deleted_user"])
    access_token = await login_user(client, email=manager_user.email)

    response = await client.request(
        "DELETE",
        f"/api/v1/admin/users/{deleted_user.id}",
        headers=authorization_headers(access_token),
        json={},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "user_already_deleted"


async def test_restore_deleted_user_succeeds(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    deleted_user = cast(User, admin_user_records["deleted_user"])
    access_token = await login_user(client, email=manager_user.email)

    response = await client.post(
        f"/api/v1/admin/users/{deleted_user.id}/restore",
        headers=authorization_headers(access_token),
        json={
            "activate": True,
            "reason": "Deletion was reversed after review.",
        },
    )

    assert response.status_code == 200, response.text
    payload = cast(dict[str, Any], response.json())

    assert payload["is_deleted"] is False
    assert payload["deleted_at"] is None
    assert payload["is_active"] is True


async def test_restoring_non_deleted_user_is_rejected(
    client: AsyncClient,
    admin_user_records: dict[str, object],
) -> None:
    manager_user = cast(User, admin_user_records["manager_user"])
    active_user = cast(User, admin_user_records["active_user"])
    access_token = await login_user(client, email=manager_user.email)

    response = await client.post(
        f"/api/v1/admin/users/{active_user.id}/restore",
        headers=authorization_headers(access_token),
        json={"activate": True},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "user_not_deleted"
