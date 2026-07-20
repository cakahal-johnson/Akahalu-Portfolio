from collections.abc import AsyncIterator
from typing import Any, cast

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.security.passwords import hash_password


TEST_EMAIL = "auth-test@example.com"
TEST_PASSWORD = "StrongTestPassword123!"

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def test_user(
    database_session: AsyncSession,
) -> AsyncIterator[User]:
    user = User(
        email=TEST_EMAIL,
        password_hash=hash_password(TEST_PASSWORD),
        first_name="Authentication",
        last_name="Tester",
        display_name="Auth Tester",
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )

    database_session.add(user)
    await database_session.flush()

    yield user


async def login_user(
    client: AsyncClient,
    *,
    email: str = TEST_EMAIL,
    password: str = TEST_PASSWORD,
    device_name: str | None = "Pytest",
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "device_name": device_name,
        },
        headers={
            "User-Agent": "authentication-integration-tests",
        },
    )

    assert response.status_code == 200, response.text

    return cast(dict[str, Any], response.json())


def get_tokens(payload: dict[str, Any]) -> dict[str, Any]:
    tokens = payload.get("tokens")

    assert isinstance(tokens, dict)

    return cast(dict[str, Any], tokens)


async def test_login_succeeds_with_valid_credentials(
    client: AsyncClient,
    test_user: User,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": TEST_EMAIL.upper(),
            "password": TEST_PASSWORD,
            "device_name": "Windows Desktop",
        },
        headers={
            "User-Agent": "pytest-authentication-client",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(dict[str, Any], response.json())
    user_payload = cast(dict[str, Any], payload["user"])
    tokens = get_tokens(payload)

    assert user_payload["id"] == str(test_user.id)
    assert str(user_payload["email"]).lower() == TEST_EMAIL
    assert user_payload["is_active"] is True
    assert user_payload["is_verified"] is True

    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["access_token_expires_at"]
    assert tokens["refresh_token_expires_at"]


async def test_login_rejects_invalid_password(
    client: AsyncClient,
    test_user: User,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "IncorrectPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "invalid_credentials"


async def test_login_rejects_unknown_account(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "missing-user@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "invalid_credentials"


async def test_login_rejects_disabled_account(
    client: AsyncClient,
    database_session: AsyncSession,
    test_user: User,
) -> None:
    test_user.is_active = False
    await database_session.flush()

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "account_disabled"


async def test_me_returns_authenticated_user(
    client: AsyncClient,
    test_user: User,
) -> None:
    login_payload = await login_user(client)
    tokens = get_tokens(login_payload)
    access_token = str(tokens["access_token"])

    response = await client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(dict[str, Any], response.json())

    assert payload["id"] == str(test_user.id)
    assert str(payload["email"]).lower() == TEST_EMAIL
    assert payload["is_active"] is True


async def test_me_rejects_missing_access_token(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == ("invalid_authentication")


async def test_me_rejects_invalid_access_token(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid-access-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == ("invalid_authentication")


async def test_refresh_rotates_refresh_token(
    client: AsyncClient,
    test_user: User,
) -> None:
    login_payload = await login_user(client)
    original_tokens = get_tokens(login_payload)
    original_refresh_token = str(original_tokens["refresh_token"])

    response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": original_refresh_token,
        },
    )

    assert response.status_code == 200, response.text

    payload = cast(dict[str, Any], response.json())
    user_payload = cast(dict[str, Any], payload["user"])
    tokens = get_tokens(payload)

    assert user_payload["id"] == str(test_user.id)
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["refresh_token"] != original_refresh_token


async def test_reusing_rotated_refresh_token_is_rejected(
    client: AsyncClient,
    test_user: User,
) -> None:
    login_payload = await login_user(client)
    original_tokens = get_tokens(login_payload)
    original_refresh_token = str(original_tokens["refresh_token"])

    first_refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": original_refresh_token,
        },
    )

    assert first_refresh_response.status_code == 200

    reuse_response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": original_refresh_token,
        },
    )

    assert reuse_response.status_code == 401
    assert reuse_response.json()["detail"]["code"] == ("refresh_token_reuse")


async def test_logout_revokes_session(
    client: AsyncClient,
    test_user: User,
) -> None:
    login_payload = await login_user(client)
    tokens = get_tokens(login_payload)

    access_token = str(tokens["access_token"])
    refresh_token = str(tokens["refresh_token"])

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert logout_response.status_code == 204
    assert logout_response.content == b""

    me_response = await client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert me_response.status_code == 401
    assert me_response.json()["detail"]["code"] == ("invalid_authentication")


async def test_refresh_after_logout_is_rejected(
    client: AsyncClient,
    test_user: User,
) -> None:
    login_payload = await login_user(client)
    tokens = get_tokens(login_payload)
    refresh_token = str(tokens["refresh_token"])

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert logout_response.status_code == 204

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh_response.status_code == 401
    assert refresh_response.json()["detail"]["code"] == ("refresh_token_reuse")


async def test_login_rejects_unverified_account(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    email = "unverified-user@example.com"
    password = "StrongPassword123!"

    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name="Unverified",
        last_name="User",
        display_name="Unverified User",
        is_active=True,
        is_verified=False,
        is_superuser=False,
    )

    database_session.add(user)
    await database_session.flush()

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "device_name": "Windows Desktop",
        },
        headers={
            "User-Agent": "pytest-authentication-client",
        },
    )

    assert response.status_code == 403

    detail = response.json()["detail"]

    assert detail["code"] == "email_not_verified"
    assert detail["message"]


async def test_logout_all_revokes_all_user_sessions(
    client: AsyncClient,
    test_user: User,
) -> None:
    first_login = await login_user(
        client,
        device_name="First Device",
    )

    second_login = await login_user(
        client,
        device_name="Second Device",
    )

    first_tokens = get_tokens(first_login)
    second_tokens = get_tokens(second_login)

    first_access_token = str(first_tokens["access_token"])
    second_access_token = str(second_tokens["access_token"])
    second_refresh_token = str(second_tokens["refresh_token"])

    logout_all_response = await client.post(
        "/api/v1/auth/logout-all",
        headers={
            "Authorization": f"Bearer {first_access_token}",
        },
    )

    assert logout_all_response.status_code == 204
    assert logout_all_response.content == b""

    first_me_response = await client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {first_access_token}",
        },
    )

    second_me_response = await client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {second_access_token}",
        },
    )

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": second_refresh_token,
        },
    )

    assert first_me_response.status_code == 401
    assert second_me_response.status_code == 401
    assert refresh_response.status_code == 401
