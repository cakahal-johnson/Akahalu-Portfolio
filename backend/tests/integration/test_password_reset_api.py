from datetime import UTC, datetime, timedelta
from typing import Any, cast

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.security.passwords import hash_password
from app.security.account_tokens import digest_account_token


pytestmark = pytest.mark.asyncio


FORGOT_PASSWORD_URL = "/api/v1/account/forgot-password"
RESET_PASSWORD_URL = "/api/v1/account/reset-password"
LOGIN_URL = "/api/v1/auth/login"

TEST_EMAIL = "password-reset-user@example.com"
OLD_PASSWORD = "OldStrongPassword123!"
NEW_PASSWORD = "NewStrongPassword456!"


async def create_verified_user(
    database_session: AsyncSession,
    *,
    email: str = TEST_EMAIL,
    password: str = OLD_PASSWORD,
) -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name="Password",
        last_name="Reset",
        display_name="Password Reset",
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )

    database_session.add(user)
    await database_session.flush()

    return user


async def request_password_reset(
    client: AsyncClient,
    *,
    email: str = TEST_EMAIL,
) -> dict[str, Any]:
    response = await client.post(
        FORGOT_PASSWORD_URL,
        json={
            "email": email,
        },
    )

    assert response.status_code == 200, response.text

    return cast(dict[str, Any], response.json())


async def reset_password(
    client: AsyncClient,
    *,
    token: str,
    new_password: str = NEW_PASSWORD,
):
    return await client.post(
        RESET_PASSWORD_URL,
        json={
            "token": token,
            "new_password": new_password,
        },
    )


async def login(
    client: AsyncClient,
    *,
    email: str = TEST_EMAIL,
    password: str,
):
    return await client.post(
        LOGIN_URL,
        json={
            "email": email,
            "password": password,
            "device_name": "Password Reset Test",
        },
        headers={
            "User-Agent": "pytest-password-reset-client",
        },
    )


async def test_forgot_password_returns_token_for_eligible_account(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    await create_verified_user(database_session)

    payload = await request_password_reset(client)

    assert payload["message"] == (
        "If an eligible account exists, password reset instructions will be sent."
    )
    assert payload["reset_token"]
    assert payload["reset_token_expires_at"]


async def test_forgot_password_returns_generic_response_for_unknown_account(
    client: AsyncClient,
) -> None:
    payload = await request_password_reset(
        client,
        email="unknown-password-reset@example.com",
    )

    assert payload["message"] == (
        "If an eligible account exists, password reset instructions will be sent."
    )
    assert payload["reset_token"] is None
    assert payload["reset_token_expires_at"] is None


async def test_forgot_password_normalizes_email(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    await create_verified_user(database_session)

    payload = await request_password_reset(
        client,
        email=f"  {TEST_EMAIL.upper()}  ",
    )

    assert payload["reset_token"]
    assert payload["reset_token_expires_at"]


async def test_forgot_password_rotates_existing_token(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    await create_verified_user(database_session)

    first_payload = await request_password_reset(client)
    first_token = str(first_payload["reset_token"])

    second_payload = await request_password_reset(client)
    second_token = str(second_payload["reset_token"])

    assert second_token
    assert second_token != first_token

    old_token_response = await reset_password(
        client,
        token=first_token,
    )

    assert old_token_response.status_code == 400
    assert old_token_response.json()["detail"]["code"] == (
        "invalid_password_reset_token"
    )


async def test_reset_password_succeeds(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    await create_verified_user(database_session)

    forgot_payload = await request_password_reset(client)
    reset_token = str(forgot_payload["reset_token"])

    response = await reset_password(
        client,
        token=reset_token,
    )

    assert response.status_code == 200, response.text

    payload = response.json()

    assert payload["message"] == "Password reset successfully."


async def test_reset_password_rejects_invalid_token(
    client: AsyncClient,
) -> None:
    response = await reset_password(
        client,
        token="invalid-password-reset-token",
    )

    assert response.status_code == 400

    detail = response.json()["detail"]

    assert detail["code"] == "invalid_password_reset_token"
    assert detail["message"]


async def test_reset_password_rejects_consumed_token(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    await create_verified_user(database_session)

    forgot_payload = await request_password_reset(client)
    reset_token = str(forgot_payload["reset_token"])

    first_response = await reset_password(
        client,
        token=reset_token,
    )

    second_response = await reset_password(
        client,
        token=reset_token,
        new_password="AnotherStrongPassword789!",
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"]["code"] == ("invalid_password_reset_token")


async def test_reset_password_rejects_expired_token(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    user = await create_verified_user(database_session)

    raw_token = "expired-password-reset-token"
    now = datetime.now(UTC)

    expired_token = PasswordResetToken(
        user_id=user.id,
        token_digest=digest_account_token(raw_token),
        created_at=now - timedelta(hours=2),
        updated_at=now - timedelta(hours=2),
        expires_at=now - timedelta(hours=1),
    )

    database_session.add(expired_token)
    await database_session.flush()

    response = await reset_password(
        client,
        token=raw_token,
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == ("invalid_password_reset_token")


async def test_reset_password_rejects_weak_password(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    await create_verified_user(database_session)

    forgot_payload = await request_password_reset(client)
    reset_token = str(forgot_payload["reset_token"])

    response = await reset_password(
        client,
        token=reset_token,
        new_password="Short1!",
    )

    assert response.status_code == 422


async def test_old_password_is_rejected_after_reset(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    await create_verified_user(database_session)

    forgot_payload = await request_password_reset(client)
    reset_token = str(forgot_payload["reset_token"])

    reset_response = await reset_password(
        client,
        token=reset_token,
    )

    assert reset_response.status_code == 200

    login_response = await login(
        client,
        password=OLD_PASSWORD,
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"]["code"] == "invalid_credentials"


async def test_new_password_is_accepted_after_reset(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    await create_verified_user(database_session)

    forgot_payload = await request_password_reset(client)
    reset_token = str(forgot_payload["reset_token"])

    reset_response = await reset_password(
        client,
        token=reset_token,
    )

    assert reset_response.status_code == 200

    login_response = await login(
        client,
        password=NEW_PASSWORD,
    )

    assert login_response.status_code == 200
    assert login_response.json()["user"]["email"] == TEST_EMAIL


async def test_reset_password_clears_account_lockout(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    user = await create_verified_user(database_session)

    user.failed_login_attempts = 5
    user.locked_until = datetime.now(UTC) + timedelta(minutes=15)

    await database_session.flush()

    forgot_payload = await request_password_reset(client)
    reset_token = str(forgot_payload["reset_token"])

    response = await reset_password(
        client,
        token=reset_token,
    )

    assert response.status_code == 200

    await database_session.refresh(user)

    assert user.failed_login_attempts == 0
    assert user.locked_until is None
    assert user.password_changed_at is not None


async def test_reset_password_marks_token_as_consumed(
    client: AsyncClient,
    database_session: AsyncSession,
) -> None:
    await create_verified_user(database_session)

    forgot_payload = await request_password_reset(client)
    reset_token = str(forgot_payload["reset_token"])

    response = await reset_password(
        client,
        token=reset_token,
    )

    assert response.status_code == 200

    statement = select(PasswordResetToken).where(
        PasswordResetToken.consumed_at.is_not(None),
    )

    result = await database_session.execute(statement)
    consumed_token = result.scalar_one_or_none()

    assert consumed_token is not None
    assert consumed_token.consumed_at is not None
