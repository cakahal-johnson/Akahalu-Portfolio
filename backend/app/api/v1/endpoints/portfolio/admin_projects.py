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
from app.schemas.portfolio import (
    AdminProjectListResponse,
    ProjectAdminRead,
    ProjectCreate,
    ProjectDeleteRequest,
    ProjectFeaturedUpdate,
    ProjectRestoreRequest,
    ProjectStatus,
    ProjectStatusUpdate,
    ProjectUpdate,
    ProjectVisibility,
    ProjectVisibilityUpdate,
)
from app.services.portfolio import (
    ProjectCategoryUnavailableError,
    ProjectConflictError,
    ProjectNotFoundError,
    ProjectPublicationError,
    ProjectSelectedCategoryNotFoundError,
    ProjectSelectedTechnologyNotFoundError,
    ProjectTechnologyUnavailableError,
    project_service,
)


router = APIRouter(
    prefix="/admin/portfolio/projects",
    tags=["Admin Portfolio Projects"],
)


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


ProjectReader = Annotated[
    User,
    Depends(
        require_permission(
            "projects.read",
        )
    ),
]


ProjectCreator = Annotated[
    User,
    Depends(
        require_permission(
            "projects.create",
        )
    ),
]


ProjectUpdater = Annotated[
    User,
    Depends(
        require_permission(
            "projects.update",
        )
    ),
]


ProjectDeleter = Annotated[
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
        description="Number of projects to return per page.",
    ),
]


SearchQuery = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=200,
        description=(
            "Search projects by title, slug, description, "
            "problem statement or solution summary."
        ),
    ),
]


CategoryIdQuery = Annotated[
    UUID | None,
    Query(
        description="Filter projects by category ID.",
    ),
]


TechnologyIdQuery = Annotated[
    UUID | None,
    Query(
        description="Filter projects by technology ID.",
    ),
]


StatusQuery = Annotated[
    ProjectStatus | None,
    Query(
        description="Filter projects by lifecycle status.",
    ),
]


VisibilityQuery = Annotated[
    ProjectVisibility | None,
    Query(
        description="Filter projects by visibility.",
    ),
]


FeaturedQuery = Annotated[
    bool | None,
    Query(
        description="Filter projects by featured state.",
    ),
]


IncludeDeletedQuery = Annotated[
    bool,
    Query(
        description="Include soft-deleted projects.",
    ),
]


ProjectSortField = Literal[
    "title",
    "slug",
    "status",
    "visibility",
    "is_featured",
    "sort_order",
    "started_at",
    "completed_at",
    "published_at",
    "created_at",
    "updated_at",
]


SortDirection = Literal[
    "asc",
    "desc",
]


SortByQuery = Annotated[
    ProjectSortField,
    Query(
        description="Field used to sort project results.",
    ),
]


SortDirectionQuery = Annotated[
    SortDirection,
    Query(
        description="Direction used to sort project results.",
    ),
]


def raise_project_error(
    exception: Exception,
) -> NoReturn:
    """Translate project service exceptions into API responses."""

    if isinstance(
        exception,
        ProjectNotFoundError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "project_not_found",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ProjectSelectedCategoryNotFoundError,
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
        ProjectSelectedTechnologyNotFoundError,
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
        ProjectCategoryUnavailableError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "project_category_unavailable",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ProjectTechnologyUnavailableError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "project_technology_unavailable",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ProjectPublicationError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "project_publication_error",
                "message": str(exception),
            },
        ) from exception

    if isinstance(
        exception,
        ProjectConflictError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "project_conflict",
                "message": str(exception),
            },
        ) from exception

    raise exception


@router.get(
    "",
    response_model=AdminProjectListResponse,
    status_code=status.HTTP_200_OK,
    summary="List portfolio projects for administration",
)
async def list_admin_projects(
    _: ProjectReader,
    database_session: DatabaseSession,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    search: SearchQuery = None,
    category_id: CategoryIdQuery = None,
    project_status: StatusQuery = None,
    visibility: VisibilityQuery = None,
    is_featured: FeaturedQuery = None,
    technology_id: TechnologyIdQuery = None,
    include_deleted: IncludeDeletedQuery = False,
    sort_by: SortByQuery = "created_at",
    sort_direction: SortDirectionQuery = "desc",
) -> AdminProjectListResponse:
    """Return paginated portfolio projects for administration."""

    projects, total_items = await project_service.list_for_admin(
        database_session,
        offset=(page - 1) * page_size,
        limit=page_size,
        search=search,
        category_id=category_id,
        status=(project_status.value if project_status is not None else None),
        visibility=(visibility.value if visibility is not None else None),
        is_featured=is_featured,
        technology_id=technology_id,
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

    return AdminProjectListResponse(
        items=[
            ProjectAdminRead.model_validate(
                project,
            )
            for project in projects
        ],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next_page=page < total_pages,
        has_previous_page=page > 1,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Get a portfolio project for administration",
)
async def get_admin_project(
    project_id: UUID,
    _: ProjectReader,
    database_session: DatabaseSession,
    include_deleted: IncludeDeletedQuery = False,
) -> ProjectAdminRead:
    """Return a portfolio project by ID."""

    try:
        project = await project_service.get_by_id(
            database_session,
            project_id,
            include_deleted=include_deleted,
        )
    except ProjectNotFoundError as exc:
        raise_project_error(
            exc,
        )

    return ProjectAdminRead.model_validate(
        project,
    )


@router.post(
    "",
    response_model=ProjectAdminRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a portfolio project",
)
async def create_admin_project(
    payload: ProjectCreate,
    current_user: ProjectCreator,
    database_session: DatabaseSession,
) -> ProjectAdminRead:
    """Create a portfolio project with optional technology assignments."""

    try:
        project = await project_service.create(
            database_session,
            payload,
            actor_user_id=current_user.id,
        )
    except (
        ProjectConflictError,
        ProjectSelectedCategoryNotFoundError,
        ProjectCategoryUnavailableError,
        ProjectSelectedTechnologyNotFoundError,
        ProjectTechnologyUnavailableError,
        ProjectPublicationError,
    ) as exc:
        raise_project_error(
            exc,
        )

    return ProjectAdminRead.model_validate(
        project,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a portfolio project",
)
async def update_admin_project(
    project_id: UUID,
    payload: ProjectUpdate,
    current_user: ProjectUpdater,
    database_session: DatabaseSession,
) -> ProjectAdminRead:
    """Update project content, category, state, and technologies."""

    try:
        project = await project_service.update(
            database_session,
            project_id,
            payload,
            actor_user_id=current_user.id,
        )
    except (
        ProjectNotFoundError,
        ProjectConflictError,
        ProjectSelectedCategoryNotFoundError,
        ProjectCategoryUnavailableError,
        ProjectSelectedTechnologyNotFoundError,
        ProjectTechnologyUnavailableError,
        ProjectPublicationError,
    ) as exc:
        raise_project_error(
            exc,
        )

    return ProjectAdminRead.model_validate(
        project,
    )


@router.patch(
    "/{project_id}/status",
    response_model=ProjectAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a portfolio project status",
)
async def update_admin_project_status(
    project_id: UUID,
    payload: ProjectStatusUpdate,
    current_user: ProjectUpdater,
    database_session: DatabaseSession,
) -> ProjectAdminRead:
    """Publish, unpublish, or archive a portfolio project."""

    del payload.reason

    try:
        if payload.status is ProjectStatus.PUBLISHED:
            project = await project_service.publish(
                database_session,
                project_id,
                actor_user_id=current_user.id,
                visibility=ProjectVisibility.PUBLIC.value,
                published_at=payload.published_at,
            )
        elif payload.status is ProjectStatus.ARCHIVED:
            project = await project_service.archive(
                database_session,
                project_id,
                actor_user_id=current_user.id,
            )
        else:
            project = await project_service.unpublish(
                database_session,
                project_id,
                actor_user_id=current_user.id,
                clear_published_at=True,
            )
    except (
        ProjectNotFoundError,
        ProjectSelectedCategoryNotFoundError,
        ProjectCategoryUnavailableError,
        ProjectPublicationError,
    ) as exc:
        raise_project_error(
            exc,
        )

    return ProjectAdminRead.model_validate(
        project,
    )


@router.patch(
    "/{project_id}/visibility",
    response_model=ProjectAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a portfolio project visibility",
)
async def update_admin_project_visibility(
    project_id: UUID,
    payload: ProjectVisibilityUpdate,
    current_user: ProjectUpdater,
    database_session: DatabaseSession,
) -> ProjectAdminRead:
    """Update the visibility of a portfolio project."""

    del payload.reason

    try:
        project = await project_service.update(
            database_session,
            project_id,
            ProjectUpdate(
                visibility=payload.visibility,
            ),
            actor_user_id=current_user.id,
        )
    except (
        ProjectNotFoundError,
        ProjectPublicationError,
    ) as exc:
        raise_project_error(
            exc,
        )

    return ProjectAdminRead.model_validate(
        project,
    )


@router.patch(
    "/{project_id}/featured",
    response_model=ProjectAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a portfolio project featured state",
)
async def update_admin_project_featured(
    project_id: UUID,
    payload: ProjectFeaturedUpdate,
    current_user: ProjectUpdater,
    database_session: DatabaseSession,
) -> ProjectAdminRead:
    """Feature or unfeature a published public portfolio project."""

    del payload.reason

    try:
        project = await project_service.set_featured(
            database_session,
            project_id,
            is_featured=payload.is_featured,
            actor_user_id=current_user.id,
        )
    except (
        ProjectNotFoundError,
        ProjectPublicationError,
    ) as exc:
        raise_project_error(
            exc,
        )

    return ProjectAdminRead.model_validate(
        project,
    )


@router.delete(
    "/{project_id}",
    response_model=ProjectAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a portfolio project",
)
async def delete_admin_project(
    project_id: UUID,
    payload: ProjectDeleteRequest,
    current_user: ProjectDeleter,
    database_session: DatabaseSession,
) -> ProjectAdminRead:
    """Soft-delete a portfolio project and its technology assignments."""

    del payload.reason

    try:
        project = await project_service.soft_delete(
            database_session,
            project_id,
            actor_user_id=current_user.id,
        )
    except ProjectNotFoundError as exc:
        raise_project_error(
            exc,
        )

    return ProjectAdminRead.model_validate(
        project,
    )


@router.post(
    "/{project_id}/restore",
    response_model=ProjectAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Restore a portfolio project",
)
async def restore_admin_project(
    project_id: UUID,
    payload: ProjectRestoreRequest,
    current_user: ProjectUpdater,
    database_session: DatabaseSession,
) -> ProjectAdminRead:
    """
    Restore a soft-deleted portfolio project.

    Restored projects cannot return directly to the published state.
    """

    del payload.reason

    try:
        project = await project_service.restore(
            database_session,
            project_id,
            actor_user_id=current_user.id,
            restore_as_draft=True,
        )

        if (
            payload.status is not ProjectStatus.DRAFT
            or payload.visibility is not ProjectVisibility.PRIVATE
        ):
            project = await project_service.update(
                database_session,
                project.id,
                ProjectUpdate(
                    status=payload.status,
                    visibility=payload.visibility,
                ),
                actor_user_id=current_user.id,
            )
    except (
        ProjectNotFoundError,
        ProjectConflictError,
        ProjectSelectedCategoryNotFoundError,
        ProjectCategoryUnavailableError,
        ProjectPublicationError,
    ) as exc:
        raise_project_error(
            exc,
        )

    return ProjectAdminRead.model_validate(
        project,
    )
