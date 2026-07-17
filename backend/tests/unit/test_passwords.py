import pytest

from app.security.passwords import (
    hash_password,
    verify_and_update_password,
    verify_password,
)


TEST_PASSWORD = "StrongPassword!2026"


def test_hash_password_does_not_store_plain_text() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    assert password_hash != TEST_PASSWORD
    assert TEST_PASSWORD not in password_hash


def test_hash_password_generates_unique_salts() -> None:
    first_hash = hash_password(TEST_PASSWORD)
    second_hash = hash_password(TEST_PASSWORD)

    assert first_hash != second_hash


def test_hash_password_rejects_empty_password() -> None:
    with pytest.raises(
        ValueError,
        match="Password must not be empty",
    ):
        hash_password("")


def test_verify_password_accepts_correct_password() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    assert verify_password(
        TEST_PASSWORD,
        password_hash,
    )


def test_verify_password_rejects_incorrect_password() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    assert not verify_password(
        "IncorrectPassword!2026",
        password_hash,
    )


def test_verify_password_rejects_empty_values() -> None:
    assert not verify_password("", "stored-hash")
    assert not verify_password(TEST_PASSWORD, "")


def test_verify_and_update_accepts_current_hash() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    result = verify_and_update_password(
        TEST_PASSWORD,
        password_hash,
    )

    assert result.is_valid
    assert not result.needs_rehash
    assert result.updated_hash is None


def test_verify_and_update_rejects_incorrect_password() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    result = verify_and_update_password(
        "IncorrectPassword!2026",
        password_hash,
    )

    assert not result.is_valid
    assert not result.needs_rehash
    assert result.updated_hash is None


def test_verify_and_update_rejects_empty_values() -> None:
    result = verify_and_update_password(
        "",
        "",
    )

    assert not result.is_valid
    assert result.updated_hash is None
