from datetime import timedelta

import pytest

from app.security.account_tokens import (
    account_token_digest_matches,
    digest_account_token,
    generate_account_token,
    utc_now,
)


def test_generate_account_token_creates_secure_token() -> None:
    token = generate_account_token(
        lifetime=timedelta(minutes=30),
    )

    assert token.raw_token
    assert len(token.digest) == 64
    assert token.raw_token not in token.digest
    assert token.expires_at > utc_now()


def test_generate_account_tokens_are_unique() -> None:
    first_token = generate_account_token(
        lifetime=timedelta(minutes=30),
    )
    second_token = generate_account_token(
        lifetime=timedelta(minutes=30),
    )

    assert first_token.raw_token != second_token.raw_token
    assert first_token.digest != second_token.digest


def test_digest_account_token_is_stable() -> None:
    raw_token = "secure-account-token"

    assert digest_account_token(raw_token) == digest_account_token(raw_token)


def test_digest_account_token_rejects_empty_value() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        digest_account_token("   ")


def test_generate_account_token_rejects_invalid_lifetime() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        generate_account_token(
            lifetime=timedelta(0),
        )


def test_generate_account_token_rejects_weak_size() -> None:
    with pytest.raises(
        ValueError,
        match="at least 32",
    ):
        generate_account_token(
            lifetime=timedelta(minutes=30),
            token_bytes=16,
        )


def test_account_token_digest_matches_valid_token() -> None:
    raw_token = "valid-account-token"
    digest = digest_account_token(raw_token)

    assert account_token_digest_matches(
        raw_token,
        digest,
    )


def test_account_token_digest_rejects_invalid_token() -> None:
    digest = digest_account_token("valid-account-token")

    assert not account_token_digest_matches(
        "invalid-account-token",
        digest,
    )


def test_account_token_digest_rejects_empty_values() -> None:
    assert not account_token_digest_matches("", "digest")
    assert not account_token_digest_matches("token", "")
