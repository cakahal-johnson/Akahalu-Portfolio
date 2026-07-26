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
from app.models.project_media import ProjectMedia
from app.models.role import Role
from app.models.user import User
from app.security.passwords import hash_password


TEST_PASSWORD = "StrongPortfolioMediaPassword123!"

ADMIN_PORTFOLIO_URL = "/api/v1/admin/portfolio"
ADMIN_PROJECT_MEDIA_URL = f"{ADMIN_PORTFOLIO_URL}/projects"
ADMIN_MEDIA_URL = f"{ADMIN_PORTFOLIO_URL}/media"

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


def create_project(
    *,
    title: str,
    slug: str,
    created_by: User,
    deleted_at: datetime | None = None,
) -> Project:
    return Project(
        title=title,
        slug=slug,
        short_description=(
            f"{title} is a professional portfolio project with managed media."
        ),
        description=(
            f"{title} demonstrates secure project-media administration, "
            "ordering, primary-image management, validation and restoration."
        ),
        status="draft",
        visibility="private",
        is_featured=False,
        sort_order=0,
        created_by=created_by,
        updated_by=created_by,
        deleted_at=deleted_at,
    )


def create_media(
    *,
    project: Project,
    url: str,
    media_type: str = "image",
    thumbnail_url: str | None = None,
    alt_text: str | None = None,
    caption: str | None = None,
    provider: str | None = None,
    provider_asset_id: str | None = None,
    mime_type: str | None = "image/webp",
    width: int | None = 1600,
    height: int | None = 900,
    duration_seconds: int | None = None,
    file_size_bytes: int | None = 250_000,
    is_primary: bool = False,
    sort_order: int = 0,
    deleted_at: datetime | None = None,
) -> ProjectMedia:
    return ProjectMedia(
        project=project,
        url=url,
        media_type=media_type,
        thumbnail_url=thumbnail_url,
        alt_text=alt_text,
        caption=caption,
        provider=provider,
        provider_asset_id=provider_asset_id,
        mime_type=mime_type,
        width=width,
        height=height,
        duration_seconds=duration_seconds,
        file_size_bytes=file_size_bytes,
        is_primary=is_primary,
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
            "device_name": "Portfolio media integration test",
        },
        headers={
            "User-Agent": "portfolio-media-integration-tests",
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


def project_media_collection_url(
    project_id: object,
) -> str:
    return f"{ADMIN_PROJECT_MEDIA_URL}/{project_id}/media"


def media_detail_url(
    media_id: object,
) -> str:
    return f"{ADMIN_MEDIA_URL}/{media_id}"


def valid_media_payload(
    *,
    url: str,
    provider_asset_id: str | None = None,
    is_primary: bool = False,
    sort_order: int = 0,
) -> dict[str, Any]:
    return {
        "url": url,
        "thumbnail_url": f"{url}?thumbnail=true",
        "media_type": "image",
        "alt_text": "Portfolio platform dashboard preview",
        "caption": "Administrative dashboard for the portfolio platform.",
        "provider": "cloudinary",
        "provider_asset_id": provider_asset_id,
        "mime_type": "image/webp",
        "width": 1600,
        "height": 900,
        "file_size_bytes": 250_000,
        "is_primary": is_primary,
        "sort_order": sort_order,
    }


@pytest_asyncio.fixture
async def admin_media_records(
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
        "portfolio_media_reader",
        permissions=[
            projects_read,
        ],
    )
    creator_role = create_role(
        "portfolio_media_creator",
        permissions=[
            projects_create,
        ],
    )
    updater_role = create_role(
        "portfolio_media_updater",
        permissions=[
            projects_update,
        ],
    )
    deleter_role = create_role(
        "portfolio_media_deleter",
        permissions=[
            projects_delete,
        ],
    )
    manager_role = create_role(
        "portfolio_media_manager",
        permissions=[
            projects_read,
            projects_create,
            projects_update,
            projects_delete,
        ],
    )
    outsider_role = create_role(
        "portfolio_media_outsider",
        permissions=[
            unrelated_permission,
        ],
    )

    reader_user = create_user(
        email="portfolio-media-reader@example.com",
        roles=[
            reader_role,
        ],
    )
    creator_user = create_user(
        email="portfolio-media-creator@example.com",
        roles=[
            creator_role,
        ],
    )
    updater_user = create_user(
        email="portfolio-media-updater@example.com",
        roles=[
            updater_role,
        ],
    )
    deleter_user = create_user(
        email="portfolio-media-deleter@example.com",
        roles=[
            deleter_role,
        ],
    )
    manager_user = create_user(
        email="portfolio-media-manager@example.com",
        roles=[
            manager_role,
        ],
    )
    outsider_user = create_user(
        email="portfolio-media-outsider@example.com",
        roles=[
            outsider_role,
        ],
    )
    superuser = create_user(
        email="portfolio-media-superuser@example.com",
        is_superuser=True,
    )

    primary_project = create_project(
        title="Portfolio Media Platform",
        slug="portfolio-media-platform",
        created_by=manager_user,
    )
    secondary_project = create_project(
        title="Secondary Media Project",
        slug="secondary-media-project",
        created_by=manager_user,
    )
    deleted_project = create_project(
        title="Deleted Media Project",
        slug="deleted-media-project",
        created_by=manager_user,
        deleted_at=datetime.now(UTC),
    )

    hero_media = create_media(
        project=primary_project,
        url="https://cdn.example.com/portfolio/hero.webp",
        thumbnail_url="https://cdn.example.com/portfolio/hero-thumb.webp",
        alt_text="Portfolio platform hero image",
        caption="Primary portfolio platform preview.",
        provider="cloudinary",
        provider_asset_id="portfolio/hero",
        is_primary=True,
        sort_order=1,
    )
    dashboard_media = create_media(
        project=primary_project,
        url="https://cdn.example.com/portfolio/dashboard.webp",
        thumbnail_url="https://cdn.example.com/portfolio/dashboard-thumb.webp",
        alt_text="Portfolio dashboard interface",
        caption="Secure project administration dashboard.",
        provider="cloudinary",
        provider_asset_id="portfolio/dashboard",
        is_primary=False,
        sort_order=2,
    )
    video_media = create_media(
        project=primary_project,
        url="https://cdn.example.com/portfolio/demo.mp4",
        media_type="video",
        thumbnail_url="https://cdn.example.com/portfolio/demo-thumb.webp",
        alt_text="Portfolio platform demonstration",
        caption="Portfolio application walkthrough.",
        provider="cloudinary",
        provider_asset_id="portfolio/demo",
        mime_type="video/mp4",
        width=1920,
        height=1080,
        duration_seconds=95,
        file_size_bytes=4_500_000,
        is_primary=False,
        sort_order=3,
    )
    deleted_media = create_media(
        project=primary_project,
        url="https://cdn.example.com/portfolio/legacy.webp",
        thumbnail_url="https://cdn.example.com/portfolio/legacy-thumb.webp",
        alt_text="Legacy portfolio preview",
        caption="Retired portfolio preview.",
        provider="cloudinary",
        provider_asset_id="portfolio/legacy",
        is_primary=False,
        sort_order=4,
        deleted_at=datetime.now(UTC),
    )
    secondary_media = create_media(
        project=secondary_project,
        url="https://cdn.example.com/secondary/hero.webp",
        thumbnail_url="https://cdn.example.com/secondary/hero-thumb.webp",
        alt_text="Secondary project preview",
        caption="Secondary portfolio project.",
        provider="cloudinary",
        provider_asset_id="secondary/hero",
        is_primary=True,
        sort_order=1,
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
            primary_project,
            secondary_project,
            deleted_project,
            hero_media,
            dashboard_media,
            video_media,
            deleted_media,
            secondary_media,
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
        "primary_project": primary_project,
        "secondary_project": secondary_project,
        "deleted_project": deleted_project,
        "hero_media": hero_media,
        "dashboard_media": dashboard_media,
        "video_media": video_media,
        "deleted_media": deleted_media,
        "secondary_media": secondary_media,
    }


async def test_list_media_rejects_unauthenticated_request(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    project = cast(
        Project,
        admin_media_records["primary_project"],
    )

    response = await client.get(
        project_media_collection_url(
            project.id,
        ),
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "invalid_authentication"


async def test_list_media_rejects_user_without_read_permission(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    outsider = cast(
        User,
        admin_media_records["outsider_user"],
    )
    project = cast(
        Project,
        admin_media_records["primary_project"],
    )

    access_token = await login_user(
        client,
        email=outsider.email,
    )

    response = await client.get(
        project_media_collection_url(
            project.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_list_media_returns_paginated_project_records(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_media_records["reader_user"],
    )
    project = cast(
        Project,
        admin_media_records["primary_project"],
    )

    access_token = await login_user(
        client,
        email=reader.email,
    )

    response = await client.get(
        project_media_collection_url(
            project.id,
        ),
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

    assert [item["sort_order"] for item in items] == [
        1,
        2,
    ]


@pytest.mark.parametrize(
    ("params", "expected_url"),
    [
        (
            {
                "search": "dashboard",
            },
            "https://cdn.example.com/portfolio/dashboard.webp",
        ),
        (
            {
                "media_type": "video",
            },
            "https://cdn.example.com/portfolio/demo.mp4",
        ),
        (
            {
                "is_primary": True,
            },
            "https://cdn.example.com/portfolio/hero.webp",
        ),
    ],
)
async def test_list_media_supports_filters(
    client: AsyncClient,
    admin_media_records: dict[str, object],
    params: dict[str, Any],
    expected_url: str,
) -> None:
    reader = cast(
        User,
        admin_media_records["reader_user"],
    )
    project = cast(
        Project,
        admin_media_records["primary_project"],
    )

    access_token = await login_user(
        client,
        email=reader.email,
    )

    response = await client.get(
        project_media_collection_url(
            project.id,
        ),
        params=params,
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json()["total_items"] == 1
    assert response.json()["items"][0]["url"] == expected_url


async def test_list_media_can_include_deleted_records(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_media_records["reader_user"],
    )
    project = cast(
        Project,
        admin_media_records["primary_project"],
    )

    access_token = await login_user(
        client,
        email=reader.email,
    )

    response = await client.get(
        project_media_collection_url(
            project.id,
        ),
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
    assert response.json()["total_items"] == 4

    deleted_item = next(
        item
        for item in response.json()["items"]
        if item["url"] == "https://cdn.example.com/portfolio/legacy.webp"
    )

    assert deleted_item["deleted_at"] is not None


async def test_list_media_returns_not_found_for_unknown_project(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_media_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader.email,
    )

    response = await client.get(
        project_media_collection_url(
            uuid4(),
        ),
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "project_not_found"


async def test_superuser_can_list_media_without_explicit_permission(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    superuser = cast(
        User,
        admin_media_records["superuser"],
    )
    project = cast(
        Project,
        admin_media_records["primary_project"],
    )

    access_token = await login_user(
        client,
        email=superuser.email,
    )

    response = await client.get(
        project_media_collection_url(
            project.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text


async def test_get_media_returns_media_detail(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_media_records["reader_user"],
    )
    media = cast(
        ProjectMedia,
        admin_media_records["hero_media"],
    )

    access_token = await login_user(
        client,
        email=reader.email,
    )

    response = await client.get(
        media_detail_url(
            media.id,
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

    assert payload["id"] == str(media.id)
    assert payload["project_id"] == str(media.project_id)
    assert payload["media_type"] == "image"
    assert payload["is_primary"] is True
    assert payload["deleted_at"] is None


async def test_get_deleted_media_requires_include_deleted(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_media_records["reader_user"],
    )
    deleted_media = cast(
        ProjectMedia,
        admin_media_records["deleted_media"],
    )

    access_token = await login_user(
        client,
        email=reader.email,
    )

    hidden_response = await client.get(
        media_detail_url(
            deleted_media.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
    )

    assert hidden_response.status_code == 404
    assert hidden_response.json()["detail"]["code"] == "project_media_not_found"

    visible_response = await client.get(
        media_detail_url(
            deleted_media.id,
        ),
        params={
            "include_deleted": True,
        },
        headers=authorization_headers(
            access_token,
        ),
    )

    assert visible_response.status_code == 200, visible_response.text
    assert visible_response.json()["deleted_at"] is not None


async def test_create_media_succeeds(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    creator = cast(
        User,
        admin_media_records["creator_user"],
    )
    project = cast(
        Project,
        admin_media_records["secondary_project"],
    )

    access_token = await login_user(
        client,
        email=creator.email,
    )

    response = await client.post(
        project_media_collection_url(
            project.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_media_payload(
            url="https://cdn.example.com/secondary/dashboard.webp",
            provider_asset_id="secondary/dashboard",
            sort_order=2,
        ),
    )

    assert response.status_code == 201, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["project_id"] == str(project.id)
    assert payload["url"] == ("https://cdn.example.com/secondary/dashboard.webp")
    assert payload["provider"] == "cloudinary"
    assert payload["provider_asset_id"] == "secondary/dashboard"
    assert payload["is_primary"] is False
    assert payload["deleted_at"] is None


async def test_create_primary_media_demotes_existing_primary(
    client: AsyncClient,
    database_session: AsyncSession,
    admin_media_records: dict[str, object],
) -> None:
    creator = cast(
        User,
        admin_media_records["creator_user"],
    )
    project = cast(
        Project,
        admin_media_records["primary_project"],
    )
    existing_primary = cast(
        ProjectMedia,
        admin_media_records["hero_media"],
    )

    access_token = await login_user(
        client,
        email=creator.email,
    )

    response = await client.post(
        project_media_collection_url(
            project.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_media_payload(
            url="https://cdn.example.com/portfolio/new-primary.webp",
            provider_asset_id="portfolio/new-primary",
            is_primary=True,
            sort_order=0,
        ),
    )

    assert response.status_code == 201, response.text
    assert response.json()["is_primary"] is True

    await database_session.refresh(
        existing_primary,
    )

    assert existing_primary.is_primary is False


async def test_create_media_rejects_duplicate_project_url(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    creator = cast(
        User,
        admin_media_records["creator_user"],
    )
    project = cast(
        Project,
        admin_media_records["primary_project"],
    )

    access_token = await login_user(
        client,
        email=creator.email,
    )

    response = await client.post(
        project_media_collection_url(
            project.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_media_payload(
            url="https://cdn.example.com/portfolio/hero.webp",
            provider_asset_id="portfolio/duplicate-url",
        ),
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_media_conflict"


async def test_create_media_rejects_duplicate_provider_asset(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    creator = cast(
        User,
        admin_media_records["creator_user"],
    )
    project = cast(
        Project,
        admin_media_records["secondary_project"],
    )

    access_token = await login_user(
        client,
        email=creator.email,
    )

    response = await client.post(
        project_media_collection_url(
            project.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_media_payload(
            url="https://cdn.example.com/secondary/duplicate-asset.webp",
            provider_asset_id="portfolio/hero",
        ),
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_media_conflict"


async def test_create_media_rejects_user_without_create_permission(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    reader = cast(
        User,
        admin_media_records["reader_user"],
    )
    project = cast(
        Project,
        admin_media_records["primary_project"],
    )

    access_token = await login_user(
        client,
        email=reader.email,
    )

    response = await client.post(
        project_media_collection_url(
            project.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_media_payload(
            url="https://cdn.example.com/portfolio/forbidden.webp",
            provider_asset_id="portfolio/forbidden",
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_update_media_succeeds(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    updater = cast(
        User,
        admin_media_records["updater_user"],
    )
    media = cast(
        ProjectMedia,
        admin_media_records["dashboard_media"],
    )

    access_token = await login_user(
        client,
        email=updater.email,
    )

    response = await client.patch(
        media_detail_url(
            media.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={
            "alt_text": "Updated secure portfolio dashboard",
            "caption": "Updated administration dashboard preview.",
            "sort_order": 10,
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["alt_text"] == ("Updated secure portfolio dashboard")
    assert response.json()["sort_order"] == 10


async def test_update_media_rejects_empty_payload(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    updater = cast(
        User,
        admin_media_records["updater_user"],
    )
    media = cast(
        ProjectMedia,
        admin_media_records["dashboard_media"],
    )

    access_token = await login_user(
        client,
        email=updater.email,
    )

    response = await client.patch(
        media_detail_url(
            media.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={},
    )

    assert response.status_code == 422


async def test_set_primary_media_demotes_previous_primary(
    client: AsyncClient,
    database_session: AsyncSession,
    admin_media_records: dict[str, object],
) -> None:
    updater = cast(
        User,
        admin_media_records["updater_user"],
    )
    old_primary = cast(
        ProjectMedia,
        admin_media_records["hero_media"],
    )
    new_primary = cast(
        ProjectMedia,
        admin_media_records["dashboard_media"],
    )

    access_token = await login_user(
        client,
        email=updater.email,
    )

    response = await client.patch(
        f"{media_detail_url(new_primary.id)}/primary",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "is_primary": True,
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["is_primary"] is True

    await database_session.refresh(
        old_primary,
    )

    assert old_primary.is_primary is False


async def test_delete_primary_media_assigns_replacement(
    client: AsyncClient,
    database_session: AsyncSession,
    admin_media_records: dict[str, object],
) -> None:
    deleter = cast(
        User,
        admin_media_records["deleter_user"],
    )
    primary_media = cast(
        ProjectMedia,
        admin_media_records["hero_media"],
    )
    replacement_media = cast(
        ProjectMedia,
        admin_media_records["dashboard_media"],
    )

    access_token = await login_user(
        client,
        email=deleter.email,
    )

    response = await client.request(
        "DELETE",
        media_detail_url(
            primary_media.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={
            "reason": "Replacing the outdated primary image.",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["deleted_at"] is not None
    assert response.json()["is_primary"] is False

    await database_session.refresh(
        replacement_media,
    )

    assert replacement_media.is_primary is True


async def test_delete_media_rejects_user_without_delete_permission(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    updater = cast(
        User,
        admin_media_records["updater_user"],
    )
    media = cast(
        ProjectMedia,
        admin_media_records["dashboard_media"],
    )

    access_token = await login_user(
        client,
        email=updater.email,
    )

    response = await client.request(
        "DELETE",
        media_detail_url(
            media.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={},
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_restore_deleted_media_succeeds(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    deleter = cast(
        User,
        admin_media_records["deleter_user"],
    )
    deleted_media = cast(
        ProjectMedia,
        admin_media_records["deleted_media"],
    )

    access_token = await login_user(
        client,
        email=deleter.email,
    )

    response = await client.post(
        f"{media_detail_url(deleted_media.id)}/restore",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "restore_as_primary": False,
            "reason": "The media record is required again.",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["deleted_at"] is None
    assert response.json()["is_primary"] is False


async def test_restore_media_can_become_primary(
    client: AsyncClient,
    database_session: AsyncSession,
    admin_media_records: dict[str, object],
) -> None:
    deleter = cast(
        User,
        admin_media_records["deleter_user"],
    )
    old_primary = cast(
        ProjectMedia,
        admin_media_records["hero_media"],
    )
    deleted_media = cast(
        ProjectMedia,
        admin_media_records["deleted_media"],
    )

    access_token = await login_user(
        client,
        email=deleter.email,
    )

    response = await client.post(
        f"{media_detail_url(deleted_media.id)}/restore",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "restore_as_primary": True,
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["deleted_at"] is None
    assert response.json()["is_primary"] is True

    await database_session.refresh(
        old_primary,
    )

    assert old_primary.is_primary is False


async def test_manager_can_complete_media_lifecycle(
    client: AsyncClient,
    admin_media_records: dict[str, object],
) -> None:
    manager = cast(
        User,
        admin_media_records["manager_user"],
    )
    project = cast(
        Project,
        admin_media_records["secondary_project"],
    )

    access_token = await login_user(
        client,
        email=manager.email,
    )

    create_response = await client.post(
        project_media_collection_url(
            project.id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json=valid_media_payload(
            url="https://cdn.example.com/lifecycle/original.webp",
            provider_asset_id="lifecycle/original",
            sort_order=5,
        ),
    )

    assert create_response.status_code == 201, create_response.text

    media_id = str(
        create_response.json()["id"],
    )

    update_response = await client.patch(
        media_detail_url(
            media_id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={
            "url": "https://cdn.example.com/lifecycle/updated.webp",
            "provider_asset_id": "lifecycle/updated",
            "caption": "Updated lifecycle media.",
            "sort_order": 6,
        },
    )

    assert update_response.status_code == 200, update_response.text

    primary_response = await client.patch(
        f"{media_detail_url(media_id)}/primary",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "is_primary": True,
        },
    )

    assert primary_response.status_code == 200, primary_response.text
    assert primary_response.json()["is_primary"] is True

    delete_response = await client.request(
        "DELETE",
        media_detail_url(
            media_id,
        ),
        headers=authorization_headers(
            access_token,
        ),
        json={
            "reason": "Testing the complete media lifecycle.",
        },
    )

    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["deleted_at"] is not None

    restore_response = await client.post(
        f"{media_detail_url(media_id)}/restore",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "restore_as_primary": False,
        },
    )

    assert restore_response.status_code == 200, restore_response.text
    assert restore_response.json()["deleted_at"] is None
    assert restore_response.json()["is_primary"] is False
