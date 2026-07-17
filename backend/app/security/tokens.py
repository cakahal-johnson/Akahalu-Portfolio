import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from jwt import InvalidTokenError

from app.core.config import settings


class TokenValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class AccessToken:
    value: str
    token_id: UUID
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class RefreshTokenValue:
    value: str
    digest: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class DecodedAccessToken:
    user_id: UUID
    session_id: UUID
    token_id: UUID
    issued_at: datetime
    expires_at: datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def create_access_token(
    *,
    user_id: UUID,
    session_id: UUID,
    now: datetime | None = None,
) -> AccessToken:
    issued_at = now or utc_now()
    expires_at = issued_at + timedelta(
        minutes=settings.access_token_expire_minutes,
    )
    token_id = uuid4()

    payload = {
        "sub": str(user_id),
        "sid": str(session_id),
        "jti": str(token_id),
        "iat": issued_at,
        "nbf": issued_at,
        "exp": expires_at,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "typ": "access",
    }

    encoded_token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return AccessToken(
        value=encoded_token,
        token_id=token_id,
        expires_at=expires_at,
    )


def decode_access_token(
    token: str,
) -> DecodedAccessToken:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
            options={
                "require": [
                    "sub",
                    "sid",
                    "jti",
                    "iat",
                    "nbf",
                    "exp",
                    "iss",
                    "aud",
                    "typ",
                ],
            },
        )
    except InvalidTokenError as exc:
        raise TokenValidationError("Invalid or expired access token.") from exc

    if payload.get("typ") != "access":
        raise TokenValidationError("Unexpected token type.")

    try:
        user_id = UUID(payload["sub"])
        session_id = UUID(payload["sid"])
        token_id = UUID(payload["jti"])

        issued_at = datetime.fromtimestamp(
            payload["iat"],
            tz=UTC,
        )

        expires_at = datetime.fromtimestamp(
            payload["exp"],
            tz=UTC,
        )
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise TokenValidationError("Access token claims are malformed.") from exc

    return DecodedAccessToken(
        user_id=user_id,
        session_id=session_id,
        token_id=token_id,
        issued_at=issued_at,
        expires_at=expires_at,
    )


def generate_refresh_token(
    *,
    now: datetime | None = None,
) -> RefreshTokenValue:
    issued_at = now or utc_now()
    expires_at = issued_at + timedelta(
        days=settings.refresh_token_expire_days,
    )

    raw_token = secrets.token_urlsafe(64)

    return RefreshTokenValue(
        value=raw_token,
        digest=digest_refresh_token(raw_token),
        expires_at=expires_at,
    )


def digest_refresh_token(
    token: str,
) -> str:
    if not token:
        raise ValueError("Refresh token must not be empty.")

    return hashlib.sha256(
        token.encode("utf-8"),
    ).hexdigest()


def constant_time_digest_matches(
    raw_token: str,
    expected_digest: str,
) -> bool:
    if not raw_token or not expected_digest:
        return False

    actual_digest = digest_refresh_token(
        raw_token,
    )

    return secrets.compare_digest(
        actual_digest,
        expected_digest,
    )
