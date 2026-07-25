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
from app.models.project_associations import ProjectTechnologyAssociation
from app.models.project_category import ProjectCategory
from app.models.project_technology import ProjectTechnology
from app.models.role import Role
from app.models.user import User
from app.security.passwords import hash_password

TEST_PASSWORD = "StrongPortfolioProjectPassword123!"
ADMIN_PROJECT_URL = "/api/v1/admin/portfolio/projects"
PUBLIC_PROJECT_URL = "/api/v1/portfolio/projects"
pytestmark = pytest.mark.asyncio


def create_permission(code: str) -> Permission:
    return Permission(
        code=code,
        name=code.replace(".", " ").title(),
        description=f"Permission for {code}.",
        is_active=True,
    )


def create_role(name: str, *, permissions: list[Permission] | None = None) -> Role:
    return Role(
        name=name,
        display_name=name.replace("_", " ").title(),
        description=f"Role for {name}.",
        is_system=False,
        is_active=True,
        permissions=permissions or [],
    )


def create_user(
    *, email: str, roles: list[Role] | None = None, is_superuser: bool = False
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
    *, name: str, slug: str, is_active: bool = True, sort_order: int = 0
) -> ProjectCategory:
    return ProjectCategory(
        name=name,
        slug=slug,
        description=f"{name} portfolio projects.",
        icon="folder",
        color="#3366FF",
        is_active=is_active,
        sort_order=sort_order,
    )


def create_technology(
    *,
    name: str,
    slug: str,
    category: str = "other",
    is_active: bool = True,
    sort_order: int = 0,
) -> ProjectTechnology:
    return ProjectTechnology(
        name=name,
        slug=slug,
        description=f"{name} technology for portfolio projects.",
        category=category,
        icon=slug,
        color="#3366FF",
        is_active=is_active,
        sort_order=sort_order,
    )


def create_project(
    *,
    title: str,
    slug: str,
    category: ProjectCategory | None = None,
    status: str = "draft",
    visibility: str = "private",
    is_featured: bool = False,
    sort_order: int = 0,
    published_at: datetime | None = None,
    deleted_at: datetime | None = None,
    created_by: User | None = None,
) -> Project:
    return Project(
        title=title,
        slug=slug,
        short_description=f"{title} is a professional portfolio project with secure workflows.",
        description=f"{title} demonstrates production-ready architecture, tested APIs, database integration, authorization, and maintainable engineering.",
        category=category,
        status=status,
        visibility=visibility,
        is_featured=is_featured,
        sort_order=sort_order,
        published_at=published_at,
        deleted_at=deleted_at,
        created_by=created_by,
        updated_by=created_by,
    )


async def login_user(client: AsyncClient, *, email: str) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": TEST_PASSWORD,
            "device_name": "Portfolio project integration test",
        },
        headers={"User-Agent": "portfolio-project-integration-tests"},
    )
    assert response.status_code == 200, response.text
    payload = cast(dict[str, Any], response.json())
    return str(cast(dict[str, Any], payload["tokens"])["access_token"])


def authorization_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def valid_project_payload(
    *,
    slug: str,
    category_id: str | None = None,
    technology_ids: list[str] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": "  Secure   Portfolio Platform  ",
        "slug": f"  {slug.upper()}  ",
        "short_description": "A secure full-stack portfolio platform with tested administration.",
        "description": "A production-ready portfolio platform built with FastAPI, PostgreSQL, role-based access control, and comprehensive tests.",
        "problem_statement": "Portfolio content needed secure structured management.",
        "solution_summary": "A layered API with validated administrative workflows.",
        "key_features": "RBAC, publication workflow, filtering, and soft deletion.",
        "technical_highlights": "Async SQLAlchemy, Pydantic, PostgreSQL, and pytest.",
        "status": "draft",
        "visibility": "private",
        "is_featured": False,
        "sort_order": 10,
        "repository_url": "https://github.com/example/portfolio",
        "live_url": "https://portfolio.example.com",
        "seo_title": "Secure Portfolio Platform",
        "seo_description": "A secure and production-ready professional portfolio platform.",
    }
    if category_id is not None:
        payload["category_id"] = category_id
    if technology_ids is not None:
        payload["technology_assignments"] = [
            {
                "technology_id": technology_id,
                "is_featured": index == 0,
                "sort_order": index + 1,
            }
            for index, technology_id in enumerate(technology_ids)
        ]
    return payload


@pytest_asyncio.fixture
async def admin_project_records(
    database_session: AsyncSession,
) -> AsyncIterator[dict[str, object]]:
    projects_read = create_permission("projects.read")
    projects_create = create_permission("projects.create")
    projects_update = create_permission("projects.update")
    projects_delete = create_permission("projects.delete")
    unrelated_permission = create_permission("settings.manage")

    reader_role = create_role("portfolio_project_reader", permissions=[projects_read])
    creator_role = create_role(
        "portfolio_project_creator", permissions=[projects_create]
    )
    updater_role = create_role(
        "portfolio_project_updater", permissions=[projects_update]
    )
    deleter_role = create_role(
        "portfolio_project_deleter", permissions=[projects_delete]
    )
    manager_role = create_role(
        "portfolio_project_manager",
        permissions=[projects_read, projects_create, projects_update, projects_delete],
    )
    outsider_role = create_role(
        "portfolio_project_outsider", permissions=[unrelated_permission]
    )

    reader_user = create_user(
        email="portfolio-project-reader@example.com", roles=[reader_role]
    )
    creator_user = create_user(
        email="portfolio-project-creator@example.com", roles=[creator_role]
    )
    updater_user = create_user(
        email="portfolio-project-updater@example.com", roles=[updater_role]
    )
    deleter_user = create_user(
        email="portfolio-project-deleter@example.com", roles=[deleter_role]
    )
    manager_user = create_user(
        email="portfolio-project-manager@example.com", roles=[manager_role]
    )
    outsider_user = create_user(
        email="portfolio-project-outsider@example.com", roles=[outsider_role]
    )
    superuser = create_user(
        email="portfolio-project-superuser@example.com", is_superuser=True
    )

    web_category = create_category(
        name="Web Applications", slug="web-applications", sort_order=1
    )
    mobile_category = create_category(
        name="Mobile Applications", slug="mobile-applications", sort_order=2
    )
    inactive_category = create_category(
        name="Legacy Projects", slug="legacy-projects", is_active=False, sort_order=3
    )

    python_technology = create_technology(
        name="Python", slug="python", category="language", sort_order=1
    )
    fastapi_technology = create_technology(
        name="FastAPI", slug="fastapi", category="framework", sort_order=2
    )
    inactive_technology = create_technology(
        name="Legacy Toolkit",
        slug="legacy-toolkit",
        category="tool",
        is_active=False,
        sort_order=3,
    )

    published_at = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    draft_project = create_project(
        title="Draft Portfolio API",
        slug="draft-portfolio-api",
        category=web_category,
        sort_order=1,
        created_by=manager_user,
    )
    public_project = create_project(
        title="Public Portfolio Platform",
        slug="public-portfolio-platform",
        category=web_category,
        status="published",
        visibility="public",
        is_featured=True,
        sort_order=2,
        published_at=published_at,
        created_by=manager_user,
    )
    archived_project = create_project(
        title="Archived Mobile Application",
        slug="archived-mobile-application",
        category=mobile_category,
        status="archived",
        visibility="private",
        sort_order=3,
        created_by=manager_user,
    )
    deleted_project = create_project(
        title="Deleted Portfolio Project",
        slug="deleted-portfolio-project",
        category=web_category,
        status="archived",
        visibility="private",
        sort_order=4,
        deleted_at=datetime.now(UTC),
        created_by=manager_user,
    )

    draft_python = ProjectTechnologyAssociation(
        project=draft_project,
        technology=python_technology,
        is_featured=True,
        sort_order=1,
    )
    public_python = ProjectTechnologyAssociation(
        project=public_project,
        technology=python_technology,
        is_featured=True,
        sort_order=1,
    )
    public_fastapi = ProjectTechnologyAssociation(
        project=public_project,
        technology=fastapi_technology,
        is_featured=False,
        sort_order=2,
    )
    deleted_python = ProjectTechnologyAssociation(
        project=deleted_project,
        technology=python_technology,
        is_featured=True,
        sort_order=1,
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
            outsider_role,
            reader_user,
            creator_user,
            updater_user,
            deleter_user,
            manager_user,
            outsider_user,
            superuser,
            web_category,
            mobile_category,
            inactive_category,
            python_technology,
            fastapi_technology,
            inactive_technology,
            draft_project,
            public_project,
            archived_project,
            deleted_project,
            draft_python,
            public_python,
            public_fastapi,
            deleted_python,
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
        "inactive_category": inactive_category,
        "python_technology": python_technology,
        "fastapi_technology": fastapi_technology,
        "inactive_technology": inactive_technology,
        "draft_project": draft_project,
        "public_project": public_project,
        "archived_project": archived_project,
        "deleted_project": deleted_project,
        "deleted_python": deleted_python,
    }


async def test_list_projects_rejects_unauthenticated_request(
    client: AsyncClient,
) -> None:
    response = await client.get(ADMIN_PROJECT_URL)
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "invalid_authentication"


async def test_list_projects_rejects_user_without_read_permission(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    outsider = cast(User, admin_project_records["outsider_user"])
    token = await login_user(client, email=outsider.email)
    response = await client.get(ADMIN_PROJECT_URL, headers=authorization_headers(token))
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_list_projects_returns_paginated_results(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    reader = cast(User, admin_project_records["reader_user"])
    token = await login_user(client, email=reader.email)
    response = await client.get(
        ADMIN_PROJECT_URL,
        params={
            "page": 1,
            "page_size": 2,
            "sort_by": "sort_order",
            "sort_direction": "asc",
        },
        headers=authorization_headers(token),
    )
    assert response.status_code == 200, response.text
    payload = cast(dict[str, Any], response.json())
    assert payload["total_items"] == 3
    assert payload["total_pages"] == 2
    assert [item["slug"] for item in payload["items"]] == [
        "draft-portfolio-api",
        "public-portfolio-platform",
    ]


@pytest.mark.parametrize(
    ("params", "expected_slug"),
    [
        ({"search": "Public Portfolio"}, "public-portfolio-platform"),
        ({"project_status": "archived"}, "archived-mobile-application"),
        ({"visibility": "public"}, "public-portfolio-platform"),
        ({"is_featured": True}, "public-portfolio-platform"),
    ],
)
async def test_list_projects_supports_common_filters(
    client: AsyncClient,
    admin_project_records: dict[str, object],
    params: dict[str, Any],
    expected_slug: str,
) -> None:
    reader = cast(User, admin_project_records["reader_user"])
    token = await login_user(client, email=reader.email)
    response = await client.get(
        ADMIN_PROJECT_URL, params=params, headers=authorization_headers(token)
    )
    assert response.status_code == 200, response.text
    assert response.json()["total_items"] == 1
    assert response.json()["items"][0]["slug"] == expected_slug


async def test_list_projects_supports_category_and_technology_filters(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    reader = cast(User, admin_project_records["reader_user"])
    mobile = cast(ProjectCategory, admin_project_records["mobile_category"])
    python = cast(ProjectTechnology, admin_project_records["python_technology"])
    token = await login_user(client, email=reader.email)
    category_response = await client.get(
        ADMIN_PROJECT_URL,
        params={"category_id": str(mobile.id)},
        headers=authorization_headers(token),
    )
    technology_response = await client.get(
        ADMIN_PROJECT_URL,
        params={"technology_id": str(python.id)},
        headers=authorization_headers(token),
    )
    assert category_response.status_code == 200, category_response.text
    assert technology_response.status_code == 200, technology_response.text
    assert category_response.json()["items"][0]["slug"] == "archived-mobile-application"
    assert {item["slug"] for item in technology_response.json()["items"]} == {
        "draft-portfolio-api",
        "public-portfolio-platform",
    }


async def test_list_projects_can_include_deleted_records(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    reader = cast(User, admin_project_records["reader_user"])
    token = await login_user(client, email=reader.email)
    response = await client.get(
        ADMIN_PROJECT_URL,
        params={"include_deleted": True},
        headers=authorization_headers(token),
    )
    assert response.status_code == 200, response.text
    assert response.json()["total_items"] == 4


async def test_superuser_can_list_projects_without_explicit_permission(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    superuser = cast(User, admin_project_records["superuser"])
    token = await login_user(client, email=superuser.email)
    response = await client.get(ADMIN_PROJECT_URL, headers=authorization_headers(token))
    assert response.status_code == 200, response.text


async def test_get_project_returns_related_category_and_technologies(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    reader = cast(User, admin_project_records["reader_user"])
    project = cast(Project, admin_project_records["public_project"])
    token = await login_user(client, email=reader.email)
    response = await client.get(
        f"{ADMIN_PROJECT_URL}/{project.id}", headers=authorization_headers(token)
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["category"]["slug"] == "web-applications"
    assert [
        item["technology"]["slug"] for item in payload["technology_assignments"]
    ] == ["python", "fastapi"]


async def test_get_project_returns_not_found_for_unknown_id(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    reader = cast(User, admin_project_records["reader_user"])
    token = await login_user(client, email=reader.email)
    response = await client.get(
        f"{ADMIN_PROJECT_URL}/{uuid4()}", headers=authorization_headers(token)
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "project_not_found"


async def test_create_project_succeeds_with_technology_assignments(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    creator = cast(User, admin_project_records["creator_user"])
    category = cast(ProjectCategory, admin_project_records["web_category"])
    python = cast(ProjectTechnology, admin_project_records["python_technology"])
    fastapi = cast(ProjectTechnology, admin_project_records["fastapi_technology"])
    token = await login_user(client, email=creator.email)
    response = await client.post(
        ADMIN_PROJECT_URL,
        headers=authorization_headers(token),
        json=valid_project_payload(
            slug="secure-portfolio-platform",
            category_id=str(category.id),
            technology_ids=[str(python.id), str(fastapi.id)],
        ),
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["title"] == "Secure Portfolio Platform"
    assert payload["slug"] == "secure-portfolio-platform"
    assert [
        item["technology"]["slug"] for item in payload["technology_assignments"]
    ] == ["python", "fastapi"]


async def test_create_project_rejects_duplicate_slug(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    creator = cast(User, admin_project_records["creator_user"])
    category = cast(ProjectCategory, admin_project_records["web_category"])
    token = await login_user(client, email=creator.email)
    response = await client.post(
        ADMIN_PROJECT_URL,
        headers=authorization_headers(token),
        json=valid_project_payload(
            slug="PUBLIC-PORTFOLIO-PLATFORM", category_id=str(category.id)
        ),
    )
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_conflict"


async def test_create_project_rejects_unknown_and_inactive_relations(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    creator = cast(User, admin_project_records["creator_user"])
    inactive_category = cast(
        ProjectCategory, admin_project_records["inactive_category"]
    )
    inactive_technology = cast(
        ProjectTechnology, admin_project_records["inactive_technology"]
    )
    active_category = cast(ProjectCategory, admin_project_records["web_category"])
    token = await login_user(client, email=creator.email)
    unknown_category = await client.post(
        ADMIN_PROJECT_URL,
        headers=authorization_headers(token),
        json=valid_project_payload(slug="unknown-category", category_id=str(uuid4())),
    )
    inactive_category_response = await client.post(
        ADMIN_PROJECT_URL,
        headers=authorization_headers(token),
        json=valid_project_payload(
            slug="inactive-category", category_id=str(inactive_category.id)
        ),
    )
    unknown_technology = await client.post(
        ADMIN_PROJECT_URL,
        headers=authorization_headers(token),
        json=valid_project_payload(
            slug="unknown-technology",
            category_id=str(active_category.id),
            technology_ids=[str(uuid4())],
        ),
    )
    inactive_technology_response = await client.post(
        ADMIN_PROJECT_URL,
        headers=authorization_headers(token),
        json=valid_project_payload(
            slug="inactive-technology",
            category_id=str(active_category.id),
            technology_ids=[str(inactive_technology.id)],
        ),
    )
    assert unknown_category.status_code == 404
    assert unknown_category.json()["detail"]["code"] == "project_category_not_found"
    assert inactive_category_response.status_code == 409
    assert (
        inactive_category_response.json()["detail"]["code"]
        == "project_category_unavailable"
    )
    assert unknown_technology.status_code == 404
    assert unknown_technology.json()["detail"]["code"] == "project_technology_not_found"
    assert inactive_technology_response.status_code == 409
    assert (
        inactive_technology_response.json()["detail"]["code"]
        == "project_technology_unavailable"
    )


async def test_update_project_replaces_category_and_technologies(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    updater = cast(User, admin_project_records["updater_user"])
    project = cast(Project, admin_project_records["draft_project"])
    category = cast(ProjectCategory, admin_project_records["mobile_category"])
    fastapi = cast(ProjectTechnology, admin_project_records["fastapi_technology"])
    token = await login_user(client, email=updater.email)
    response = await client.patch(
        f"{ADMIN_PROJECT_URL}/{project.id}",
        headers=authorization_headers(token),
        json={
            "title": "  Updated   Portfolio API  ",
            "slug": "  UPDATED-PORTFOLIO-API  ",
            "category_id": str(category.id),
            "technology_assignments": [
                {"technology_id": str(fastapi.id), "is_featured": True, "sort_order": 1}
            ],
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["title"] == "Updated Portfolio API"
    assert payload["slug"] == "updated-portfolio-api"
    assert payload["category"]["slug"] == "mobile-applications"
    assert [
        item["technology"]["slug"] for item in payload["technology_assignments"]
    ] == ["fastapi"]


async def test_update_project_rejects_empty_payload(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    updater = cast(User, admin_project_records["updater_user"])
    project = cast(Project, admin_project_records["draft_project"])
    token = await login_user(client, email=updater.email)
    response = await client.patch(
        f"{ADMIN_PROJECT_URL}/{project.id}",
        headers=authorization_headers(token),
        json={},
    )
    assert response.status_code == 422


async def test_publish_project_requires_category(
    client: AsyncClient,
    database_session: AsyncSession,
    admin_project_records: dict[str, object],
) -> None:
    updater = cast(User, admin_project_records["updater_user"])
    project = create_project(
        title="Uncategorized Project", slug="uncategorized-project", created_by=updater
    )
    database_session.add(project)
    await database_session.flush()
    token = await login_user(client, email=updater.email)
    response = await client.patch(
        f"{ADMIN_PROJECT_URL}/{project.id}/status",
        headers=authorization_headers(token),
        json={"status": "published", "published_at": datetime.now(UTC).isoformat()},
    )
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_publication_error"


async def test_status_visibility_and_featured_workflow(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    updater = cast(User, admin_project_records["updater_user"])
    project = cast(Project, admin_project_records["draft_project"])
    token = await login_user(client, email=updater.email)
    publish = await client.patch(
        f"{ADMIN_PROJECT_URL}/{project.id}/status",
        headers=authorization_headers(token),
        json={"status": "published", "published_at": datetime.now(UTC).isoformat()},
    )
    feature = await client.patch(
        f"{ADMIN_PROJECT_URL}/{project.id}/featured",
        headers=authorization_headers(token),
        json={"is_featured": True},
    )
    unlist = await client.patch(
        f"{ADMIN_PROJECT_URL}/{project.id}/visibility",
        headers=authorization_headers(token),
        json={"visibility": "unlisted"},
    )
    archive = await client.patch(
        f"{ADMIN_PROJECT_URL}/{project.id}/status",
        headers=authorization_headers(token),
        json={"status": "archived"},
    )
    assert publish.status_code == 200, publish.text
    assert publish.json()["visibility"] == "public"
    assert feature.status_code == 200, feature.text
    assert feature.json()["is_featured"] is True
    assert unlist.status_code == 200, unlist.text
    assert unlist.json()["visibility"] == "unlisted"
    assert archive.status_code == 200, archive.text
    assert archive.json()["status"] == "archived"
    assert archive.json()["visibility"] == "private"
    assert archive.json()["is_featured"] is False


async def test_feature_draft_project_is_rejected(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    updater = cast(User, admin_project_records["updater_user"])
    project = cast(Project, admin_project_records["draft_project"])
    token = await login_user(client, email=updater.email)
    response = await client.patch(
        f"{ADMIN_PROJECT_URL}/{project.id}/featured",
        headers=authorization_headers(token),
        json={"is_featured": True},
    )
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_publication_error"


async def test_delete_project_soft_deletes_project_and_associations(
    client: AsyncClient,
    database_session: AsyncSession,
    admin_project_records: dict[str, object],
) -> None:
    deleter = cast(User, admin_project_records["deleter_user"])
    project = cast(Project, admin_project_records["draft_project"])
    token = await login_user(client, email=deleter.email)
    response = await client.request(
        "DELETE",
        f"{ADMIN_PROJECT_URL}/{project.id}",
        headers=authorization_headers(token),
        json={"reason": "Project retired."},
    )
    assert response.status_code == 200, response.text
    assert response.json()["deleted_at"] is not None
    await database_session.refresh(project)
    assert all(item.deleted_at is not None for item in project.technology_associations)


async def test_restore_project_restores_active_technology_associations(
    client: AsyncClient,
    database_session: AsyncSession,
    admin_project_records: dict[str, object],
) -> None:
    updater = cast(User, admin_project_records["updater_user"])
    project = cast(Project, admin_project_records["deleted_project"])
    association = cast(
        ProjectTechnologyAssociation, admin_project_records["deleted_python"]
    )
    token = await login_user(client, email=updater.email)
    response = await client.post(
        f"{ADMIN_PROJECT_URL}/{project.id}/restore",
        headers=authorization_headers(token),
        json={"status": "draft", "visibility": "private"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["deleted_at"] is None
    assert payload["status"] == "draft"
    assert [
        item["technology"]["slug"] for item in payload["technology_assignments"]
    ] == ["python"]
    await database_session.refresh(association)
    assert association.deleted_at is None


async def test_restore_project_rejects_direct_published_state(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    updater = cast(User, admin_project_records["updater_user"])
    project = cast(Project, admin_project_records["deleted_project"])
    token = await login_user(client, email=updater.email)
    response = await client.post(
        f"{ADMIN_PROJECT_URL}/{project.id}/restore",
        headers=authorization_headers(token),
        json={"status": "published", "visibility": "public"},
    )
    assert response.status_code == 422


async def test_public_projects_only_return_published_public_records(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    response = await client.get(PUBLIC_PROJECT_URL)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total_items"] == 1
    assert payload["items"][0]["slug"] == "public-portfolio-platform"
    assert [item["slug"] for item in payload["items"][0]["technologies"]] == [
        "python",
        "fastapi",
    ]


async def test_public_project_detail_and_featured_endpoints(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    detail = await client.get(f"{PUBLIC_PROJECT_URL}/public-portfolio-platform")
    featured = await client.get(f"{PUBLIC_PROJECT_URL}/featured")
    assert detail.status_code == 200, detail.text
    assert [item["slug"] for item in detail.json()["technologies"]] == [
        "python",
        "fastapi",
    ]
    assert featured.status_code == 200, featured.text
    assert [item["slug"] for item in featured.json()] == ["public-portfolio-platform"]


@pytest.mark.parametrize(
    "slug",
    ["draft-portfolio-api", "archived-mobile-application", "deleted-portfolio-project"],
)
async def test_public_project_detail_hides_non_public_projects(
    client: AsyncClient, admin_project_records: dict[str, object], slug: str
) -> None:
    response = await client.get(f"{PUBLIC_PROJECT_URL}/{slug}")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "project_not_found"


async def test_manager_can_complete_project_lifecycle(
    client: AsyncClient, admin_project_records: dict[str, object]
) -> None:
    manager = cast(User, admin_project_records["manager_user"])
    category = cast(ProjectCategory, admin_project_records["web_category"])
    python = cast(ProjectTechnology, admin_project_records["python_technology"])
    fastapi = cast(ProjectTechnology, admin_project_records["fastapi_technology"])
    token = await login_user(client, email=manager.email)
    create_response = await client.post(
        ADMIN_PROJECT_URL,
        headers=authorization_headers(token),
        json=valid_project_payload(
            slug="manager-lifecycle-project",
            category_id=str(category.id),
            technology_ids=[str(python.id), str(fastapi.id)],
        ),
    )
    assert create_response.status_code == 201, create_response.text
    project_id = str(create_response.json()["id"])
    publish_response = await client.patch(
        f"{ADMIN_PROJECT_URL}/{project_id}/status",
        headers=authorization_headers(token),
        json={"status": "published", "published_at": datetime.now(UTC).isoformat()},
    )
    feature_response = await client.patch(
        f"{ADMIN_PROJECT_URL}/{project_id}/featured",
        headers=authorization_headers(token),
        json={"is_featured": True},
    )
    public_response = await client.get(
        f"{PUBLIC_PROJECT_URL}/manager-lifecycle-project"
    )
    delete_response = await client.request(
        "DELETE",
        f"{ADMIN_PROJECT_URL}/{project_id}",
        headers=authorization_headers(token),
        json={},
    )
    hidden_response = await client.get(
        f"{PUBLIC_PROJECT_URL}/manager-lifecycle-project"
    )
    restore_response = await client.post(
        f"{ADMIN_PROJECT_URL}/{project_id}/restore",
        headers=authorization_headers(token),
        json={},
    )
    assert publish_response.status_code == 200, publish_response.text
    assert feature_response.status_code == 200, feature_response.text
    assert public_response.status_code == 200, public_response.text
    assert delete_response.status_code == 200, delete_response.text
    assert hidden_response.status_code == 404
    assert restore_response.status_code == 200, restore_response.text
    assert restore_response.json()["status"] == "draft"
    assert [
        item["technology"]["slug"]
        for item in restore_response.json()["technology_assignments"]
    ] == ["python", "fastapi"]
