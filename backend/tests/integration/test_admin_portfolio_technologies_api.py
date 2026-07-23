from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.project_technology import ProjectTechnology
from app.models.role import Role
from app.models.user import User
from app.security.passwords import hash_password


TEST_PASSWORD = "StrongPortfolioTechnologyPassword123!"

ADMIN_TECHNOLOGY_URL = "/api/v1/admin/portfolio/technologies"

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


def create_technology(
    *,
    name: str,
    slug: str,
    category: str = "other",
    description: str | None = None,
    icon: str | None = None,
    official_url: str | None = None,
    color: str | None = None,
    is_active: bool = True,
    sort_order: int = 0,
    deleted_at: datetime | None = None,
) -> ProjectTechnology:
    return ProjectTechnology(
        name=name,
        slug=slug,
        description=(
            description or f"{name} technology used in professional portfolio projects."
        ),
        category=category,
        icon=icon,
        official_url=official_url,
        color=color,
        is_active=is_active,
        sort_order=sort_order,
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
            "device_name": "Portfolio technology integration test",
        },
        headers={
            "User-Agent": "portfolio-technology-integration-tests",
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
async def admin_technology_records(
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
        "portfolio_technology_reader",
        permissions=[
            projects_read,
        ],
    )
    creator_role = create_role(
        "portfolio_technology_creator",
        permissions=[
            projects_create,
        ],
    )
    updater_role = create_role(
        "portfolio_technology_updater",
        permissions=[
            projects_update,
        ],
    )
    deleter_role = create_role(
        "portfolio_technology_deleter",
        permissions=[
            projects_delete,
        ],
    )
    manager_role = create_role(
        "portfolio_technology_manager",
        permissions=[
            projects_read,
            projects_create,
            projects_update,
            projects_delete,
        ],
    )
    unrelated_role = create_role(
        "portfolio_technology_outsider",
        permissions=[
            unrelated_permission,
        ],
    )

    reader_user = create_user(
        email="portfolio-technology-reader@example.com",
        roles=[
            reader_role,
        ],
    )
    creator_user = create_user(
        email="portfolio-technology-creator@example.com",
        roles=[
            creator_role,
        ],
    )
    updater_user = create_user(
        email="portfolio-technology-updater@example.com",
        roles=[
            updater_role,
        ],
    )
    deleter_user = create_user(
        email="portfolio-technology-deleter@example.com",
        roles=[
            deleter_role,
        ],
    )
    manager_user = create_user(
        email="portfolio-technology-manager@example.com",
        roles=[
            manager_role,
        ],
    )
    outsider_user = create_user(
        email="portfolio-technology-outsider@example.com",
        roles=[
            unrelated_role,
        ],
    )
    superuser = create_user(
        email="portfolio-technology-superuser@example.com",
        is_superuser=True,
    )

    python_technology = create_technology(
        name="Python",
        slug="python",
        category="language",
        icon="python",
        official_url="https://www.python.org",
        color="#3776AB",
        sort_order=1,
    )
    fastapi_technology = create_technology(
        name="FastAPI",
        slug="fastapi",
        category="framework",
        icon="fastapi",
        official_url="https://fastapi.tiangolo.com",
        color="#009688",
        sort_order=2,
    )
    postgresql_technology = create_technology(
        name="PostgreSQL",
        slug="postgresql",
        category="database",
        icon="postgresql",
        official_url="https://www.postgresql.org",
        color="#336791",
        is_active=False,
        sort_order=3,
    )
    deleted_technology = create_technology(
        name="Legacy Toolkit",
        slug="legacy-toolkit",
        category="tool",
        icon="archive",
        color="#6B7280",
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
            python_technology,
            fastapi_technology,
            postgresql_technology,
            deleted_technology,
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
        "python_technology": python_technology,
        "fastapi_technology": fastapi_technology,
        "postgresql_technology": postgresql_technology,
        "deleted_technology": deleted_technology,
    }


async def test_list_technologies_rejects_unauthenticated_request(
    client: AsyncClient,
) -> None:
    response = await client.get(
        ADMIN_TECHNOLOGY_URL,
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "invalid_authentication"


async def test_list_technologies_rejects_user_without_read_permission(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    outsider_user = cast(
        User,
        admin_technology_records["outsider_user"],
    )

    access_token = await login_user(
        client,
        email=outsider_user.email,
    )

    response = await client.get(
        ADMIN_TECHNOLOGY_URL,
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_list_technologies_returns_paginated_results(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_technology_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        ADMIN_TECHNOLOGY_URL,
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
        "python",
        "fastapi",
    ]


async def test_list_technologies_supports_search_and_status_filter(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_technology_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        ADMIN_TECHNOLOGY_URL,
        params={
            "search": "postgres",
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
    assert items[0]["slug"] == "postgresql"
    assert items[0]["is_active"] is False


async def test_list_technologies_supports_category_filter(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_technology_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        ADMIN_TECHNOLOGY_URL,
        params={
            "category": "framework",
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
    assert items[0]["slug"] == "fastapi"
    assert items[0]["category"] == "framework"


async def test_list_technologies_normalizes_category_filter(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_technology_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        ADMIN_TECHNOLOGY_URL,
        params={
            "category": "  LANGUAGE  ",
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
    assert payload["items"][0]["slug"] == "python"


async def test_list_technologies_can_include_deleted_records(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_technology_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        ADMIN_TECHNOLOGY_URL,
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

    deleted_item = next(item for item in items if item["slug"] == "legacy-toolkit")

    assert deleted_item["deleted_at"] is not None


async def test_superuser_can_list_technologies_without_explicit_permission(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    superuser = cast(
        User,
        admin_technology_records["superuser"],
    )

    access_token = await login_user(
        client,
        email=superuser.email,
    )

    response = await client.get(
        ADMIN_TECHNOLOGY_URL,
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text


async def test_get_technology_returns_technology_detail(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_technology_records["reader_user"],
    )
    python_technology = cast(
        ProjectTechnology,
        admin_technology_records["python_technology"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        f"{ADMIN_TECHNOLOGY_URL}/{python_technology.id}",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["id"] == str(python_technology.id)
    assert payload["name"] == "Python"
    assert payload["slug"] == "python"
    assert payload["category"] == "language"
    assert payload["official_url"] == "https://www.python.org"
    assert payload["deleted_at"] is None


async def test_get_technology_returns_not_found_for_unknown_id(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_technology_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        f"{ADMIN_TECHNOLOGY_URL}/{uuid4()}",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "project_technology_not_found"


async def test_get_deleted_technology_requires_include_deleted(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_technology_records["reader_user"],
    )
    deleted_technology = cast(
        ProjectTechnology,
        admin_technology_records["deleted_technology"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    hidden_response = await client.get(
        f"{ADMIN_TECHNOLOGY_URL}/{deleted_technology.id}",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert hidden_response.status_code == 404
    assert hidden_response.json()["detail"]["code"] == ("project_technology_not_found")

    visible_response = await client.get(
        f"{ADMIN_TECHNOLOGY_URL}/{deleted_technology.id}",
        params={
            "include_deleted": True,
        },
        headers=authorization_headers(
            access_token,
        ),
    )

    assert visible_response.status_code == 200, visible_response.text
    assert visible_response.json()["deleted_at"] is not None


async def test_create_technology_succeeds(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        admin_technology_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        ADMIN_TECHNOLOGY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Docker",
            "slug": "docker",
            "description": (
                "A container platform used to package and run applications."
            ),
            "category": "devops",
            "icon": "docker",
            "official_url": "https://www.docker.com",
            "color": "#2496ED",
            "is_active": True,
            "sort_order": 5,
        },
    )

    assert response.status_code == 201, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["name"] == "Docker"
    assert payload["slug"] == "docker"
    assert payload["category"] == "devops"
    assert payload["official_url"] == "https://www.docker.com"
    assert payload["color"] == "#2496ED"
    assert payload["is_active"] is True
    assert payload["sort_order"] == 5
    assert payload["deleted_at"] is None


async def test_create_technology_normalizes_name_slug_and_color(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        admin_technology_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        ADMIN_TECHNOLOGY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "  Next.js   Framework  ",
            "slug": "  NEXTJS-FRAMEWORK  ",
            "category": "framework",
            "color": "#a1b2c3",
        },
    )

    assert response.status_code == 201, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["name"] == "Next.js Framework"
    assert payload["slug"] == "nextjs-framework"
    assert payload["color"] == "#A1B2C3"


async def test_create_technology_rejects_user_without_create_permission(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_technology_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.post(
        ADMIN_TECHNOLOGY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Redis",
            "slug": "redis",
            "category": "database",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_create_technology_rejects_duplicate_name(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        admin_technology_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        ADMIN_TECHNOLOGY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Python",
            "slug": "python-language",
            "category": "language",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_technology_conflict"


async def test_create_technology_rejects_duplicate_slug(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        admin_technology_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        ADMIN_TECHNOLOGY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Python Language",
            "slug": "python",
            "category": "language",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_technology_conflict"


async def test_create_technology_rejects_invalid_category(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        admin_technology_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        ADMIN_TECHNOLOGY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Unknown Platform",
            "slug": "unknown-platform",
            "category": "unsupported",
        },
    )

    assert response.status_code == 422


async def test_create_technology_rejects_invalid_color(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        admin_technology_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        ADMIN_TECHNOLOGY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Invalid Colour Tool",
            "slug": "invalid-colour-tool",
            "category": "tool",
            "color": "blue",
        },
    )

    assert response.status_code == 422


async def test_update_technology_succeeds(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        admin_technology_records["updater_user"],
    )
    fastapi_technology = cast(
        ProjectTechnology,
        admin_technology_records["fastapi_technology"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        f"{ADMIN_TECHNOLOGY_URL}/{fastapi_technology.id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "FastAPI Framework",
            "slug": "fastapi-framework",
            "description": ("A modern Python framework for building production APIs."),
            "category": "framework",
            "sort_order": 10,
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["name"] == "FastAPI Framework"
    assert payload["slug"] == "fastapi-framework"
    assert payload["category"] == "framework"
    assert payload["sort_order"] == 10


async def test_update_technology_rejects_empty_payload(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        admin_technology_records["updater_user"],
    )
    fastapi_technology = cast(
        ProjectTechnology,
        admin_technology_records["fastapi_technology"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        f"{ADMIN_TECHNOLOGY_URL}/{fastapi_technology.id}",
        headers=authorization_headers(
            access_token,
        ),
        json={},
    )

    assert response.status_code == 422


async def test_update_technology_rejects_duplicate_slug(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        admin_technology_records["updater_user"],
    )
    fastapi_technology = cast(
        ProjectTechnology,
        admin_technology_records["fastapi_technology"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        f"{ADMIN_TECHNOLOGY_URL}/{fastapi_technology.id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "slug": "python",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_technology_conflict"


async def test_update_technology_status_succeeds(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        admin_technology_records["updater_user"],
    )
    python_technology = cast(
        ProjectTechnology,
        admin_technology_records["python_technology"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        f"{ADMIN_TECHNOLOGY_URL}/{python_technology.id}/status",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "is_active": False,
            "reason": "Temporarily hidden during portfolio review.",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["is_active"] is False


async def test_update_technology_status_rejects_user_without_update_permission(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_technology_records["reader_user"],
    )
    python_technology = cast(
        ProjectTechnology,
        admin_technology_records["python_technology"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.patch(
        f"{ADMIN_TECHNOLOGY_URL}/{python_technology.id}/status",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_delete_technology_succeeds(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    deleter_user = cast(
        User,
        admin_technology_records["deleter_user"],
    )
    postgresql_technology = cast(
        ProjectTechnology,
        admin_technology_records["postgresql_technology"],
    )

    access_token = await login_user(
        client,
        email=deleter_user.email,
    )

    response = await client.request(
        "DELETE",
        f"{ADMIN_TECHNOLOGY_URL}/{postgresql_technology.id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "reason": "The technology is no longer required.",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["id"] == str(postgresql_technology.id)
    assert payload["deleted_at"] is not None


async def test_delete_technology_rejects_user_without_delete_permission(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        admin_technology_records["updater_user"],
    )
    postgresql_technology = cast(
        ProjectTechnology,
        admin_technology_records["postgresql_technology"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.request(
        "DELETE",
        f"{ADMIN_TECHNOLOGY_URL}/{postgresql_technology.id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "reason": "Unauthorized deletion attempt.",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_delete_unknown_technology_returns_not_found(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    deleter_user = cast(
        User,
        admin_technology_records["deleter_user"],
    )

    access_token = await login_user(
        client,
        email=deleter_user.email,
    )

    response = await client.request(
        "DELETE",
        f"{ADMIN_TECHNOLOGY_URL}/{uuid4()}",
        headers=authorization_headers(
            access_token,
        ),
        json={},
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "project_technology_not_found"


async def test_restore_deleted_technology_succeeds(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        admin_technology_records["updater_user"],
    )
    deleted_technology = cast(
        ProjectTechnology,
        admin_technology_records["deleted_technology"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.post(
        f"{ADMIN_TECHNOLOGY_URL}/{deleted_technology.id}/restore",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "activate": True,
            "reason": "The technology is required again.",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["id"] == str(deleted_technology.id)
    assert payload["deleted_at"] is None
    assert payload["is_active"] is True


async def test_restore_technology_can_keep_it_inactive(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        admin_technology_records["updater_user"],
    )
    deleted_technology = cast(
        ProjectTechnology,
        admin_technology_records["deleted_technology"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.post(
        f"{ADMIN_TECHNOLOGY_URL}/{deleted_technology.id}/restore",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "activate": False,
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["deleted_at"] is None
    assert response.json()["is_active"] is False


async def test_manager_can_complete_technology_lifecycle(
    client: AsyncClient,
    admin_technology_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        admin_technology_records["manager_user"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    create_response = await client.post(
        ADMIN_TECHNOLOGY_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Kubernetes",
            "slug": "kubernetes",
            "description": (
                "Container orchestration for production portfolio projects."
            ),
            "category": "devops",
            "icon": "kubernetes",
            "official_url": "https://kubernetes.io",
            "color": "#326CE5",
            "is_active": True,
            "sort_order": 20,
        },
    )

    assert create_response.status_code == 201, create_response.text

    technology_id = str(
        create_response.json()["id"],
    )

    update_response = await client.patch(
        f"{ADMIN_TECHNOLOGY_URL}/{technology_id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "name": "Kubernetes Platform",
            "slug": "kubernetes-platform",
            "category": "platform",
        },
    )

    assert update_response.status_code == 200, update_response.text

    status_response = await client.patch(
        f"{ADMIN_TECHNOLOGY_URL}/{technology_id}/status",
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
        f"{ADMIN_TECHNOLOGY_URL}/{technology_id}",
        headers=authorization_headers(
            access_token,
        ),
        json={},
    )

    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["deleted_at"] is not None

    restore_response = await client.post(
        f"{ADMIN_TECHNOLOGY_URL}/{technology_id}/restore",
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
