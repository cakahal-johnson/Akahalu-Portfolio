from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.project_category import ProjectCategory
from app.models.role import Role
from app.models.user import User
from app.security.passwords import hash_password


TEST_PASSWORD = "StrongPortfolioCategoryPassword123!"

ADMIN_CATEGORY_URL = "/api/v1/admin/portfolio/categories"

pytestmark = pytest.mark.asyncio


def create_permission(
    code: str,
) -> Permission:
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
    roles: list[Role] | None = None,
    is_superuser: bool = False,
) -> User:
    return User(
        email=email,
        password_hash=hash_password(TEST_PASSWORD),
        first_name="Portfolio",
        last_name="Administrator",
        display_name="Portfolio Administrator",
        is_active=True,
        is_verified=True,
        is_superuser=is_superuser,
        roles=roles or [],
    )


def create_category(
    *,
    name: str,
    slug: str,
    description: str | None = None,
    is_active: bool = True,
    sort_order: int = 0,
    deleted_at: datetime | None = None,
) -> ProjectCategory:
    return ProjectCategory(
        name=name,
        slug=slug,
        description=(
            description or f"Portfolio projects belonging to the {name} category."
        ),
        icon="folder",
        color="#2563EB",
        is_active=is_active,
        sort_order=sort_order,
        seo_title=f"{name} Portfolio Projects",
        seo_description=(f"Explore professional {name.lower()} portfolio projects."),
        deleted_at=deleted_at,
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
            "device_name": "Portfolio category integration test",
        },
        headers={
            "User-Agent": "portfolio-category-integration-tests",
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

    return str(
        tokens["access_token"],
    )


def authorization_headers(
    access_token: str,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest_asyncio.fixture
async def admin_category_records(
    database_session: AsyncSession,
) -> AsyncIterator[dict[str, object]]:
    projects_read = create_permission(
        "projects.read",
    )
    projects_create = create_permission(
        "projects.create",
    )
    projects_update = create_permission(
        "projects.update",
    )
    projects_delete = create_permission(
        "projects.delete",
    )
    unrelated_permission = create_permission(
        "settings.manage",
    )

    reader_role = create_role(
        "portfolio_category_reader",
        permissions=[
            projects_read,
        ],
    )
    creator_role = create_role(
        "portfolio_category_creator",
        permissions=[
            projects_create,
        ],
    )
    updater_role = create_role(
        "portfolio_category_updater",
        permissions=[
            projects_update,
        ],
    )
    deleter_role = create_role(
        "portfolio_category_deleter",
        permissions=[
            projects_delete,
        ],
    )
    manager_role = create_role(
        "portfolio_category_manager",
        permissions=[
            projects_read,
            projects_create,
            projects_update,
            projects_delete,
        ],
    )
    unrelated_role = create_role(
        "portfolio_category_outsider",
        permissions=[
            unrelated_permission,
        ],
    )

    reader_user = create_user(
        email="portfolio-category-reader@example.com",
        roles=[
            reader_role,
        ],
    )
    creator_user = create_user(
        email="portfolio-category-creator@example.com",
        roles=[
            creator_role,
        ],
    )
    updater_user = create_user(
        email="portfolio-category-updater@example.com",
        roles=[
            updater_role,
        ],
    )
    deleter_user = create_user(
        email="portfolio-category-deleter@example.com",
        roles=[
            deleter_role,
        ],
    )
    manager_user = create_user(
        email="portfolio-category-manager@example.com",
        roles=[
            manager_role,
        ],
    )
    outsider_user = create_user(
        email="portfolio-category-outsider@example.com",
        roles=[
            unrelated_role,
        ],
    )
    superuser = create_user(
        email="portfolio-category-superuser@example.com",
        is_superuser=True,
    )

    web_category = create_category(
        name="Web Development",
        slug="web-development",
        sort_order=1,
    )
    mobile_category = create_category(
        name="Mobile Development",
        slug="mobile-development",
        sort_order=2,
    )
    data_category = create_category(
        name="Data Engineering",
        slug="data-engineering",
        is_active=False,
        sort_order=3,
    )
    deleted_category = create_category(
        name="Legacy Systems",
        slug="legacy-systems",
        is_active=False,
        sort_order=4,
        deleted_at=datetime.now(UTC),
    )

    database_session.add_all(
        [
            projects_read,
            projects_create,
            projects_update,
            projects_delete,
            unrelated_permission,
            reader_role,
            creator_role,
            updater_role,
            deleter_role,
            manager_role,
            unrelated_role,
            reader_user,
            creator_user,
            updater_user,
            deleter_user,
            manager_user,
            outsider_user,
            superuser,
            web_category,
            mobile_category,
            data_category,
            deleted_category,
        ]
    )

    await database_session.flush()

    yield {
        "reader_user": reader_user,
        "creator_user": creator_user,
        "updater_user": updater_user,
        "deleter_user": deleter_user,
        "manager_user": manager_user,
        "outsider_user": outsider_user,
        "superuser": superuser,
        "web_category": web_category,
        "mobile_category": mobile_category,
        "data_category": data_category,
        "deleted_category": deleted_category,
    }


async def test_list_categories_rejects_unauthenticated_request(
    client: AsyncClient,
) -> None:
    response = await client.get(
        ADMIN_CATEGORY_URL,
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == ("invalid_authentication")


async def test_list_categories_rejects_user_without_read_permission(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    outsider_user = cast(
        User,
        admin_category_records["outsider_user"],
    )

    access_token = await login_user(
        client,
        email=outsider_user.email,
    )

    response = await client.get(
        ADMIN_CATEGORY_URL,
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == ("insufficient_permissions")


async def test_list_categories_returns_paginated_results(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_category_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        ADMIN_CATEGORY_URL,
        params={
            "page": 1,
            "page_size": 2,
            "sort_by": "sort_order",
            "sort_direction": "asc",
        },
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["page"] == 1
    assert payload["page_size"] == 2
    assert payload["total_items"] == 3
    assert payload["total_pages"] == 2
    assert payload["has_next_page"] is True
    assert payload["has_previous_page"] is False

    items = cast(
        list[dict[str, Any]],
        payload["items"],
    )

    assert len(items) == 2
    assert [item["slug"] for item in items] == [
        "web-development",
        "mobile-development",
    ]


async def test_list_categories_supports_search_and_status_filter(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_category_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        ADMIN_CATEGORY_URL,
        params={
            "search": "data",
            "is_active": False,
        },
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["total_items"] == 1

    items = cast(
        list[dict[str, Any]],
        payload["items"],
    )

    assert len(items) == 1
    assert items[0]["slug"] == "data-engineering"
    assert items[0]["is_active"] is False


async def test_list_categories_can_include_deleted_records(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_category_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        ADMIN_CATEGORY_URL,
        params={
            "include_deleted": True,
            "sort_by": "sort_order",
            "sort_direction": "asc",
        },
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["total_items"] == 4

    items = cast(
        list[dict[str, Any]],
        payload["items"],
    )

    deleted_item = next(item for item in items if item["slug"] == "legacy-systems")

    assert deleted_item["deleted_at"] is not None


async def test_superuser_can_list_categories_without_explicit_permission(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    superuser = cast(
        User,
        admin_category_records["superuser"],
    )

    access_token = await login_user(
        client,
        email=superuser.email,
    )

    response = await client.get(
        ADMIN_CATEGORY_URL,
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text


async def test_get_category_returns_category_detail(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_category_records["reader_user"],
    )
    web_category = cast(
        ProjectCategory,
        admin_category_records["web_category"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        f"{ADMIN_CATEGORY_URL}/{web_category.id}",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["id"] == str(web_category.id)
    assert payload["name"] == "Web Development"
    assert payload["slug"] == "web-development"
    assert payload["deleted_at"] is None


async def test_get_category_returns_not_found_for_unknown_id(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_category_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        f"{ADMIN_CATEGORY_URL}/{uuid4()}",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == ("project_category_not_found")


async def test_get_deleted_category_requires_include_deleted(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_category_records["reader_user"],
    )
    deleted_category = cast(
        ProjectCategory,
        admin_category_records["deleted_category"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    hidden_response = await client.get(
        f"{ADMIN_CATEGORY_URL}/{deleted_category.id}",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert hidden_response.status_code == 404

    visible_response = await client.get(
        f"{ADMIN_CATEGORY_URL}/{deleted_category.id}",
        params={
            "include_deleted": True,
        },
        headers=authorization_headers(
            access_token,
        ),
    )

    assert visible_response.status_code == 200, visible_response.text
    assert visible_response.json()["deleted_at"] is not None


async def test_create_category_succeeds(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        admin_category_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        ADMIN_CATEGORY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Cloud Engineering",
            "slug": "cloud-engineering",
            "description": ("Cloud infrastructure, deployment and platform projects."),
            "icon": "cloud",
            "color": "#0EA5E9",
            "is_active": True,
            "sort_order": 5,
            "seo_title": "Cloud Engineering Projects",
            "seo_description": ("Explore cloud engineering and deployment projects."),
        },
    )

    assert response.status_code == 201, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["name"] == "Cloud Engineering"
    assert payload["slug"] == "cloud-engineering"
    assert payload["is_active"] is True
    assert payload["sort_order"] == 5
    assert payload["deleted_at"] is None


async def test_create_category_rejects_user_without_create_permission(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_category_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.post(
        ADMIN_CATEGORY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Cybersecurity",
            "slug": "cybersecurity",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == ("insufficient_permissions")


async def test_create_category_rejects_duplicate_slug(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        admin_category_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        ADMIN_CATEGORY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Another Web Category",
            "slug": "web-development",
            "description": (
                "A duplicate category slug used to test conflict handling."
            ),
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == ("project_category_conflict")


async def test_update_category_succeeds(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        admin_category_records["updater_user"],
    )
    mobile_category = cast(
        ProjectCategory,
        admin_category_records["mobile_category"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        f"{ADMIN_CATEGORY_URL}/{mobile_category.id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Mobile Application Development",
            "slug": "mobile-application-development",
            "description": (
                "Professional native and cross-platform mobile applications."
            ),
            "sort_order": 10,
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["name"] == ("Mobile Application Development")
    assert payload["slug"] == ("mobile-application-development")
    assert payload["sort_order"] == 10


async def test_update_category_status_succeeds(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        admin_category_records["updater_user"],
    )
    web_category = cast(
        ProjectCategory,
        admin_category_records["web_category"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        f"{ADMIN_CATEGORY_URL}/{web_category.id}/status",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "is_active": False,
            "reason": "Temporarily hidden during content review.",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["is_active"] is False


async def test_delete_category_succeeds(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    deleter_user = cast(
        User,
        admin_category_records["deleter_user"],
    )
    data_category = cast(
        ProjectCategory,
        admin_category_records["data_category"],
    )

    access_token = await login_user(
        client,
        email=deleter_user.email,
    )

    response = await client.request(
        "DELETE",
        f"{ADMIN_CATEGORY_URL}/{data_category.id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "reason": "The category is no longer required.",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["id"] == str(data_category.id)
    assert payload["deleted_at"] is not None


async def test_delete_category_rejects_user_without_delete_permission(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        admin_category_records["updater_user"],
    )
    data_category = cast(
        ProjectCategory,
        admin_category_records["data_category"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.request(
        "DELETE",
        f"{ADMIN_CATEGORY_URL}/{data_category.id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "reason": "Unauthorized deletion attempt.",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == ("insufficient_permissions")


async def test_restore_deleted_category_succeeds(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        admin_category_records["updater_user"],
    )
    deleted_category = cast(
        ProjectCategory,
        admin_category_records["deleted_category"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.post(
        f"{ADMIN_CATEGORY_URL}/{deleted_category.id}/restore",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "activate": True,
            "reason": "The category is required again.",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["id"] == str(deleted_category.id)
    assert payload["deleted_at"] is None
    assert payload["is_active"] is True


async def test_manager_can_complete_category_lifecycle(
    client: AsyncClient,
    admin_category_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        admin_category_records["manager_user"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    create_response = await client.post(
        ADMIN_CATEGORY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "DevOps Engineering",
            "slug": "devops-engineering",
            "description": (
                "Automation, infrastructure and deployment engineering projects."
            ),
            "is_active": True,
            "sort_order": 20,
        },
    )

    assert create_response.status_code == 201, create_response.text

    category_id = str(
        create_response.json()["id"],
    )

    update_response = await client.patch(
        f"{ADMIN_CATEGORY_URL}/{category_id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "DevOps and Platform Engineering",
            "slug": "devops-platform-engineering",
        },
    )

    assert update_response.status_code == 200, update_response.text

    status_response = await client.patch(
        f"{ADMIN_CATEGORY_URL}/{category_id}/status",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "is_active": False,
        },
    )

    assert status_response.status_code == 200, status_response.text
    assert status_response.json()["is_active"] is False

    delete_response = await client.request(
        "DELETE",
        f"{ADMIN_CATEGORY_URL}/{category_id}",
        headers=authorization_headers(
            access_token,
        ),
        json={},
    )

    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["deleted_at"] is not None

    restore_response = await client.post(
        f"{ADMIN_CATEGORY_URL}/{category_id}/restore",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "activate": True,
        },
    )

    assert restore_response.status_code == 200, restore_response.text
    assert restore_response.json()["deleted_at"] is None
    assert restore_response.json()["is_active"] is True
