from typing import Annotated, NoReturn

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authorization import require_permission
from app.db.dependencies import get_db_session
from app.models.user import User
from app.schemas.portfolio import (
    ProfileAdminRead,
    ProfileCreate,
    ProfileDeleteRequest,
    ProfileRestoreRequest,
    ProfileUpdate,
    ProfileVisibilityUpdate,
)
from app.services.portfolio import (
    ProfileAlreadyExistsError,
    ProfileDeletedError,
    ProfileNotFoundError,
    ProfileValidationError,
    profile_service,
)


router = APIRouter(
    prefix="/admin/portfolio/profile",
    tags=["Admin Portfolio Profile"],
)


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


ProfileReader = Annotated[
    User,
    Depends(
        require_permission(
            "profile.read",
        )
    ),
]


ProfileCreator = Annotated[
    User,
    Depends(
        require_permission(
            "profile.create",
        )
    ),
]


ProfileUpdater = Annotated[
    User,
    Depends(
        require_permission(
            "profile.update",
        )
    ),
]


ProfileDeleter = Annotated[
    User,
    Depends(
        require_permission(
            "profile.delete",
        )
    ),
]


IncludeDeletedQuery = Annotated[
    bool,
    Query(
        description="Include the soft-deleted singleton profile.",
    ),
]


def raise_profile_error(
    exception: Exception,
) -> NoReturn:
    """Translate profile service exceptions into API responses."""

    if isinstance(
        exception,
        ProfileNotFoundError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "profile_not_found",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ProfileDeletedError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "profile_deleted",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ProfileAlreadyExistsError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "profile_already_exists",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ProfileValidationError,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "code": "profile_validation_error",
                "message": str(exception),
            },
        ) from exception

    raise exception


@router.get(
    "",
    response_model=ProfileAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Get the portfolio profile for administration",
)
async def get_admin_profile(
    _: ProfileReader,
    database_session: DatabaseSession,
    include_deleted: IncludeDeletedQuery = False,
) -> ProfileAdminRead:
    """Return the singleton portfolio profile for administration."""

    try:
        profile = await profile_service.get_admin(
            database_session,
            include_deleted=include_deleted,
        )
    except (
        ProfileNotFoundError,
        ProfileDeletedError,
    ) as exc:
        raise_profile_error(
            exc,
        )

    return ProfileAdminRead.model_validate(
        profile,
    )


@router.post(
    "",
    response_model=ProfileAdminRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create the portfolio profile",
)
async def create_admin_profile(
    payload: ProfileCreate,
    current_user: ProfileCreator,
    database_session: DatabaseSession,
) -> ProfileAdminRead:
    """Create the singleton portfolio profile."""

    try:
        profile = await profile_service.create(
            database_session,
            payload,
            actor_user_id=current_user.id,
        )
    except (
        ProfileAlreadyExistsError,
        ProfileDeletedError,
        ProfileValidationError,
    ) as exc:
        raise_profile_error(
            exc,
        )

    return ProfileAdminRead.model_validate(
        profile,
    )


@router.patch(
    "",
    response_model=ProfileAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update the portfolio profile",
)
async def update_admin_profile(
    payload: ProfileUpdate,
    current_user: ProfileUpdater,
    database_session: DatabaseSession,
) -> ProfileAdminRead:
    """Update content and metadata on the active portfolio profile."""

    try:
        profile = await profile_service.update(
            database_session,
            payload,
            actor_user_id=current_user.id,
        )
    except (
        ProfileNotFoundError,
        ProfileDeletedError,
        ProfileValidationError,
    ) as exc:
        raise_profile_error(
            exc,
        )

    return ProfileAdminRead.model_validate(
        profile,
    )


@router.patch(
    "/visibility",
    response_model=ProfileAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update portfolio profile visibility",
)
async def update_admin_profile_visibility(
    payload: ProfileVisibilityUpdate,
    current_user: ProfileUpdater,
    database_session: DatabaseSession,
) -> ProfileAdminRead:
    """Enable or disable public access to the profile."""

    del payload.reason

    try:
        profile = await profile_service.set_visibility(
            database_session,
            is_public=payload.is_public,
            actor_user_id=current_user.id,
        )
    except (
        ProfileNotFoundError,
        ProfileDeletedError,
    ) as exc:
        raise_profile_error(
            exc,
        )

    return ProfileAdminRead.model_validate(
        profile,
    )


@router.delete(
    "",
    response_model=ProfileAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete the portfolio profile",
)
async def delete_admin_profile(
    payload: ProfileDeleteRequest,
    current_user: ProfileDeleter,
    database_session: DatabaseSession,
) -> ProfileAdminRead:
    """Soft-delete the singleton profile and disable public visibility."""

    del payload.reason

    try:
        profile = await profile_service.soft_delete(
            database_session,
            actor_user_id=current_user.id,
        )
    except (
        ProfileNotFoundError,
        ProfileDeletedError,
    ) as exc:
        raise_profile_error(
            exc,
        )

    return ProfileAdminRead.model_validate(
        profile,
    )


@router.post(
    "/restore",
    response_model=ProfileAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Restore the portfolio profile",
)
async def restore_admin_profile(
    payload: ProfileRestoreRequest,
    current_user: ProfileUpdater,
    database_session: DatabaseSession,
) -> ProfileAdminRead:
    """Restore the soft-deleted singleton portfolio profile."""

    del payload.reason

    try:
        profile = await profile_service.restore(
            database_session,
            restore_as_public=payload.restore_as_public,
            actor_user_id=current_user.id,
        )
    except ProfileNotFoundError as exc:
        raise_profile_error(
            exc,
        )

    return ProfileAdminRead.model_validate(
        profile,
    )
