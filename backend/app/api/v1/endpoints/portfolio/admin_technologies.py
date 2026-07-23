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

from app.api.dependencies.authorization import (
    require_permission,
)
from app.db.dependencies import get_db_session
from app.models.user import User
from app.schemas.portfolio.project_technology import (
    AdminProjectTechnologyListResponse,
    ProjectTechnologyAdminRead,
    ProjectTechnologyCreate,
    ProjectTechnologyDeleteRequest,
    ProjectTechnologyRestoreRequest,
    ProjectTechnologyStatusUpdate,
    ProjectTechnologyUpdate,
)
from app.services.portfolio import (
    ProjectTechnologyConflictError,
    ProjectTechnologyInUseError,
    ProjectTechnologyNotFoundError,
    project_technology_service,
)


router = APIRouter(
    prefix="/admin/portfolio/technologies",
    tags=["Admin Portfolio Technologies"],
)


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


ProjectTechnologyReader = Annotated[
    User,
    Depends(
        require_permission(
            "projects.read",
        )
    ),
]


ProjectTechnologyCreator = Annotated[
    User,
    Depends(
        require_permission(
            "projects.create",
        )
    ),
]


ProjectTechnologyUpdater = Annotated[
    User,
    Depends(
        require_permission(
            "projects.update",
        )
    ),
]


ProjectTechnologyDeleter = Annotated[
    User,
    Depends(
        require_permission(
            "projects.delete",
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
        description="Number of technologies to return per page.",
    ),
]


SearchQuery = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=200,
        description=("Search technologies by name, slug, description or category."),
    ),
]


CategoryQuery = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=100,
        description="Filter technologies by category.",
    ),
]


ActiveQuery = Annotated[
    bool | None,
    Query(
        description="Filter technologies by their active status.",
    ),
]


IncludeDeletedQuery = Annotated[
    bool,
    Query(
        description="Include soft-deleted technologies.",
    ),
]


TechnologySortField = Literal[
    "sort_order",
    "name",
    "slug",
    "category",
    "created_at",
    "updated_at",
]


SortDirection = Literal[
    "asc",
    "desc",
]


SortByQuery = Annotated[
    TechnologySortField,
    Query(
        description="Field used to sort technology results.",
    ),
]


SortDirectionQuery = Annotated[
    SortDirection,
    Query(
        description="Direction used to sort technology results.",
    ),
]


def raise_technology_error(
    exception: Exception,
) -> NoReturn:
    """Translate technology service exceptions into API responses."""

    if isinstance(
        exception,
        ProjectTechnologyNotFoundError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "project_technology_not_found",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ProjectTechnologyInUseError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "project_technology_in_use",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ProjectTechnologyConflictError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "project_technology_conflict",
                "message": str(exception),
            },
        ) from exception

    raise exception


@router.get(
    "",
    response_model=AdminProjectTechnologyListResponse,
    status_code=status.HTTP_200_OK,
    summary="List portfolio technologies for administration",
)
async def list_admin_technologies(
    _: ProjectTechnologyReader,
    database_session: DatabaseSession,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    search: SearchQuery = None,
    category: CategoryQuery = None,
    is_active: ActiveQuery = None,
    include_deleted: IncludeDeletedQuery = False,
    sort_by: SortByQuery = "sort_order",
    sort_direction: SortDirectionQuery = "asc",
) -> AdminProjectTechnologyListResponse:
    """Return paginated portfolio technologies for administration."""

    technologies, total_items = await project_technology_service.list_for_admin(
        database_session,
        offset=(page - 1) * page_size,
        limit=page_size,
        search=search,
        category=category,
        is_active=is_active,
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

    return AdminProjectTechnologyListResponse(
        items=[
            ProjectTechnologyAdminRead.model_validate(
                technology,
            )
            for technology in technologies
        ],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next_page=page < total_pages,
        has_previous_page=page > 1,
    )


@router.get(
    "/{technology_id}",
    response_model=ProjectTechnologyAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Get a portfolio technology for administration",
)
async def get_admin_technology(
    technology_id: UUID,
    _: ProjectTechnologyReader,
    database_session: DatabaseSession,
    include_deleted: IncludeDeletedQuery = False,
) -> ProjectTechnologyAdminRead:
    """Return a portfolio technology by ID."""

    try:
        technology = await project_technology_service.get_by_id(
            database_session,
            technology_id,
            include_deleted=include_deleted,
        )
    except ProjectTechnologyNotFoundError as exc:
        raise_technology_error(
            exc,
        )

    return ProjectTechnologyAdminRead.model_validate(
        technology,
    )


@router.post(
    "",
    response_model=ProjectTechnologyAdminRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a portfolio technology",
)
async def create_admin_technology(
    payload: ProjectTechnologyCreate,
    _: ProjectTechnologyCreator,
    database_session: DatabaseSession,
) -> ProjectTechnologyAdminRead:
    """Create a new portfolio technology."""

    try:
        technology = await project_technology_service.create(
            database_session,
            payload,
        )
    except ProjectTechnologyConflictError as exc:
        raise_technology_error(
            exc,
        )

    return ProjectTechnologyAdminRead.model_validate(
        technology,
    )


@router.patch(
    "/{technology_id}",
    response_model=ProjectTechnologyAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a portfolio technology",
)
async def update_admin_technology(
    technology_id: UUID,
    payload: ProjectTechnologyUpdate,
    _: ProjectTechnologyUpdater,
    database_session: DatabaseSession,
) -> ProjectTechnologyAdminRead:
    """Update an existing portfolio technology."""

    try:
        technology = await project_technology_service.update(
            database_session,
            technology_id,
            payload,
        )
    except (
        ProjectTechnologyNotFoundError,
        ProjectTechnologyConflictError,
    ) as exc:
        raise_technology_error(
            exc,
        )

    return ProjectTechnologyAdminRead.model_validate(
        technology,
    )


@router.patch(
    "/{technology_id}/status",
    response_model=ProjectTechnologyAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a portfolio technology status",
)
async def update_admin_technology_status(
    technology_id: UUID,
    payload: ProjectTechnologyStatusUpdate,
    _: ProjectTechnologyUpdater,
    database_session: DatabaseSession,
) -> ProjectTechnologyAdminRead:
    """Activate or deactivate a portfolio technology."""

    try:
        technology = await project_technology_service.set_active(
            database_session,
            technology_id,
            is_active=payload.is_active,
        )
    except ProjectTechnologyNotFoundError as exc:
        raise_technology_error(
            exc,
        )

    return ProjectTechnologyAdminRead.model_validate(
        technology,
    )


@router.delete(
    "/{technology_id}",
    response_model=ProjectTechnologyAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a portfolio technology",
)
async def delete_admin_technology(
    technology_id: UUID,
    payload: ProjectTechnologyDeleteRequest,
    _: ProjectTechnologyDeleter,
    database_session: DatabaseSession,
) -> ProjectTechnologyAdminRead:
    """
    Soft-delete a portfolio technology.

    Technologies assigned to projects cannot be deleted until those
    project assignments are changed.
    """

    del payload

    try:
        technology = await project_technology_service.soft_delete(
            database_session,
            technology_id,
            allow_if_assigned=False,
        )
    except (
        ProjectTechnologyNotFoundError,
        ProjectTechnologyInUseError,
    ) as exc:
        raise_technology_error(
            exc,
        )

    return ProjectTechnologyAdminRead.model_validate(
        technology,
    )


@router.post(
    "/{technology_id}/restore",
    response_model=ProjectTechnologyAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Restore a portfolio technology",
)
async def restore_admin_technology(
    technology_id: UUID,
    payload: ProjectTechnologyRestoreRequest,
    _: ProjectTechnologyUpdater,
    database_session: DatabaseSession,
) -> ProjectTechnologyAdminRead:
    """Restore a previously soft-deleted portfolio technology."""

    try:
        technology = await project_technology_service.restore(
            database_session,
            technology_id,
        )

        if technology.is_active != payload.activate:
            technology = await project_technology_service.set_active(
                database_session,
                technology_id,
                is_active=payload.activate,
            )
    except (
        ProjectTechnologyNotFoundError,
        ProjectTechnologyConflictError,
    ) as exc:
        raise_technology_error(
            exc,
        )

    return ProjectTechnologyAdminRead.model_validate(
        technology,
    )
