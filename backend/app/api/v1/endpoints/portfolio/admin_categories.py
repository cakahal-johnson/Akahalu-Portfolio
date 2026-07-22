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
from app.schemas.portfolio.project_category import (
    AdminProjectCategoryListResponse,
    ProjectCategoryAdminRead,
    ProjectCategoryCreate,
    ProjectCategoryDeleteRequest,
    ProjectCategoryRestoreRequest,
    ProjectCategoryStatusUpdate,
    ProjectCategoryUpdate,
)
from app.services.portfolio import (
    ProjectCategoryConflictError,
    ProjectCategoryInUseError,
    ProjectCategoryNotFoundError,
    project_category_service,
)


router = APIRouter(
    prefix="/admin/portfolio/categories",
    tags=["Admin Portfolio Categories"],
)


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


ProjectCategoryReader = Annotated[
    User,
    Depends(
        require_permission(
            "projects.read",
        )
    ),
]


ProjectCategoryCreator = Annotated[
    User,
    Depends(
        require_permission(
            "projects.create",
        )
    ),
]


ProjectCategoryUpdater = Annotated[
    User,
    Depends(
        require_permission(
            "projects.update",
        )
    ),
]


ProjectCategoryDeleter = Annotated[
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
        description="Number of categories to return per page.",
    ),
]


SearchQuery = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=200,
        description="Search categories by name, slug or description.",
    ),
]


ActiveQuery = Annotated[
    bool | None,
    Query(
        description="Filter categories by their active status.",
    ),
]


IncludeDeletedQuery = Annotated[
    bool,
    Query(
        description="Include soft-deleted categories.",
    ),
]


CategorySortField = Literal[
    "sort_order",
    "name",
    "slug",
    "created_at",
    "updated_at",
]


SortDirection = Literal[
    "asc",
    "desc",
]


SortByQuery = Annotated[
    CategorySortField,
    Query(
        description="Field used to sort category results.",
    ),
]


SortDirectionQuery = Annotated[
    SortDirection,
    Query(
        description="Direction used to sort category results.",
    ),
]


def raise_category_error(
    exception: Exception,
) -> NoReturn:
    """Translate category service exceptions into API responses."""

    if isinstance(
        exception,
        ProjectCategoryNotFoundError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "project_category_not_found",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ProjectCategoryInUseError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "project_category_in_use",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ProjectCategoryConflictError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "project_category_conflict",
                "message": str(exception),
            },
        ) from exception

    raise exception


@router.get(
    "",
    response_model=AdminProjectCategoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List portfolio categories for administration",
)
async def list_admin_categories(
    _: ProjectCategoryReader,
    database_session: DatabaseSession,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    search: SearchQuery = None,
    is_active: ActiveQuery = None,
    include_deleted: IncludeDeletedQuery = False,
    sort_by: SortByQuery = "sort_order",
    sort_direction: SortDirectionQuery = "asc",
) -> AdminProjectCategoryListResponse:
    """Return paginated portfolio categories for administration."""

    categories, total_items = await project_category_service.list_for_admin(
        database_session,
        offset=(page - 1) * page_size,
        limit=page_size,
        search=search,
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

    return AdminProjectCategoryListResponse(
        items=[
            ProjectCategoryAdminRead.model_validate(
                category,
            )
            for category in categories
        ],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next_page=page < total_pages,
        has_previous_page=page > 1,
    )


@router.get(
    "/{category_id}",
    response_model=ProjectCategoryAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Get a portfolio category for administration",
)
async def get_admin_category(
    category_id: UUID,
    _: ProjectCategoryReader,
    database_session: DatabaseSession,
    include_deleted: IncludeDeletedQuery = False,
) -> ProjectCategoryAdminRead:
    """Return a portfolio category by ID."""

    try:
        category = await project_category_service.get_by_id(
            database_session,
            category_id,
            include_deleted=include_deleted,
        )
    except ProjectCategoryNotFoundError as exc:
        raise_category_error(
            exc,
        )

    return ProjectCategoryAdminRead.model_validate(
        category,
    )


@router.post(
    "",
    response_model=ProjectCategoryAdminRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a portfolio category",
)
async def create_admin_category(
    payload: ProjectCategoryCreate,
    _: ProjectCategoryCreator,
    database_session: DatabaseSession,
) -> ProjectCategoryAdminRead:
    """Create a new portfolio category."""

    try:
        category = await project_category_service.create(
            database_session,
            payload,
        )
    except ProjectCategoryConflictError as exc:
        raise_category_error(
            exc,
        )

    return ProjectCategoryAdminRead.model_validate(
        category,
    )


@router.patch(
    "/{category_id}",
    response_model=ProjectCategoryAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a portfolio category",
)
async def update_admin_category(
    category_id: UUID,
    payload: ProjectCategoryUpdate,
    _: ProjectCategoryUpdater,
    database_session: DatabaseSession,
) -> ProjectCategoryAdminRead:
    """Update an existing portfolio category."""

    try:
        category = await project_category_service.update(
            database_session,
            category_id,
            payload,
        )
    except (
        ProjectCategoryNotFoundError,
        ProjectCategoryConflictError,
    ) as exc:
        raise_category_error(
            exc,
        )

    return ProjectCategoryAdminRead.model_validate(
        category,
    )


@router.patch(
    "/{category_id}/status",
    response_model=ProjectCategoryAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a portfolio category status",
)
async def update_admin_category_status(
    category_id: UUID,
    payload: ProjectCategoryStatusUpdate,
    _: ProjectCategoryUpdater,
    database_session: DatabaseSession,
) -> ProjectCategoryAdminRead:
    """Activate or deactivate a portfolio category."""

    try:
        category = await project_category_service.set_active(
            database_session,
            category_id,
            is_active=payload.is_active,
        )
    except ProjectCategoryNotFoundError as exc:
        raise_category_error(
            exc,
        )

    return ProjectCategoryAdminRead.model_validate(
        category,
    )


@router.delete(
    "/{category_id}",
    response_model=ProjectCategoryAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a portfolio category",
)
async def delete_admin_category(
    category_id: UUID,
    payload: ProjectCategoryDeleteRequest,
    _: ProjectCategoryDeleter,
    database_session: DatabaseSession,
) -> ProjectCategoryAdminRead:
    """
    Soft-delete a portfolio category.

    Categories assigned to projects cannot be deleted until those
    project assignments are changed.
    """

    del payload

    try:
        category = await project_category_service.soft_delete(
            database_session,
            category_id,
            allow_if_assigned=False,
        )
    except (
        ProjectCategoryNotFoundError,
        ProjectCategoryInUseError,
    ) as exc:
        raise_category_error(
            exc,
        )

    return ProjectCategoryAdminRead.model_validate(
        category,
    )


@router.post(
    "/{category_id}/restore",
    response_model=ProjectCategoryAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Restore a portfolio category",
)
async def restore_admin_category(
    category_id: UUID,
    payload: ProjectCategoryRestoreRequest,
    _: ProjectCategoryUpdater,
    database_session: DatabaseSession,
) -> ProjectCategoryAdminRead:
    """Restore a previously soft-deleted portfolio category."""

    try:
        category = await project_category_service.restore(
            database_session,
            category_id,
        )

        if category.is_active != payload.activate:
            category = await project_category_service.set_active(
                database_session,
                category_id,
                is_active=payload.activate,
            )
    except (
        ProjectCategoryNotFoundError,
        ProjectCategoryConflictError,
    ) as exc:
        raise_category_error(
            exc,
        )

    return ProjectCategoryAdminRead.model_validate(
        category,
    )
