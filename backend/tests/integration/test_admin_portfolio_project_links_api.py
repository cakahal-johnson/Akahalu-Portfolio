from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.project import Project
from app.models.project_category import ProjectCategory
from app.models.project_link import ProjectLink
from app.models.role import Role
from app.models.user import User
from app.security.passwords import hash_password


TEST_PASSWORD = "StrongPortfolioProjectLinkPassword123!"

ADMIN_PROJECT_URL = "/api/v1/admin/portfolio/projects"
PUBLIC_PROJECT_URL = "/api/v1/portfolio/projects"

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
        password_hash=hash_password(
            TEST_PASSWORD,
        ),
        first_name="Portfolio",
        last_name="Link Administrator",
        display_name="Portfolio Link Administrator",
        is_active=True,
        is_verified=True,
        is_superuser=is_superuser,
        roles=roles or [],
    )


def create_category(
    *,
    name: str,
    slug: str,
) -> ProjectCategory:
    return ProjectCategory(
        name=name,
        slug=slug,
        description=f"{name} portfolio projects.",
        icon="folder",
        color="#3366FF",
        is_active=True,
        sort_order=0,
    )


def create_project(
    *,
    title: str,
    slug: str,
    category: ProjectCategory,
    created_by: User,
    status: str = "draft",
    visibility: str = "private",
    published_at: datetime | None = None,
    deleted_at: datetime | None = None,
) -> Project:
    return Project(
        title=title,
        slug=slug,
        short_description=(
            f"{title} is a professional portfolio project with secure external links."
        ),
        description=(
            f"{title} demonstrates secure project-link administration, "
            "validation, authorization, ordering, and public visibility."
        ),
        category=category,
        status=status,
        visibility=visibility,
        is_featured=False,
        sort_order=0,
        published_at=published_at,
        deleted_at=deleted_at,
        created_by=created_by,
        updated_by=created_by,
    )


def create_project_link(
    *,
    project: Project,
    label: str,
    url: str,
    link_type: str = "other",
    icon: str | None = None,
    opens_in_new_tab: bool = True,
    is_active: bool = True,
    sort_order: int = 0,
    deleted_at: datetime | None = None,
) -> ProjectLink:
    return ProjectLink(
        project=project,
        label=label,
        url=url,
        link_type=link_type,
        icon=icon,
        opens_in_new_tab=opens_in_new_tab,
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
            "device_name": "Portfolio project-link integration test",
        },
        headers={
            "User-Agent": "portfolio-project-link-integration-tests",
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


def project_links_url(
    project: Project,
) -> str:
    return f"{ADMIN_PROJECT_URL}/{project.id}/links"


def project_link_detail_url(
    project: Project,
    link: ProjectLink,
) -> str:
    return f"{project_links_url(project)}/{link.id}"


def valid_project_link_payload(
    *,
    label: str = "GitHub Repository",
    url: str = "https://github.com/example/secure-portfolio",
    link_type: str = "repository",
    icon: str | None = "github",
    opens_in_new_tab: bool = True,
    is_active: bool = True,
    sort_order: int = 10,
) -> dict[str, Any]:
    return {
        "label": label,
        "url": url,
        "link_type": link_type,
        "icon": icon,
        "opens_in_new_tab": opens_in_new_tab,
        "is_active": is_active,
        "sort_order": sort_order,
    }


@pytest_asyncio.fixture
async def admin_project_link_records(
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
        "portfolio_link_reader",
        permissions=[
            projects_read,
        ],
    )
    creator_role = create_role(
        "portfolio_link_creator",
        permissions=[
            projects_create,
        ],
    )
    updater_role = create_role(
        "portfolio_link_updater",
        permissions=[
            projects_update,
        ],
    )
    deleter_role = create_role(
        "portfolio_link_deleter",
        permissions=[
            projects_delete,
        ],
    )
    manager_role = create_role(
        "portfolio_link_manager",
        permissions=[
            projects_read,
            projects_create,
            projects_update,
            projects_delete,
        ],
    )
    unrelated_role = create_role(
        "portfolio_link_unrelated",
        permissions=[
            unrelated_permission,
        ],
    )

    reader_user = create_user(
        email="portfolio-link-reader@example.com",
        roles=[
            reader_role,
        ],
    )
    creator_user = create_user(
        email="portfolio-link-creator@example.com",
        roles=[
            creator_role,
        ],
    )
    updater_user = create_user(
        email="portfolio-link-updater@example.com",
        roles=[
            updater_role,
        ],
    )
    deleter_user = create_user(
        email="portfolio-link-deleter@example.com",
        roles=[
            deleter_role,
        ],
    )
    manager_user = create_user(
        email="portfolio-link-manager@example.com",
        roles=[
            manager_role,
        ],
    )
    unrelated_user = create_user(
        email="portfolio-link-unrelated@example.com",
        roles=[
            unrelated_role,
        ],
    )
    superuser = create_user(
        email="portfolio-link-superuser@example.com",
        is_superuser=True,
    )

    category = create_category(
        name="Web Applications",
        slug="web-applications",
    )

    project = create_project(
        title="Secure Portfolio Platform",
        slug="secure-portfolio-platform",
        category=category,
        created_by=manager_user,
        status="published",
        visibility="public",
        published_at=datetime.now(UTC),
    )

    second_project = create_project(
        title="Independent Mobile Application",
        slug="independent-mobile-application",
        category=category,
        created_by=manager_user,
    )

    deleted_project = create_project(
        title="Deleted Portfolio Project",
        slug="deleted-portfolio-project",
        category=category,
        created_by=manager_user,
        deleted_at=datetime.now(UTC),
    )

    repository_link = create_project_link(
        project=project,
        label="Source Code",
        url="https://github.com/example/secure-portfolio",
        link_type="repository",
        icon="github",
        sort_order=10,
    )

    documentation_link = create_project_link(
        project=project,
        label="Documentation",
        url="https://docs.example.com/secure-portfolio",
        link_type="documentation",
        icon="book",
        opens_in_new_tab=False,
        sort_order=20,
    )

    inactive_link = create_project_link(
        project=project,
        label="Legacy Demo",
        url="https://legacy.example.com/secure-portfolio",
        link_type="live_demo",
        icon="external-link",
        is_active=False,
        sort_order=30,
    )

    deleted_link = create_project_link(
        project=project,
        label="Archived Article",
        url="https://example.com/articles/archived-portfolio",
        link_type="article",
        icon="article",
        is_active=False,
        sort_order=40,
        deleted_at=datetime.now(UTC),
    )

    second_project_link = create_project_link(
        project=second_project,
        label="Mobile Repository",
        url="https://github.com/example/mobile-application",
        link_type="repository",
        icon="github",
        sort_order=10,
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
            unrelated_user,
            superuser,
            category,
            project,
            second_project,
            deleted_project,
            repository_link,
            documentation_link,
            inactive_link,
            deleted_link,
            second_project_link,
        ]
    )

    await database_session.flush()

    yield {
        "reader_user": reader_user,
        "creator_user": creator_user,
        "updater_user": updater_user,
        "deleter_user": deleter_user,
        "manager_user": manager_user,
        "unrelated_user": unrelated_user,
        "superuser": superuser,
        "category": category,
        "project": project,
        "second_project": second_project,
        "deleted_project": deleted_project,
        "repository_link": repository_link,
        "documentation_link": documentation_link,
        "inactive_link": inactive_link,
        "deleted_link": deleted_link,
        "second_project_link": second_project_link,
    }


async def test_list_project_links_rejects_unauthenticated_request(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )

    response = await client.get(
        project_links_url(project),
    )

    assert response.status_code == 401


async def test_list_project_links_rejects_user_without_read_permission(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    unrelated_user = cast(
        User,
        admin_project_link_records["unrelated_user"],
    )

    access_token = await login_user(
        client,
        email=unrelated_user.email,
    )

    response = await client.get(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_list_project_links_returns_paginated_records(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        params={
            "page": 1,
            "page_size": 2,
        },
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
    assert len(payload["items"]) == 2

    assert [item["label"] for item in payload["items"]] == [
        "Source Code",
        "Documentation",
    ]


async def test_list_project_links_can_include_deleted_records(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        params={
            "include_deleted": True,
        },
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

    archived_link = next(item for item in items if item["label"] == "Archived Article")

    assert archived_link["deleted_at"] is not None
    assert archived_link["is_active"] is False


async def test_list_project_links_supports_search(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        params={
            "search": "documentation",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["total_items"] == 1
    assert payload["items"][0]["label"] == "Documentation"


async def test_list_project_links_supports_type_filter(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        params={
            "link_type": "repository",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["total_items"] == 1
    assert payload["items"][0]["link_type"] == "repository"


async def test_list_project_links_supports_active_filter(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        params={
            "is_active": False,
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["total_items"] == 1
    assert payload["items"][0]["label"] == "Legacy Demo"
    assert payload["items"][0]["is_active"] is False


async def test_list_project_links_supports_new_tab_filter(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        params={
            "opens_in_new_tab": False,
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["total_items"] == 1
    assert payload["items"][0]["label"] == "Documentation"
    assert payload["items"][0]["opens_in_new_tab"] is False


async def test_superuser_can_list_project_links(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    superuser = cast(
        User,
        admin_project_link_records["superuser"],
    )

    access_token = await login_user(
        client,
        email=superuser.email,
    )

    response = await client.get(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json()["total_items"] == 3


async def test_list_project_links_rejects_unknown_project(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        f"{ADMIN_PROJECT_URL}/{uuid4()}/links",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "project_not_found"


async def test_get_project_link_returns_detail(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    repository_link = cast(
        ProjectLink,
        admin_project_link_records["repository_link"],
    )
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        project_link_detail_url(
            project,
            repository_link,
        ),
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["id"] == str(repository_link.id)
    assert payload["project_id"] == str(project.id)
    assert payload["label"] == "Source Code"
    assert payload["link_type"] == "repository"
    assert payload["is_active"] is True
    assert payload["deleted_at"] is None


async def test_get_project_link_rejects_link_from_another_project(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    second_project_link = cast(
        ProjectLink,
        admin_project_link_records["second_project_link"],
    )
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        f"{project_links_url(project)}/{second_project_link.id}",
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "project_link_not_found"


async def test_get_deleted_project_link_requires_include_deleted(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    deleted_link = cast(
        ProjectLink,
        admin_project_link_records["deleted_link"],
    )
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    hidden_response = await client.get(
        project_link_detail_url(
            project,
            deleted_link,
        ),
        headers=authorization_headers(
            access_token,
        ),
    )

    visible_response = await client.get(
        project_link_detail_url(
            project,
            deleted_link,
        ),
        headers=authorization_headers(
            access_token,
        ),
        params={
            "include_deleted": True,
        },
    )

    assert hidden_response.status_code == 404
    assert visible_response.status_code == 200, visible_response.text
    assert visible_response.json()["deleted_at"] is not None


async def test_create_project_link_succeeds(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    creator_user = cast(
        User,
        admin_project_link_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_project_link_payload(
            label="API Documentation",
            url="https://api.example.com/docs",
            link_type="api",
            icon="code",
            sort_order=50,
        ),
    )

    assert response.status_code == 201, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["project_id"] == str(project.id)
    assert payload["label"] == "API Documentation"
    assert payload["url"].startswith(
        "https://api.example.com/docs",
    )
    assert payload["link_type"] == "api"
    assert payload["icon"] == "code"
    assert payload["opens_in_new_tab"] is True
    assert payload["is_active"] is True
    assert payload["sort_order"] == 50
    assert payload["deleted_at"] is None


async def test_create_project_link_normalizes_fields(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    creator_user = cast(
        User,
        admin_project_link_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_project_link_payload(
            label="  Design   Prototype  ",
            url="  https://figma.com/file/portfolio-design  ",
            link_type="design",
            icon="  figma   icon  ",
        ),
    )

    assert response.status_code == 201, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["label"] == "Design Prototype"
    assert payload["icon"] == "figma icon"
    assert payload["url"].startswith(
        "https://figma.com/file/portfolio-design",
    )


async def test_create_project_link_rejects_user_without_create_permission(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.post(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_project_link_payload(),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_create_project_link_rejects_duplicate_url(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    repository_link = cast(
        ProjectLink,
        admin_project_link_records["repository_link"],
    )
    creator_user = cast(
        User,
        admin_project_link_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_project_link_payload(
            label="Alternative Repository Label",
            url=repository_link.url,
        ),
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_link_conflict"


async def test_create_project_link_rejects_duplicate_label_case_insensitively(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    creator_user = cast(
        User,
        admin_project_link_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_project_link_payload(
            label="source code",
            url="https://gitlab.com/example/secure-portfolio",
        ),
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_link_conflict"


async def test_create_project_link_rejects_invalid_url(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    creator_user = cast(
        User,
        admin_project_link_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_project_link_payload(
            label="Invalid Resource",
            url="not-a-valid-url",
        ),
    )

    assert response.status_code == 422


async def test_create_project_link_rejects_invalid_type(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    creator_user = cast(
        User,
        admin_project_link_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_project_link_payload(
            label="Unsupported Resource",
            url="https://example.com/unsupported",
            link_type="unsupported",
        ),
    )

    assert response.status_code == 422


async def test_create_project_link_rejects_negative_sort_order(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    creator_user = cast(
        User,
        admin_project_link_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_project_link_payload(
            label="Negative Position Resource",
            url="https://example.com/negative-position",
            sort_order=-1,
        ),
    )

    assert response.status_code == 422


async def test_create_project_link_rejects_unknown_project(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        admin_project_link_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        f"{ADMIN_PROJECT_URL}/{uuid4()}/links",
        headers=authorization_headers(
            access_token,
        ),
        json=valid_project_link_payload(),
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "project_not_found"


async def test_update_project_link_succeeds(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    documentation_link = cast(
        ProjectLink,
        admin_project_link_records["documentation_link"],
    )
    updater_user = cast(
        User,
        admin_project_link_records["updater_user"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        project_link_detail_url(
            project,
            documentation_link,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={
            "label": "Developer Documentation",
            "url": "https://developers.example.com/secure-portfolio",
            "link_type": "documentation",
            "icon": "developer-docs",
            "opens_in_new_tab": True,
            "sort_order": 5,
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["label"] == "Developer Documentation"
    assert payload["url"].startswith(
        "https://developers.example.com/secure-portfolio",
    )
    assert payload["icon"] == "developer-docs"
    assert payload["opens_in_new_tab"] is True
    assert payload["sort_order"] == 5


async def test_update_project_link_rejects_empty_payload(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    repository_link = cast(
        ProjectLink,
        admin_project_link_records["repository_link"],
    )
    updater_user = cast(
        User,
        admin_project_link_records["updater_user"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        project_link_detail_url(
            project,
            repository_link,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={},
    )

    assert response.status_code == 422


async def test_update_project_link_rejects_duplicate_url(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    repository_link = cast(
        ProjectLink,
        admin_project_link_records["repository_link"],
    )
    documentation_link = cast(
        ProjectLink,
        admin_project_link_records["documentation_link"],
    )
    updater_user = cast(
        User,
        admin_project_link_records["updater_user"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        project_link_detail_url(
            project,
            documentation_link,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={
            "url": repository_link.url,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_link_conflict"


async def test_update_project_link_rejects_duplicate_label(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    documentation_link = cast(
        ProjectLink,
        admin_project_link_records["documentation_link"],
    )
    updater_user = cast(
        User,
        admin_project_link_records["updater_user"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        project_link_detail_url(
            project,
            documentation_link,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={
            "label": "SOURCE CODE",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_link_conflict"


async def test_update_project_link_rejects_user_without_update_permission(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    repository_link = cast(
        ProjectLink,
        admin_project_link_records["repository_link"],
    )
    reader_user = cast(
        User,
        admin_project_link_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.patch(
        project_link_detail_url(
            project,
            repository_link,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={
            "label": "Updated Source Code",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_update_project_link_rejects_cross_project_link(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    second_project_link = cast(
        ProjectLink,
        admin_project_link_records["second_project_link"],
    )
    updater_user = cast(
        User,
        admin_project_link_records["updater_user"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        f"{project_links_url(project)}/{second_project_link.id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "label": "Unauthorized Cross-Project Update",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "project_link_not_found"


async def test_update_project_link_status_succeeds(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    repository_link = cast(
        ProjectLink,
        admin_project_link_records["repository_link"],
    )
    updater_user = cast(
        User,
        admin_project_link_records["updater_user"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        f"{project_link_detail_url(project, repository_link)}/status",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "is_active": False,
            "reason": "Temporarily hiding the repository link.",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["is_active"] is False


async def test_delete_project_link_succeeds(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    documentation_link = cast(
        ProjectLink,
        admin_project_link_records["documentation_link"],
    )
    deleter_user = cast(
        User,
        admin_project_link_records["deleter_user"],
    )

    access_token = await login_user(
        client,
        email=deleter_user.email,
    )

    response = await client.request(
        "DELETE",
        project_link_detail_url(
            project,
            documentation_link,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={
            "reason": "The documentation resource is no longer available.",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["deleted_at"] is not None
    assert payload["is_active"] is False


async def test_delete_project_link_rejects_user_without_delete_permission(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    repository_link = cast(
        ProjectLink,
        admin_project_link_records["repository_link"],
    )
    updater_user = cast(
        User,
        admin_project_link_records["updater_user"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.request(
        "DELETE",
        project_link_detail_url(
            project,
            repository_link,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={},
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_restore_project_link_succeeds(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    deleted_link = cast(
        ProjectLink,
        admin_project_link_records["deleted_link"],
    )
    updater_user = cast(
        User,
        admin_project_link_records["updater_user"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.post(
        f"{project_link_detail_url(project, deleted_link)}/restore",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "activate": True,
            "reason": "The archived article is relevant again.",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["deleted_at"] is None
    assert payload["is_active"] is True


async def test_restore_project_link_can_remain_inactive(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    deleted_link = cast(
        ProjectLink,
        admin_project_link_records["deleted_link"],
    )
    updater_user = cast(
        User,
        admin_project_link_records["updater_user"],
    )

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.post(
        f"{project_link_detail_url(project, deleted_link)}/restore",
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


async def test_restore_project_link_rejects_duplicate_url_conflict(
    client: AsyncClient,
    database_session: AsyncSession,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    deleted_link = cast(
        ProjectLink,
        admin_project_link_records["deleted_link"],
    )
    updater_user = cast(
        User,
        admin_project_link_records["updater_user"],
    )

    conflicting_link = create_project_link(
        project=project,
        label="Current Archived Article",
        url=deleted_link.url,
        link_type="article",
        sort_order=60,
    )

    database_session.add(
        conflicting_link,
    )
    await database_session.flush()

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.post(
        f"{project_link_detail_url(project, deleted_link)}/restore",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "activate": True,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_link_conflict"


async def test_public_project_returns_only_active_non_deleted_links(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )

    response = await client.get(
        f"{PUBLIC_PROJECT_URL}/{project.slug}",
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    links = cast(
        list[dict[str, Any]],
        payload["links"],
    )

    assert [item["label"] for item in links] == [
        "Source Code",
        "Documentation",
    ]

    assert all(item["label"] != "Legacy Demo" for item in links)
    assert all(item["label"] != "Archived Article" for item in links)


async def test_public_project_links_follow_sort_order(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )

    response = await client.get(
        f"{PUBLIC_PROJECT_URL}/{project.slug}",
    )

    assert response.status_code == 200, response.text

    links = cast(
        list[dict[str, Any]],
        response.json()["links"],
    )

    assert [item["sort_order"] for item in links] == [
        10,
        20,
    ]


async def test_manager_can_complete_project_link_lifecycle(
    client: AsyncClient,
    admin_project_link_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_project_link_records["project"],
    )
    manager_user = cast(
        User,
        admin_project_link_records["manager_user"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    create_response = await client.post(
        project_links_url(project),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_project_link_payload(
            label="Video Walkthrough",
            url="https://video.example.com/secure-portfolio",
            link_type="video",
            icon="video",
            sort_order=70,
        ),
    )

    assert create_response.status_code == 201, create_response.text

    link_id = str(
        create_response.json()["id"],
    )

    update_response = await client.patch(
        f"{project_links_url(project)}/{link_id}",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "label": "Architecture Video Walkthrough",
            "url": "https://video.example.com/secure-portfolio-architecture",
            "sort_order": 5,
        },
    )

    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["label"] == "Architecture Video Walkthrough"
    assert update_response.json()["sort_order"] == 5

    status_response = await client.patch(
        f"{project_links_url(project)}/{link_id}/status",
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
        f"{project_links_url(project)}/{link_id}",
        headers=authorization_headers(
            access_token,
        ),
        json={},
    )

    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["deleted_at"] is not None
    assert delete_response.json()["is_active"] is False

    restore_response = await client.post(
        f"{project_links_url(project)}/{link_id}/restore",
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
