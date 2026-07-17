from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.models.user import User
from app.repositories.session_repository import (
    session_repository,
)
from app.security.tokens import (
    TokenValidationError,
    decode_access_token,
)

bearer_scheme = HTTPBearer(
    auto_error=False,
)


def authentication_exception(
    *,
    detail: str = "Authentication credentials are invalid.",
) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "invalid_authentication",
            "message": detail,
        },
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    database_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> User:
    if credentials is None:
        raise authentication_exception(
            detail="Authentication credentials were not provided.",
        )

    if credentials.scheme.lower() != "bearer":
        raise authentication_exception(
            detail="The authentication scheme must be Bearer.",
        )

    try:
        token_claims = decode_access_token(
            credentials.credentials,
        )
    except TokenValidationError as exc:
        raise authentication_exception(
            detail="The access token is invalid or expired.",
        ) from exc

    authentication_session = await session_repository.get_active_by_id(
        database_session,
        token_claims.session_id,
    )

    if authentication_session is None:
        raise authentication_exception(
            detail="The authentication session is invalid or expired.",
        )

    if authentication_session.user_id != token_claims.user_id:
        raise authentication_exception(
            detail="The access token does not match its session.",
        )

    user = authentication_session.user

    if not user.is_active or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "account_disabled",
                "message": "This account is disabled.",
            },
        )

    return user


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]
