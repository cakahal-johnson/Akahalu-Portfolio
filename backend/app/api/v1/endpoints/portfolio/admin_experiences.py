from math import ceil
from typing import Annotated, Literal, NoReturn
from uuid import UUID

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
from app.schemas.portfolio.experience import (
    AdminExperienceListResponse,
    EmploymentType,
    ExperienceAdminRead,
    ExperienceCreate,
    ExperienceDeleteRequest,
    ExperienceFeaturedUpdate,
    ExperienceLocationType,
    ExperienceRestoreRequest,
    ExperienceUpdate,
    ExperienceVisibilityUpdate,
)
from app.services.portfolio.experience_service import (
    ExperienceConflictError,
    ExperienceLifecycleError,
    ExperienceNotFoundError,
    experience_service,
)


router = APIRouter(
    prefix="/admin/portfolio/experiences",
    tags=["Admin Portfolio Experiences"],
)


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


ExperienceReader = Annotated[
    User,
    Depends(
        require_permission(
            "experience.read",
        )
    ),
]


ExperienceCreator = Annotated[
    User,
    Depends(
        require_permission(
            "experience.create",
        )
    ),
]


ExperienceUpdater = Annotated[
    User,
    Depends(
        require_permission(
            "experience.update",
        )
    ),
]


ExperienceDeleter = Annotated[
    User,
    Depends(
        require_permission(
            "experience.delete",
        )
    ),
]


PageQuery = Annotated[
    int,
    Query(
        ge=1,
        description="Page number to return.",
    ),
]


PageSizeQuery = Annotated[
    int,
    Query(
        ge=1,
        le=100,
        description="Number of experiences to return per page.",
    ),
]


SearchQuery = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=200,
        description=(
            "Search experiences by company, job title, slug, location, "
            "summary, responsibilities, or achievements."
        ),
    ),
]


EmploymentTypeQuery = Annotated[
    EmploymentType | None,
    Query(
        description="Filter experiences by employment type.",
    ),
]


LocationTypeQuery = Annotated[
    ExperienceLocationType | None,
    Query(
        description="Filter experiences by work-location arrangement.",
    ),
]


CurrentQuery = Annotated[
    bool | None,
    Query(
        description="Filter experiences by current-position status.",
    ),
]


PublicQuery = Annotated[
    bool | None,
    Query(
        description="Filter experiences by public visibility.",
    ),
]


FeaturedQuery = Annotated[
    bool | None,
    Query(
        description="Filter experiences by featured status.",
    ),
]


IncludeDeletedQuery = Annotated[
    bool,
    Query(
        description="Include soft-deleted experiences.",
    ),
]


ExperienceSortField = Literal[
    "company_name",
    "job_title",
    "slug",
    "employment_type",
    "location_type",
    "start_date",
    "end_date",
    "is_current",
    "is_public",
    "is_featured",
    "sort_order",
    "created_at",
    "updated_at",
]


SortDirection = Literal[
    "asc",
    "desc",
]


SortByQuery = Annotated[
    ExperienceSortField,
    Query(
        description="Field used to sort experience results.",
    ),
]


SortDirectionQuery = Annotated[
    SortDirection,
    Query(
        description="Direction used to sort experience results.",
    ),
]


def raise_experience_error(
    exception: Exception,
) -> NoReturn:
    """Translate experience service exceptions into API responses."""

    if isinstance(
        exception,
        ExperienceNotFoundError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "experience_not_found",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ExperienceConflictError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "experience_conflict",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ExperienceLifecycleError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "experience_lifecycle_conflict",
                "message": str(exception),
            },
        ) from exception

    raise exception


@router.get(
    "",
    response_model=AdminExperienceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List portfolio experiences for administration",
)
async def list_admin_experiences(
    _: ExperienceReader,
    database_session: DatabaseSession,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    search: SearchQuery = None,
    employment_type: EmploymentTypeQuery = None,
    location_type: LocationTypeQuery = None,
    is_current: CurrentQuery = None,
    is_public: PublicQuery = None,
    is_featured: FeaturedQuery = None,
    include_deleted: IncludeDeletedQuery = False,
    sort_by: SortByQuery = "start_date",
    sort_direction: SortDirectionQuery = "desc",
) -> AdminExperienceListResponse:
    """Return paginated portfolio experiences for administration."""

    experiences, total_items = await experience_service.list_for_admin(
        database_session,
        offset=(page - 1) * page_size,
        limit=page_size,
        search=search,
        employment_type=(
            employment_type.value if employment_type is not None else None
        ),
        location_type=(location_type.value if location_type is not None else None),
        is_current=is_current,
        is_public=is_public,
        is_featured=is_featured,
        include_deleted=include_deleted,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )

    total_pages = (
        ceil(
            total_items / page_size,
        )
        if total_items > 0
        else 0
    )

    return AdminExperienceListResponse(
        items=[
            ExperienceAdminRead.model_validate(
                experience,
            )
            for experience in experiences
        ],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next_page=page < total_pages,
        has_previous_page=page > 1,
    )


@router.get(
    "/{experience_id}",
    response_model=ExperienceAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Get a portfolio experience for administration",
)
async def get_admin_experience(
    experience_id: UUID,
    _: ExperienceReader,
    database_session: DatabaseSession,
    include_deleted: IncludeDeletedQuery = False,
) -> ExperienceAdminRead:
    """Return a portfolio experience by ID."""

    try:
        experience = await experience_service.get_by_id(
            database_session,
            experience_id,
            include_deleted=include_deleted,
        )
    except ExperienceNotFoundError as exc:
        raise_experience_error(
            exc,
        )

    return ExperienceAdminRead.model_validate(
        experience,
    )


@router.post(
    "",
    response_model=ExperienceAdminRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a portfolio experience",
)
async def create_admin_experience(
    payload: ExperienceCreate,
    current_user: ExperienceCreator,
    database_session: DatabaseSession,
) -> ExperienceAdminRead:
    """Create a new portfolio experience."""

    try:
        experience = await experience_service.create(
            database_session,
            payload,
            actor_user_id=current_user.id,
        )
    except (
        ExperienceConflictError,
        ExperienceLifecycleError,
    ) as exc:
        raise_experience_error(
            exc,
        )

    return ExperienceAdminRead.model_validate(
        experience,
    )


@router.patch(
    "/{experience_id}",
    response_model=ExperienceAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a portfolio experience",
)
async def update_admin_experience(
    experience_id: UUID,
    payload: ExperienceUpdate,
    current_user: ExperienceUpdater,
    database_session: DatabaseSession,
) -> ExperienceAdminRead:
    """Update an existing portfolio experience."""

    try:
        experience = await experience_service.update(
            database_session,
            experience_id,
            payload,
            actor_user_id=current_user.id,
        )
    except (
        ExperienceNotFoundError,
        ExperienceConflictError,
        ExperienceLifecycleError,
    ) as exc:
        raise_experience_error(
            exc,
        )

    return ExperienceAdminRead.model_validate(
        experience,
    )


@router.patch(
    "/{experience_id}/visibility",
    response_model=ExperienceAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update portfolio experience visibility",
)
async def update_admin_experience_visibility(
    experience_id: UUID,
    payload: ExperienceVisibilityUpdate,
    current_user: ExperienceUpdater,
    database_session: DatabaseSession,
) -> ExperienceAdminRead:
    """Show or hide a portfolio experience publicly."""

    try:
        experience = await experience_service.set_visibility(
            database_session,
            experience_id,
            is_public=payload.is_public,
            actor_user_id=current_user.id,
        )
    except ExperienceNotFoundError as exc:
        raise_experience_error(
            exc,
        )

    return ExperienceAdminRead.model_validate(
        experience,
    )


@router.patch(
    "/{experience_id}/featured",
    response_model=ExperienceAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update portfolio experience featured status",
)
async def update_admin_experience_featured(
    experience_id: UUID,
    payload: ExperienceFeaturedUpdate,
    current_user: ExperienceUpdater,
    database_session: DatabaseSession,
) -> ExperienceAdminRead:
    """Feature or unfeature a public portfolio experience."""

    try:
        experience = await experience_service.set_featured(
            database_session,
            experience_id,
            is_featured=payload.is_featured,
            actor_user_id=current_user.id,
        )
    except (
        ExperienceNotFoundError,
        ExperienceLifecycleError,
    ) as exc:
        raise_experience_error(
            exc,
        )

    return ExperienceAdminRead.model_validate(
        experience,
    )


@router.delete(
    "/{experience_id}",
    response_model=ExperienceAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a portfolio experience",
)
async def delete_admin_experience(
    experience_id: UUID,
    payload: ExperienceDeleteRequest,
    current_user: ExperienceDeleter,
    database_session: DatabaseSession,
) -> ExperienceAdminRead:
    """Soft-delete a portfolio experience."""

    del payload

    try:
        experience = await experience_service.soft_delete(
            database_session,
            experience_id,
            actor_user_id=current_user.id,
        )
    except ExperienceNotFoundError as exc:
        raise_experience_error(
            exc,
        )

    return ExperienceAdminRead.model_validate(
        experience,
    )


@router.post(
    "/{experience_id}/restore",
    response_model=ExperienceAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Restore a portfolio experience",
)
async def restore_admin_experience(
    experience_id: UUID,
    payload: ExperienceRestoreRequest,
    current_user: ExperienceUpdater,
    database_session: DatabaseSession,
) -> ExperienceAdminRead:
    """Restore a previously soft-deleted portfolio experience."""

    try:
        experience = await experience_service.restore(
            database_session,
            experience_id,
            actor_user_id=current_user.id,
            make_public=payload.make_public,
        )
    except (
        ExperienceNotFoundError,
        ExperienceConflictError,
        ExperienceLifecycleError,
    ) as exc:
        raise_experience_error(
            exc,
        )

    return ExperienceAdminRead.model_validate(
        experience,
    )
