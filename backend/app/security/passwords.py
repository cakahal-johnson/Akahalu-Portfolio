from dataclasses import dataclass

from pwdlib import PasswordHash


password_hasher = PasswordHash.recommended()


@dataclass(frozen=True, slots=True)
class PasswordVerificationResult:
    is_valid: bool
    updated_hash: str | None = None

    @property
    def needs_rehash(self) -> bool:
        return self.updated_hash is not None


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password must not be empty.")

    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    if not plain_password or not password_hash:
        return False

    return password_hasher.verify(
        plain_password,
        password_hash,
    )


def verify_and_update_password(
    plain_password: str,
    password_hash: str,
) -> PasswordVerificationResult:
    if not plain_password or not password_hash:
        return PasswordVerificationResult(
            is_valid=False,
        )

    is_valid, updated_hash = password_hasher.verify_and_update(
        plain_password,
        password_hash,
    )

    return PasswordVerificationResult(
        is_valid=is_valid,
        updated_hash=updated_hash,
    )
