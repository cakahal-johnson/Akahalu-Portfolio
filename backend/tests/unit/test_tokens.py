from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.security.tokens import (
    TokenValidationError,
    constant_time_digest_matches,
    create_access_token,
    decode_access_token,
    digest_refresh_token,
    generate_refresh_token,
)


def current_test_time() -> datetime:
    return datetime.now(UTC).replace(
        microsecond=0,
    )


def test_create_and_decode_access_token() -> None:
    user_id = uuid4()
    session_id = uuid4()
    issued_at = current_test_time()

    created_token = create_access_token(
        user_id=user_id,
        session_id=session_id,
        now=issued_at,
    )

    decoded_token = decode_access_token(
        created_token.value,
    )

    assert decoded_token.user_id == user_id
    assert decoded_token.session_id == session_id
    assert decoded_token.token_id == created_token.token_id
    assert decoded_token.issued_at == issued_at
    assert decoded_token.expires_at == created_token.expires_at


def test_decode_rejects_invalid_token() -> None:
    with pytest.raises(
        TokenValidationError,
        match="Invalid or expired access token",
    ):
        decode_access_token(
            "not-a-valid-jwt",
        )


def test_refresh_tokens_are_random() -> None:
    issued_at = current_test_time()

    first_token = generate_refresh_token(
        now=issued_at,
    )

    second_token = generate_refresh_token(
        now=issued_at,
    )

    assert first_token.value != second_token.value
    assert first_token.digest != second_token.digest


def test_refresh_token_digest_is_stable() -> None:
    raw_token = "test-refresh-token-value"

    first_digest = digest_refresh_token(
        raw_token,
    )

    second_digest = digest_refresh_token(
        raw_token,
    )

    assert first_digest == second_digest
    assert len(first_digest) == 64


def test_refresh_token_digest_does_not_contain_token() -> None:
    generated_token = generate_refresh_token(
        now=current_test_time(),
    )

    assert generated_token.value not in generated_token.digest


def test_constant_time_digest_match_accepts_valid_token() -> None:
    raw_token = "valid-refresh-token"
    digest = digest_refresh_token(raw_token)

    assert constant_time_digest_matches(
        raw_token,
        digest,
    )


def test_constant_time_digest_match_rejects_invalid_token() -> None:
    digest = digest_refresh_token(
        "valid-refresh-token",
    )

    assert not constant_time_digest_matches(
        "different-refresh-token",
        digest,
    )


def test_digest_rejects_empty_token() -> None:
    with pytest.raises(
        ValueError,
        match="Refresh token must not be empty",
    ):
        digest_refresh_token("")
