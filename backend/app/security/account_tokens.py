from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from hmac import compare_digest
from secrets import token_urlsafe


DEFAULT_TOKEN_BYTES = 48


@dataclass(frozen=True, slots=True)
class AccountToken:
    raw_token: str
    digest: str
    expires_at: datetime


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_account_token(
    *,
    lifetime: timedelta,
    token_bytes: int = DEFAULT_TOKEN_BYTES,
) -> AccountToken:
    if lifetime <= timedelta(0):
        raise ValueError("Token lifetime must be greater than zero.")

    if token_bytes < 32:
        raise ValueError("Account tokens must contain at least 32 random bytes.")

    raw_token = token_urlsafe(token_bytes)

    return AccountToken(
        raw_token=raw_token,
        digest=digest_account_token(raw_token),
        expires_at=utc_now() + lifetime,
    )


def digest_account_token(raw_token: str) -> str:
    normalized_token = raw_token.strip()

    if not normalized_token:
        raise ValueError("Account token cannot be empty.")

    return sha256(normalized_token.encode("utf-8")).hexdigest()


def account_token_digest_matches(
    raw_token: str,
    expected_digest: str,
) -> bool:
    if not raw_token.strip() or not expected_digest.strip():
        return False

    actual_digest = digest_account_token(raw_token)

    return compare_digest(
        actual_digest,
        expected_digest,
    )
