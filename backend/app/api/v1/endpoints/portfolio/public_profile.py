from typing import Annotated, NoReturn

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.schemas.portfolio import ProfileRead
from app.services.portfolio import (
    ProfileNotFoundError,
    profile_service,
)


router = APIRouter(
    prefix="/portfolio/profile",
    tags=["Public Portfolio Profile"],
)


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


def raise_public_profile_error(
    exception: Exception,
) -> NoReturn:
    """Translate public profile service errors into API responses."""

    if isinstance(
        exception,
        ProfileNotFoundError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "public_profile_not_found",
                "message": str(exception),
            },
        ) from exception

    raise exception


@router.get(
    "",
    response_model=ProfileRead,
    status_code=status.HTTP_200_OK,
    summary="Get the public portfolio profile",
)
async def get_public_profile(
    database_session: DatabaseSession,
) -> ProfileRead:
    """
    Return the publicly visible portfolio profile.

    Private, missing, and soft-deleted profiles are not exposed.
    """

    try:
        profile = await profile_service.get_public(
            database_session,
        )
    except ProfileNotFoundError as exc:
        raise_public_profile_error(
            exc,
        )

    return ProfileRead.model_validate(
        profile,
    )
