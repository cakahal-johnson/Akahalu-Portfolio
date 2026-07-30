from collections.abc import AsyncIterator
from datetime import UTC, date, datetime
from typing import Any, cast
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.experience import Experience
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.security.passwords import hash_password


TEST_PASSWORD = "StrongPortfolioExperiencePassword123!"
ADMIN_URL = "/api/v1/admin/portfolio/experiences"
PUBLIC_URL = "/api/v1/portfolio/experiences"

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


def create_experience(
    *,
    company_name: str,
    job_title: str,
    slug: str,
    employment_type: str = "full_time",
    location: str | None = "Regina, Saskatchewan",
    location_type: str = "onsite",
    start_date_value: date = date(2024, 1, 1),
    end_date: date | None = None,
    is_current: bool = False,
    summary: str | None = None,
    responsibilities: str | None = None,
    achievements: str | None = None,
    sort_order: int = 0,
    is_featured: bool = False,
    is_public: bool = False,
    deleted_at: datetime | None = None,
) -> Experience:
    return Experience(
        company_name=company_name,
        job_title=job_title,
        slug=slug,
        employment_type=employment_type,
        location=location,
        location_type=location_type,
        start_date=start_date_value,
        end_date=end_date,
        is_current=is_current,
        summary=(
            summary
            or f"Delivered secure and maintainable software solutions for {company_name}."
        ),
        responsibilities=responsibilities,
        achievements=achievements,
        sort_order=sort_order,
        is_featured=is_featured,
        is_public=is_public,
        deleted_at=deleted_at,
    )


async def login_user(client: AsyncClient, *, email: str) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": TEST_PASSWORD,
            "device_name": "Portfolio experience integration test",
        },
        headers={"User-Agent": "portfolio-experience-integration-tests"},
    )
    assert response.status_code == 200, response.text

    payload = cast(dict[str, Any], response.json())
    tokens = cast(dict[str, Any], payload["tokens"])
    return str(tokens["access_token"])


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def experience_records(
    database_session: AsyncSession,
) -> AsyncIterator[dict[str, object]]:
    read = create_permission("experience.read")
    create = create_permission("experience.create")
    update = create_permission("experience.update")
    delete = create_permission("experience.delete")
    unrelated = create_permission("settings.manage")

    reader = create_user(
        email="experience-reader@example.com",
        roles=[create_role("experience_reader", permissions=[read])],
    )
    creator = create_user(
        email="experience-creator@example.com",
        roles=[create_role("experience_creator", permissions=[create])],
    )
    updater = create_user(
        email="experience-updater@example.com",
        roles=[create_role("experience_updater", permissions=[update])],
    )
    deleter = create_user(
        email="experience-deleter@example.com",
        roles=[create_role("experience_deleter", permissions=[delete])],
    )
    manager = create_user(
        email="experience-manager@example.com",
        roles=[
            create_role(
                "experience_manager",
                permissions=[read, create, update, delete],
            )
        ],
    )
    outsider = create_user(
        email="experience-outsider@example.com",
        roles=[create_role("experience_outsider", permissions=[unrelated])],
    )
    superuser = create_user(
        email="experience-superuser@example.com",
        is_superuser=True,
    )

    current_public = create_experience(
        company_name="ZaraDera Ltd",
        job_title="Backend Software Developer",
        slug="zaradera-backend-developer",
        employment_type="full_time",
        location="London, United Kingdom",
        location_type="remote",
        start_date_value=date(2025, 1, 1),
        is_current=True,
        summary=(
            "Built secure backend services for a cleaning and facilities "
            "management platform."
        ),
        responsibilities="Designed APIs, authentication, and database workflows.",
        achievements="Implemented production-oriented lifecycle controls.",
        sort_order=1,
        is_featured=True,
        is_public=True,
    )
    completed_public = create_experience(
        company_name="Akahalu Digital",
        job_title="Full Stack Developer",
        slug="akahalu-full-stack-developer",
        employment_type="contract",
        location="Enugu, Nigeria",
        location_type="hybrid",
        start_date_value=date(2023, 1, 1),
        end_date=date(2024, 12, 31),
        summary="Delivered full-stack web applications and administrative systems.",
        responsibilities="Built responsive interfaces and secure backend services.",
        achievements="Improved reliability through automated tests.",
        sort_order=2,
        is_public=True,
    )
    private = create_experience(
        company_name="Private Consulting",
        job_title="Software Consultant",
        slug="private-software-consultant",
        employment_type="freelance",
        location_type="remote",
        start_date_value=date(2022, 5, 1),
        end_date=date(2022, 12, 31),
        summary="Provided private software consulting and maintenance services.",
        sort_order=3,
    )
    deleted = create_experience(
        company_name="Legacy Systems Ltd",
        job_title="Junior Developer",
        slug="legacy-junior-developer",
        employment_type="internship",
        location="Abuja, Nigeria",
        start_date_value=date(2021, 1, 1),
        end_date=date(2021, 6, 30),
        summary="Supported legacy application maintenance and internal tooling.",
        sort_order=4,
        deleted_at=datetime.now(UTC),
    )

    database_session.add_all(
        [
            reader,
            creator,
            updater,
            deleter,
            manager,
            outsider,
            superuser,
            current_public,
            completed_public,
            private,
            deleted,
        ]
    )
    await database_session.flush()

    yield {
        "reader": reader,
        "creator": creator,
        "updater": updater,
        "deleter": deleter,
        "manager": manager,
        "outsider": outsider,
        "superuser": superuser,
        "current_public": current_public,
        "completed_public": completed_public,
        "private": private,
        "deleted": deleted,
    }


async def test_admin_list_requires_authentication(client: AsyncClient) -> None:
    response = await client.get(ADMIN_URL)
    assert response.status_code == 401


async def test_admin_list_requires_read_permission(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["outsider"])
    token = await login_user(client, email=user.email)

    response = await client.get(ADMIN_URL, headers=auth_headers(token))

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "insufficient_permissions"


async def test_admin_list_paginates_sorts_and_excludes_deleted(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["reader"])
    token = await login_user(client, email=user.email)

    response = await client.get(
        ADMIN_URL,
        params={
            "page": 1,
            "page_size": 2,
            "sort_by": "sort_order",
            "sort_direction": "asc",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total_items"] == 3
    assert payload["total_pages"] == 2
    assert payload["has_next_page"] is True
    assert [item["slug"] for item in payload["items"]] == [
        "zaradera-backend-developer",
        "akahalu-full-stack-developer",
    ]


async def test_admin_list_supports_search_filters_and_deleted_visibility(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["reader"])
    token = await login_user(client, email=user.email)
    headers = auth_headers(token)

    filtered = await client.get(
        ADMIN_URL,
        params={
            "search": "cleaning",
            "employment_type": "full_time",
            "location_type": "remote",
            "is_current": True,
            "is_public": True,
            "is_featured": True,
        },
        headers=headers,
    )
    included = await client.get(
        ADMIN_URL,
        params={"include_deleted": True},
        headers=headers,
    )

    assert filtered.status_code == 200, filtered.text
    assert filtered.json()["total_items"] == 1
    assert filtered.json()["items"][0]["slug"] == "zaradera-backend-developer"
    assert included.status_code == 200, included.text
    assert included.json()["total_items"] == 4


async def test_superuser_bypasses_experience_permissions(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["superuser"])
    token = await login_user(client, email=user.email)

    response = await client.get(ADMIN_URL, headers=auth_headers(token))

    assert response.status_code == 200, response.text
    assert response.json()["total_items"] == 3


async def test_admin_detail_handles_deleted_and_unknown_records(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["reader"])
    deleted = cast(Experience, experience_records["deleted"])
    token = await login_user(client, email=user.email)
    headers = auth_headers(token)

    hidden = await client.get(f"{ADMIN_URL}/{deleted.id}", headers=headers)
    visible = await client.get(
        f"{ADMIN_URL}/{deleted.id}",
        params={"include_deleted": True},
        headers=headers,
    )
    unknown = await client.get(f"{ADMIN_URL}/{uuid4()}", headers=headers)

    assert hidden.status_code == 404
    assert hidden.json()["detail"]["code"] == "experience_not_found"
    assert visible.status_code == 200, visible.text
    assert visible.json()["deleted_at"] is not None
    assert unknown.status_code == 404


async def test_create_experience_normalizes_fields_and_sets_audit_ids(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["creator"])
    token = await login_user(client, email=user.email)

    response = await client.post(
        ADMIN_URL,
        headers=auth_headers(token),
        json={
            "company_name": "  Akahalu   Portfolio  ",
            "job_title": "  Senior   Backend Developer  ",
            "slug": "  AKAHALU-SENIOR-BACKEND  ",
            "employment_type": "CONTRACT",
            "location": "  Regina,   Saskatchewan  ",
            "location_type": "REMOTE",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "summary": "  Built secure APIs for a professional portfolio platform.  ",
            "company_website": " https://example.org ",
            "company_logo_url": " https://example.org/logo.png ",
            "sort_order": 5,
            "is_public": True,
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["company_name"] == "Akahalu Portfolio"
    assert payload["job_title"] == "Senior Backend Developer"
    assert payload["slug"] == "akahalu-senior-backend"
    assert payload["employment_type"] == "contract"
    assert payload["location"] == "Regina, Saskatchewan"
    assert payload["location_type"] == "remote"
    assert payload["created_by_id"] == str(user.id)
    assert payload["updated_by_id"] == str(user.id)


async def test_create_requires_create_permission(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["reader"])
    token = await login_user(client, email=user.email)

    response = await client.post(
        ADMIN_URL,
        headers=auth_headers(token),
        json={
            "company_name": "Unauthorized Ltd",
            "job_title": "Developer",
            "slug": "unauthorized-developer",
            "start_date": "2026-01-01",
            "summary": "This request should be rejected by authorization.",
        },
    )

    assert response.status_code == 403


async def test_create_rejects_duplicate_slug(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["creator"])
    token = await login_user(client, email=user.email)

    response = await client.post(
        ADMIN_URL,
        headers=auth_headers(token),
        json={
            "company_name": "Duplicate Ltd",
            "job_title": "Developer",
            "slug": "ZARADERA-BACKEND-DEVELOPER",
            "start_date": "2026-01-01",
            "summary": "This record intentionally duplicates an existing slug.",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "experience_conflict"


@pytest.mark.parametrize(
    "payload",
    [
        {
            "company_name": "Invalid Dates Ltd",
            "job_title": "Developer",
            "slug": "invalid-date-range",
            "start_date": "2026-06-01",
            "end_date": "2026-05-01",
            "summary": "This experience has an invalid chronological date range.",
        },
        {
            "company_name": "Invalid Current Ltd",
            "job_title": "Developer",
            "slug": "invalid-current-end-date",
            "start_date": "2026-01-01",
            "end_date": "2026-05-01",
            "is_current": True,
            "summary": "This current experience incorrectly includes an end date.",
        },
    ],
)
async def test_create_rejects_invalid_dates(
    client: AsyncClient,
    experience_records: dict[str, object],
    payload: dict[str, object],
) -> None:
    user = cast(User, experience_records["creator"])
    token = await login_user(client, email=user.email)

    response = await client.post(
        ADMIN_URL,
        headers=auth_headers(token),
        json=payload,
    )

    assert response.status_code == 422, response.text


async def test_create_rejects_private_featured_record(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["creator"])
    token = await login_user(client, email=user.email)

    response = await client.post(
        ADMIN_URL,
        headers=auth_headers(token),
        json={
            "company_name": "Invalid Featured Ltd",
            "job_title": "Developer",
            "slug": "invalid-private-featured",
            "start_date": "2026-01-01",
            "summary": "This private experience incorrectly requests featured status.",
            "is_public": False,
            "is_featured": True,
        },
    )

    assert response.status_code == 409, response.text
    assert response.json()["detail"]["code"] == "experience_lifecycle_conflict"


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("employment_type", "permanent"),
        ("location_type", "distributed"),
    ],
)
async def test_create_rejects_invalid_enums(
    client: AsyncClient,
    experience_records: dict[str, object],
    field_name: str,
    invalid_value: str,
) -> None:
    user = cast(User, experience_records["creator"])
    token = await login_user(client, email=user.email)
    payload: dict[str, object] = {
        "company_name": "Invalid Enum Ltd",
        "job_title": "Developer",
        "slug": f"invalid-{field_name}",
        "start_date": "2026-01-01",
        "summary": "This experience contains an unsupported enumeration value.",
        field_name: invalid_value,
    }

    response = await client.post(
        ADMIN_URL,
        headers=auth_headers(token),
        json=payload,
    )

    assert response.status_code == 422


async def test_update_normalizes_and_can_clear_end_date(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["updater"])
    experience = cast(Experience, experience_records["completed_public"])
    token = await login_user(client, email=user.email)
    headers = auth_headers(token)

    updated = await client.patch(
        f"{ADMIN_URL}/{experience.id}",
        headers=headers,
        json={
            "company_name": "  Akahalu   Digital Solutions  ",
            "slug": "AKAHALU-SENIOR-FULL-STACK",
        },
    )
    current = await client.patch(
        f"{ADMIN_URL}/{experience.id}",
        headers=headers,
        json={
            "is_current": True,
            "end_date": None,
        },
    )

    assert updated.status_code == 200, updated.text
    assert updated.json()["company_name"] == "Akahalu Digital Solutions"
    assert updated.json()["slug"] == "akahalu-senior-full-stack"
    assert current.status_code == 200, current.text
    assert current.json()["is_current"] is True
    assert current.json()["end_date"] is None


async def test_update_rejects_empty_duplicate_and_invalid_visibility(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["updater"])
    private = cast(Experience, experience_records["private"])
    featured = cast(Experience, experience_records["current_public"])
    token = await login_user(client, email=user.email)
    headers = auth_headers(token)

    empty = await client.patch(f"{ADMIN_URL}/{private.id}", headers=headers, json={})
    duplicate = await client.patch(
        f"{ADMIN_URL}/{private.id}",
        headers=headers,
        json={"slug": "zaradera-backend-developer"},
    )
    invalid_visibility = await client.patch(
        f"{ADMIN_URL}/{featured.id}",
        headers=headers,
        json={"is_public": False},
    )

    assert empty.status_code == 422
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["code"] == "experience_conflict"
    assert invalid_visibility.status_code == 409
    assert (
        invalid_visibility.json()["detail"]["code"] == "experience_lifecycle_conflict"
    )


async def test_feature_private_record_fails_but_visibility_endpoint_unfeatures(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["updater"])
    private = cast(Experience, experience_records["private"])
    featured = cast(Experience, experience_records["current_public"])
    token = await login_user(client, email=user.email)
    headers = auth_headers(token)

    feature_private = await client.patch(
        f"{ADMIN_URL}/{private.id}/featured",
        headers=headers,
        json={"is_featured": True, "reason": "Invalid feature request."},
    )
    hide_featured = await client.patch(
        f"{ADMIN_URL}/{featured.id}/visibility",
        headers=headers,
        json={"is_public": False, "reason": "Temporarily hide this record."},
    )

    assert feature_private.status_code == 409
    assert feature_private.json()["detail"]["code"] == "experience_lifecycle_conflict"
    assert hide_featured.status_code == 200, hide_featured.text
    assert hide_featured.json()["is_public"] is False
    assert hide_featured.json()["is_featured"] is False


async def test_delete_requires_permission_and_soft_deletes(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    updater = cast(User, experience_records["updater"])
    deleter = cast(User, experience_records["deleter"])
    experience = cast(Experience, experience_records["current_public"])
    updater_token = await login_user(client, email=updater.email)
    deleter_token = await login_user(client, email=deleter.email)

    denied = await client.request(
        "DELETE",
        f"{ADMIN_URL}/{experience.id}",
        headers=auth_headers(updater_token),
        json={"reason": "Unauthorized deletion attempt."},
    )
    deleted = await client.request(
        "DELETE",
        f"{ADMIN_URL}/{experience.id}",
        headers=auth_headers(deleter_token),
        json={"reason": "Removing outdated portfolio information."},
    )

    assert denied.status_code == 403
    assert deleted.status_code == 200, deleted.text
    assert deleted.json()["deleted_at"] is not None
    assert deleted.json()["is_public"] is False
    assert deleted.json()["is_featured"] is False


async def test_restore_deleted_record_can_make_it_public(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["updater"])
    deleted = cast(Experience, experience_records["deleted"])
    token = await login_user(client, email=user.email)

    response = await client.post(
        f"{ADMIN_URL}/{deleted.id}/restore",
        headers=auth_headers(token),
        json={
            "make_public": True,
            "reason": "Restoring verified professional history.",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["deleted_at"] is None
    assert response.json()["is_public"] is True
    assert response.json()["is_featured"] is False


async def test_public_endpoints_hide_private_and_deleted_records(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    listing = await client.get(PUBLIC_URL)
    private = await client.get(f"{PUBLIC_URL}/private-software-consultant")
    deleted = await client.get(f"{PUBLIC_URL}/legacy-junior-developer")

    assert listing.status_code == 200, listing.text
    assert listing.json()["total_items"] == 2
    assert [item["slug"] for item in listing.json()["items"]] == [
        "zaradera-backend-developer",
        "akahalu-full-stack-developer",
    ]
    assert private.status_code == 404
    assert deleted.status_code == 404


async def test_public_endpoints_support_filters_featured_and_slug_detail(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    filtered = await client.get(
        PUBLIC_URL,
        params={
            "employment_type": "contract",
            "location_type": "hybrid",
            "is_current": False,
            "is_featured": False,
            "search": "full",
        },
    )
    featured = await client.get(f"{PUBLIC_URL}/featured", params={"limit": 6})
    detail = await client.get(f"{PUBLIC_URL}/ZARADERA-BACKEND-DEVELOPER")

    assert filtered.status_code == 200, filtered.text
    assert filtered.json()["total_items"] == 1
    assert filtered.json()["items"][0]["slug"] == "akahalu-full-stack-developer"
    assert featured.status_code == 200, featured.text
    assert [item["slug"] for item in featured.json()] == ["zaradera-backend-developer"]
    assert detail.status_code == 200, detail.text
    assert detail.json()["slug"] == "zaradera-backend-developer"
    assert detail.json()["responsibilities"] is not None
    assert detail.json()["achievements"] is not None


async def test_manager_can_complete_full_experience_lifecycle(
    client: AsyncClient,
    experience_records: dict[str, object],
) -> None:
    user = cast(User, experience_records["manager"])
    token = await login_user(client, email=user.email)
    headers = auth_headers(token)

    created = await client.post(
        ADMIN_URL,
        headers=headers,
        json={
            "company_name": "Lifecycle Systems Ltd",
            "job_title": "Platform Engineer",
            "slug": "lifecycle-platform-engineer",
            "employment_type": "full_time",
            "location": "Regina, Saskatchewan",
            "location_type": "hybrid",
            "start_date": "2026-01-01",
            "is_current": True,
            "summary": "Built and maintained secure platform engineering workflows.",
            "sort_order": 20,
        },
    )
    assert created.status_code == 201, created.text
    experience_id = created.json()["id"]

    visible = await client.patch(
        f"{ADMIN_URL}/{experience_id}/visibility",
        headers=headers,
        json={"is_public": True, "reason": "Approved for public display."},
    )
    featured = await client.patch(
        f"{ADMIN_URL}/{experience_id}/featured",
        headers=headers,
        json={"is_featured": True, "reason": "Selected as a highlight."},
    )
    public_before_delete = await client.get(f"{PUBLIC_URL}/lifecycle-platform-engineer")
    deleted = await client.request(
        "DELETE",
        f"{ADMIN_URL}/{experience_id}",
        headers=headers,
        json={"reason": "Testing the complete soft-delete lifecycle."},
    )
    public_after_delete = await client.get(f"{PUBLIC_URL}/lifecycle-platform-engineer")
    restored = await client.post(
        f"{ADMIN_URL}/{experience_id}/restore",
        headers=headers,
        json={"make_public": True, "reason": "Restore lifecycle test record."},
    )
    public_after_restore = await client.get(f"{PUBLIC_URL}/lifecycle-platform-engineer")

    assert visible.status_code == 200
    assert featured.status_code == 200
    assert public_before_delete.status_code == 200
    assert deleted.status_code == 200
    assert deleted.json()["is_public"] is False
    assert deleted.json()["is_featured"] is False
    assert public_after_delete.status_code == 404
    assert restored.status_code == 200
    assert restored.json()["deleted_at"] is None
    assert restored.json()["is_public"] is True
    assert restored.json()["is_featured"] is False
    assert public_after_restore.status_code == 200
