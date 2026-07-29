from collections.abc import AsyncIterator
from typing import Any, cast

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.profile import Profile
from app.models.role import Role
from app.models.user import User
from app.security.passwords import hash_password


TEST_PASSWORD = "StrongPortfolioProfilePassword123!"

ADMIN_PROFILE_URL = "/api/v1/admin/portfolio/profile"
PUBLIC_PROFILE_URL = "/api/v1/portfolio/profile"

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
        last_name="Profile Administrator",
        display_name="Portfolio Profile Administrator",
        is_active=True,
        is_verified=True,
        is_superuser=is_superuser,
        roles=roles or [],
    )


def create_profile(
    *,
    created_by: User,
    is_public: bool = True,
) -> Profile:
    return Profile(
        profile_key="primary",
        first_name="Akahalu",
        middle_name="Chinonso",
        last_name="Vitalis",
        display_name="Akahalu Vitalis",
        professional_title="Full-Stack Software Developer",
        headline=(
            "Building secure web, API, and mobile applications "
            "with modern technologies."
        ),
        short_bio=(
            "Full-stack developer specializing in secure APIs, "
            "web platforms, and mobile applications."
        ),
        biography=(
            "Akahalu Vitalis is a software developer focused on building "
            "secure, maintainable, and production-ready digital products. "
            "His experience includes backend APIs, web applications, mobile "
            "development, database design, testing, and deployment."
        ),
        location="Regina, Saskatchewan",
        country="Canada",
        timezone="America/Regina",
        primary_email="akahalu@example.com",
        phone="+1 306 555 0101",
        website_url="https://akahalu.example.com",
        resume_url="https://akahalu.example.com/resume.pdf",
        profile_image_url="https://akahalu.example.com/profile.jpg",
        years_of_experience=5,
        availability_message=("Available for software development opportunities."),
        is_public=is_public,
        seo_title="Akahalu Vitalis | Full-Stack Software Developer",
        seo_description=(
            "Professional portfolio of Akahalu Vitalis, a full-stack "
            "software developer specializing in APIs, web, and mobile."
        ),
        created_by=created_by,
        updated_by=created_by,
    )


def valid_profile_payload() -> dict[str, Any]:
    return {
        "first_name": "  Akahalu  ",
        "middle_name": "  Chinonso  ",
        "last_name": "  Vitalis  ",
        "display_name": "  Akahalu   Vitalis  ",
        "professional_title": "  Full-Stack   Software Developer  ",
        "headline": (
            "  Building secure web, API, and mobile applications "
            "with modern technologies.  "
        ),
        "short_bio": (
            "  Full-stack developer specializing in secure APIs, "
            "web platforms, and mobile applications.  "
        ),
        "biography": (
            "  Akahalu Vitalis is a software developer focused on building "
            "secure, maintainable, and production-ready digital products. "
            "His experience includes backend APIs, web applications, mobile "
            "development, database design, testing, and deployment.  "
        ),
        "location": "  Regina, Saskatchewan  ",
        "country": "  Canada  ",
        "timezone": "  America/Regina  ",
        "primary_email": "  AKAHALU@EXAMPLE.COM  ",
        "phone": "  +1 306 555 0101  ",
        "website_url": "https://akahalu.example.com",
        "resume_url": "https://akahalu.example.com/resume.pdf",
        "profile_image_url": "https://akahalu.example.com/profile.jpg",
        "years_of_experience": 5,
        "availability_message": (
            "  Available for software development opportunities.  "
        ),
        "is_public": True,
        "seo_title": ("  Akahalu Vitalis | Full-Stack Software Developer  "),
        "seo_description": (
            "  Professional portfolio of Akahalu Vitalis, a full-stack "
            "software developer specializing in APIs, web, and mobile.  "
        ),
    }


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
            "device_name": "Portfolio profile integration test",
        },
        headers={
            "User-Agent": "portfolio-profile-integration-tests",
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
async def profile_authorization_records(
    database_session: AsyncSession,
) -> AsyncIterator[dict[str, object]]:
    profile_read = create_permission(
        "profile.read",
    )
    profile_create = create_permission(
        "profile.create",
    )
    profile_update = create_permission(
        "profile.update",
    )
    profile_delete = create_permission(
        "profile.delete",
    )
    unrelated_permission = create_permission(
        "settings.manage",
    )

    reader_role = create_role(
        "portfolio_profile_reader",
        permissions=[
            profile_read,
        ],
    )
    creator_role = create_role(
        "portfolio_profile_creator",
        permissions=[
            profile_create,
        ],
    )
    updater_role = create_role(
        "portfolio_profile_updater",
        permissions=[
            profile_update,
        ],
    )
    deleter_role = create_role(
        "portfolio_profile_deleter",
        permissions=[
            profile_delete,
        ],
    )
    manager_role = create_role(
        "portfolio_profile_manager",
        permissions=[
            profile_read,
            profile_create,
            profile_update,
            profile_delete,
        ],
    )
    outsider_role = create_role(
        "portfolio_profile_outsider",
        permissions=[
            unrelated_permission,
        ],
    )

    reader_user = create_user(
        email="portfolio-profile-reader@example.com",
        roles=[
            reader_role,
        ],
    )
    creator_user = create_user(
        email="portfolio-profile-creator@example.com",
        roles=[
            creator_role,
        ],
    )
    updater_user = create_user(
        email="portfolio-profile-updater@example.com",
        roles=[
            updater_role,
        ],
    )
    deleter_user = create_user(
        email="portfolio-profile-deleter@example.com",
        roles=[
            deleter_role,
        ],
    )
    manager_user = create_user(
        email="portfolio-profile-manager@example.com",
        roles=[
            manager_role,
        ],
    )
    outsider_user = create_user(
        email="portfolio-profile-outsider@example.com",
        roles=[
            outsider_role,
        ],
    )
    superuser = create_user(
        email="portfolio-profile-superuser@example.com",
        is_superuser=True,
    )

    database_session.add_all(
        [
            profile_read,
            profile_create,
            profile_update,
            profile_delete,
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
    }


async def test_public_profile_returns_not_found_when_missing(
    client: AsyncClient,
) -> None:
    response = await client.get(
        PUBLIC_PROFILE_URL,
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == ("public_profile_not_found")


async def test_public_profile_returns_visible_profile(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        profile_authorization_records["manager_user"],
    )

    profile = create_profile(
        created_by=manager_user,
        is_public=True,
    )

    database_session.add(
        profile,
    )
    await database_session.flush()

    response = await client.get(
        PUBLIC_PROFILE_URL,
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["id"] == str(profile.id)
    assert payload["display_name"] == "Akahalu Vitalis"
    assert payload["professional_title"] == ("Full-Stack Software Developer")
    assert payload["primary_email"] == "akahalu@example.com"
    assert payload["is_public"] is True


async def test_public_profile_hides_private_profile(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        profile_authorization_records["manager_user"],
    )

    database_session.add(
        create_profile(
            created_by=manager_user,
            is_public=False,
        )
    )
    await database_session.flush()

    response = await client.get(
        PUBLIC_PROFILE_URL,
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == ("public_profile_not_found")


async def test_get_admin_profile_rejects_unauthenticated_request(
    client: AsyncClient,
) -> None:
    response = await client.get(
        ADMIN_PROFILE_URL,
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == ("invalid_authentication")


async def test_get_admin_profile_rejects_missing_permission(
    client: AsyncClient,
    profile_authorization_records: dict[str, object],
) -> None:
    outsider_user = cast(
        User,
        profile_authorization_records["outsider_user"],
    )

    access_token = await login_user(
        client,
        email=outsider_user.email,
    )

    response = await client.get(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == ("insufficient_permissions")


async def test_get_admin_profile_returns_not_found_when_missing(
    client: AsyncClient,
    profile_authorization_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        profile_authorization_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.get(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "profile_not_found"


async def test_superuser_can_get_profile_without_explicit_permission(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    superuser = cast(
        User,
        profile_authorization_records["superuser"],
    )

    profile = create_profile(
        created_by=superuser,
    )

    database_session.add(
        profile,
    )
    await database_session.flush()

    access_token = await login_user(
        client,
        email=superuser.email,
    )

    response = await client.get(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json()["id"] == str(profile.id)


async def test_create_profile_succeeds_and_normalizes_values(
    client: AsyncClient,
    profile_authorization_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        profile_authorization_records["creator_user"],
    )

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
        json=valid_profile_payload(),
    )

    assert response.status_code == 201, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["profile_key"] == "primary"
    assert payload["first_name"] == "Akahalu"
    assert payload["middle_name"] == "Chinonso"
    assert payload["last_name"] == "Vitalis"
    assert payload["display_name"] == "Akahalu Vitalis"
    assert payload["professional_title"] == ("Full-Stack Software Developer")
    assert payload["primary_email"] == "akahalu@example.com"
    assert payload["is_public"] is True
    assert payload["deleted_at"] is None
    assert payload["created_by_id"] == str(creator_user.id)
    assert payload["updated_by_id"] == str(creator_user.id)


async def test_create_profile_rejects_missing_permission(
    client: AsyncClient,
    profile_authorization_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        profile_authorization_records["reader_user"],
    )

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    response = await client.post(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
        json=valid_profile_payload(),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == ("insufficient_permissions")


async def test_create_profile_rejects_second_profile(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        profile_authorization_records["creator_user"],
    )

    database_session.add(
        create_profile(
            created_by=creator_user,
        )
    )
    await database_session.flush()

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
        json=valid_profile_payload(),
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == ("profile_already_exists")


async def test_update_profile_succeeds(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        profile_authorization_records["updater_user"],
    )

    profile = create_profile(
        created_by=updater_user,
    )

    database_session.add(
        profile,
    )
    await database_session.flush()

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "professional_title": ("Senior Full-Stack Software Developer"),
            "headline": ("Designing secure and scalable software products."),
            "years_of_experience": 6,
            "primary_email": "UPDATED@EXAMPLE.COM",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["professional_title"] == ("Senior Full-Stack Software Developer")
    assert payload["headline"] == ("Designing secure and scalable software products.")
    assert payload["years_of_experience"] == 6
    assert payload["primary_email"] == "updated@example.com"
    assert payload["updated_by_id"] == str(updater_user.id)


async def test_update_profile_can_clear_nullable_field(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        profile_authorization_records["updater_user"],
    )

    profile = create_profile(
        created_by=updater_user,
    )

    database_session.add(
        profile,
    )
    await database_session.flush()

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.patch(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "phone": None,
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["phone"] is None


async def test_update_visibility_hides_profile_from_public_endpoint(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        profile_authorization_records["updater_user"],
    )

    database_session.add(
        create_profile(
            created_by=updater_user,
            is_public=True,
        )
    )
    await database_session.flush()

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    visibility_response = await client.patch(
        f"{ADMIN_PROFILE_URL}/visibility",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "is_public": False,
            "reason": "Temporarily hidden during content review.",
        },
    )

    public_response = await client.get(
        PUBLIC_PROFILE_URL,
    )

    assert visibility_response.status_code == 200
    assert visibility_response.json()["is_public"] is False
    assert public_response.status_code == 404


async def test_delete_profile_soft_deletes_and_disables_visibility(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    deleter_user = cast(
        User,
        profile_authorization_records["deleter_user"],
    )

    profile = create_profile(
        created_by=deleter_user,
        is_public=True,
    )

    database_session.add(
        profile,
    )
    await database_session.flush()

    access_token = await login_user(
        client,
        email=deleter_user.email,
    )

    delete_response = await client.request(
        "DELETE",
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "reason": "Profile content requires complete revision.",
        },
    )

    public_response = await client.get(
        PUBLIC_PROFILE_URL,
    )

    assert delete_response.status_code == 200, delete_response.text

    payload = cast(
        dict[str, Any],
        delete_response.json(),
    )

    assert payload["id"] == str(profile.id)
    assert payload["is_public"] is False
    assert payload["deleted_at"] is not None
    assert payload["updated_by_id"] == str(deleter_user.id)
    assert public_response.status_code == 404


async def test_delete_profile_rejects_missing_permission(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        profile_authorization_records["updater_user"],
    )

    database_session.add(
        create_profile(
            created_by=updater_user,
        )
    )
    await database_session.flush()

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.request(
        "DELETE",
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "reason": "Unauthorized deletion attempt.",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == ("insufficient_permissions")


async def test_deleted_profile_requires_include_deleted_for_admin_read(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    reader_user = cast(
        User,
        profile_authorization_records["reader_user"],
    )

    profile = create_profile(
        created_by=reader_user,
        is_public=False,
    )
    profile.soft_delete()

    database_session.add(
        profile,
    )
    await database_session.flush()

    access_token = await login_user(
        client,
        email=reader_user.email,
    )

    hidden_response = await client.get(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
    )

    visible_response = await client.get(
        ADMIN_PROFILE_URL,
        params={
            "include_deleted": True,
        },
        headers=authorization_headers(
            access_token,
        ),
    )

    assert hidden_response.status_code == 409
    assert hidden_response.json()["detail"]["code"] == ("profile_deleted")

    assert visible_response.status_code == 200, visible_response.text
    assert visible_response.json()["deleted_at"] is not None


async def test_create_rejects_when_deleted_profile_exists(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    creator_user = cast(
        User,
        profile_authorization_records["creator_user"],
    )

    profile = create_profile(
        created_by=creator_user,
        is_public=False,
    )
    profile.soft_delete()

    database_session.add(
        profile,
    )
    await database_session.flush()

    access_token = await login_user(
        client,
        email=creator_user.email,
    )

    response = await client.post(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
        json=valid_profile_payload(),
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "profile_deleted"


async def test_restore_deleted_profile_succeeds(
    client: AsyncClient,
    database_session: AsyncSession,
    profile_authorization_records: dict[str, object],
) -> None:
    updater_user = cast(
        User,
        profile_authorization_records["updater_user"],
    )

    profile = create_profile(
        created_by=updater_user,
        is_public=False,
    )
    profile.soft_delete()

    database_session.add(
        profile,
    )
    await database_session.flush()

    access_token = await login_user(
        client,
        email=updater_user.email,
    )

    response = await client.post(
        f"{ADMIN_PROFILE_URL}/restore",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "restore_as_public": True,
            "reason": "Profile content has been reviewed and approved.",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(
        dict[str, Any],
        response.json(),
    )

    assert payload["id"] == str(profile.id)
    assert payload["deleted_at"] is None
    assert payload["is_public"] is True
    assert payload["updated_by_id"] == str(updater_user.id)


async def test_manager_can_complete_profile_lifecycle(
    client: AsyncClient,
    profile_authorization_records: dict[str, object],
) -> None:
    manager_user = cast(
        User,
        profile_authorization_records["manager_user"],
    )

    access_token = await login_user(
        client,
        email=manager_user.email,
    )

    create_response = await client.post(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
        json=valid_profile_payload(),
    )

    assert create_response.status_code == 201, create_response.text

    profile_id = str(
        create_response.json()["id"],
    )

    update_response = await client.patch(
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "headline": ("Building secure software solutions for modern businesses."),
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["id"] == profile_id

    visibility_response = await client.patch(
        f"{ADMIN_PROFILE_URL}/visibility",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "is_public": False,
        },
    )

    assert visibility_response.status_code == 200
    assert visibility_response.json()["is_public"] is False

    delete_response = await client.request(
        "DELETE",
        ADMIN_PROFILE_URL,
        headers=authorization_headers(
            access_token,
        ),
        json={
            "reason": "Profile lifecycle deletion test.",
        },
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["deleted_at"] is not None

    restore_response = await client.post(
        f"{ADMIN_PROFILE_URL}/restore",
        headers=authorization_headers(
            access_token,
        ),
        json={
            "restore_as_public": True,
            "reason": "Profile lifecycle restoration test.",
        },
    )

    assert restore_response.status_code == 200
    assert restore_response.json()["id"] == profile_id
    assert restore_response.json()["deleted_at"] is None
    assert restore_response.json()["is_public"] is True

    public_response = await client.get(
        PUBLIC_PROFILE_URL,
    )

    assert public_response.status_code == 200
    assert public_response.json()["id"] == profile_id
