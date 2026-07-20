from typing import Any

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


REGISTER_URL = "/api/v1/account/register"
VERIFY_EMAIL_URL = "/api/v1/account/verify-email"
RESEND_VERIFICATION_URL = "/api/v1/account/resend-verification"

LOGIN_URL = "/api/v1/auth/login"

VALID_PASSWORD = "StrongPassword123!"


def registration_payload(
    *,
    email: str,
    password: str = VALID_PASSWORD,
    first_name: str = "Akahalu",
    last_name: str = "Johnson",
    display_name: str | None = "Akahalu Johnson",
) -> dict[str, Any]:
    return {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "display_name": display_name,
    }


async def register_user(
    client: AsyncClient,
    *,
    email: str,
) -> dict[str, Any]:
    response = await client.post(
        REGISTER_URL,
        json=registration_payload(email=email),
    )

    assert response.status_code == 201

    payload: dict[str, Any] = response.json()

    return payload


async def test_registration_succeeds(
    client: AsyncClient,
) -> None:
    response = await client.post(
        REGISTER_URL,
        json=registration_payload(
            email="new-user@example.com",
        ),
    )

    assert response.status_code == 201

    payload = response.json()
    user = payload["user"]

    assert user["email"] == "new-user@example.com"
    assert user["first_name"] == "Akahalu"
    assert user["last_name"] == "Johnson"
    assert user["display_name"] == "Akahalu Johnson"
    assert user["is_active"] is True
    assert user["is_verified"] is False

    assert payload["message"] == (
        "Registration completed. Please verify your email address."
    )
    assert payload["verification_token"]
    assert payload["verification_token_expires_at"]


async def test_registration_normalizes_email_and_names(
    client: AsyncClient,
) -> None:
    response = await client.post(
        REGISTER_URL,
        json=registration_payload(
            email="NORMALIZED-USER@EXAMPLE.COM",
            first_name="  Akahalu   Chinonso  ",
            last_name="  Johnson   Vitalis  ",
            display_name="  Akahalu   Johnson  ",
        ),
    )

    assert response.status_code == 201

    user = response.json()["user"]

    assert user["email"] == "normalized-user@example.com"
    assert user["first_name"] == "Akahalu Chinonso"
    assert user["last_name"] == "Johnson Vitalis"
    assert user["display_name"] == "Akahalu Johnson"


async def test_registration_rejects_duplicate_email(
    client: AsyncClient,
) -> None:
    email = "duplicate-user@example.com"

    first_response = await client.post(
        REGISTER_URL,
        json=registration_payload(email=email),
    )

    duplicate_response = await client.post(
        REGISTER_URL,
        json=registration_payload(
            email=email.upper(),
        ),
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409

    detail = duplicate_response.json()["detail"]

    assert detail["code"] == "email_already_registered"
    assert detail["message"]


async def test_registration_rejects_short_password(
    client: AsyncClient,
) -> None:
    response = await client.post(
        REGISTER_URL,
        json=registration_payload(
            email="weak-password@example.com",
            password="TooShort1!",
        ),
    )

    assert response.status_code == 422


async def test_registration_rejects_blank_required_name(
    client: AsyncClient,
) -> None:
    response = await client.post(
        REGISTER_URL,
        json=registration_payload(
            email="blank-name@example.com",
            first_name="   ",
        ),
    )

    assert response.status_code == 422


async def test_email_verification_succeeds(
    client: AsyncClient,
) -> None:
    registration = await register_user(
        client,
        email="verification-user@example.com",
    )

    verification_token = str(registration["verification_token"])

    response = await client.post(
        VERIFY_EMAIL_URL,
        json={
            "token": verification_token,
        },
    )

    assert response.status_code == 200

    payload = response.json()
    user = payload["user"]

    assert user["email"] == "verification-user@example.com"
    assert user["is_verified"] is True
    assert payload["message"] == ("Email address verified successfully.")


async def test_registered_user_can_login_only_after_verification(
    client: AsyncClient,
) -> None:
    email = "verification-login@example.com"
    password = VALID_PASSWORD

    registration_response = await client.post(
        REGISTER_URL,
        json=registration_payload(
            email=email,
            password=password,
        ),
    )

    assert registration_response.status_code == 201

    registration_payload_data = registration_response.json()
    verification_token = str(registration_payload_data["verification_token"])

    login_before_verification = await client.post(
        LOGIN_URL,
        json={
            "email": email,
            "password": password,
            "device_name": "Integration Test",
        },
        headers={
            "User-Agent": "pytest-account-lifecycle-client",
        },
    )

    assert login_before_verification.status_code == 403

    detail = login_before_verification.json()["detail"]

    assert detail["code"] == "email_not_verified"

    verification_response = await client.post(
        VERIFY_EMAIL_URL,
        json={
            "token": verification_token,
        },
    )

    assert verification_response.status_code == 200

    login_after_verification = await client.post(
        LOGIN_URL,
        json={
            "email": email,
            "password": password,
            "device_name": "Integration Test",
        },
        headers={
            "User-Agent": "pytest-account-lifecycle-client",
        },
    )

    assert login_after_verification.status_code == 200

    payload = login_after_verification.json()

    assert payload["user"]["email"] == email
    assert payload["user"]["is_verified"] is True
    assert payload["tokens"]["access_token"]
    assert payload["tokens"]["refresh_token"]


async def test_email_verification_rejects_invalid_token(
    client: AsyncClient,
) -> None:
    response = await client.post(
        VERIFY_EMAIL_URL,
        json={
            "token": "invalid-verification-token",
        },
    )

    assert response.status_code == 400

    detail = response.json()["detail"]

    assert detail["code"] == "invalid_verification_token"
    assert detail["message"]


async def test_email_verification_rejects_consumed_token(
    client: AsyncClient,
) -> None:
    registration = await register_user(
        client,
        email="consumed-token@example.com",
    )

    verification_token = str(registration["verification_token"])

    first_response = await client.post(
        VERIFY_EMAIL_URL,
        json={
            "token": verification_token,
        },
    )

    second_response = await client.post(
        VERIFY_EMAIL_URL,
        json={
            "token": verification_token,
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400

    detail = second_response.json()["detail"]

    assert detail["code"] == "invalid_verification_token"


async def test_resend_verification_returns_generic_response_for_unknown_email(
    client: AsyncClient,
) -> None:
    response = await client.post(
        RESEND_VERIFICATION_URL,
        json={
            "email": "unknown-account@example.com",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["message"] == (
        "If an eligible account exists, a verification email will be sent."
    )
    assert payload["verification_token"] is None
    assert payload["verification_token_expires_at"] is None


async def test_resend_verification_rotates_token(
    client: AsyncClient,
) -> None:
    email = "resend-token@example.com"

    registration = await register_user(
        client,
        email=email,
    )

    original_token = str(registration["verification_token"])

    response = await client.post(
        RESEND_VERIFICATION_URL,
        json={
            "email": email,
        },
    )

    assert response.status_code == 200

    payload = response.json()
    new_token = payload["verification_token"]

    assert payload["message"] == (
        "If an eligible account exists, a verification email will be sent."
    )
    assert new_token
    assert new_token != original_token
    assert payload["verification_token_expires_at"]

    old_token_response = await client.post(
        VERIFY_EMAIL_URL,
        json={
            "token": original_token,
        },
    )

    new_token_response = await client.post(
        VERIFY_EMAIL_URL,
        json={
            "token": new_token,
        },
    )

    assert old_token_response.status_code == 400
    assert new_token_response.status_code == 200
    assert new_token_response.json()["user"]["is_verified"] is True
