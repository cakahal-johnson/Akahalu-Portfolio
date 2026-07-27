from math import ceil
from typing import Annotated, NoReturn
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
    AdminProjectLinkListResponse,
    ProjectLinkAdminRead,
    ProjectLinkCreate,
    ProjectLinkDeleteRequest,
    ProjectLinkRestoreRequest,
    ProjectLinkStatusUpdate,
    ProjectLinkType,
    ProjectLinkUpdate,
    SortDirection,
)
from app.services.portfolio import (
    ProjectLinkConflictError,
    ProjectLinkNotFoundError,
    ProjectLinkProjectNotFoundError,
    project_link_service,
)


router = APIRouter(
    prefix="/admin/portfolio/projects/{project_id}/links",
    tags=["Admin Portfolio Project Links"],
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
        description="Number of project links to return per page.",
    ),
]


SearchQuery = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=200,
        description="Search project-link labels, URLs, types, and icons.",
    ),
]


LinkTypeQuery = Annotated[
    ProjectLinkType | None,
    Query(
        description="Filter project links by link type.",
    ),
]


ActiveQuery = Annotated[
    bool | None,
    Query(
        description="Filter project links by active status.",
    ),
]


NewTabQuery = Annotated[
    bool | None,
    Query(
        description="Filter links by whether they open in a new browser tab.",
    ),
]


IncludeDeletedQuery = Annotated[
    bool,
    Query(
        description="Include soft-deleted project links.",
    ),
]


SortByQuery = Annotated[
    str,
    Query(
        pattern=(
            "^(label|link_type|is_active|opens_in_new_tab|"
            "sort_order|created_at|updated_at)$"
        ),
        description="Field used to sort project links.",
    ),
]


SortDirectionQuery = Annotated[
    SortDirection,
    Query(
        description="Sort links in ascending or descending order.",
    ),
]


def raise_project_link_error(
    exception: Exception,
) -> NoReturn:
    """Convert project-link service exceptions into API responses."""

    if isinstance(
        exception,
        ProjectLinkNotFoundError,
    ):
        status_code = status.HTTP_404_NOT_FOUND
        code = "project_link_not_found"

    elif isinstance(
        exception,
        ProjectLinkProjectNotFoundError,
    ):
        status_code = status.HTTP_404_NOT_FOUND
        code = "project_not_found"

    elif isinstance(
        exception,
        ProjectLinkConflictError,
    ):
        status_code = status.HTTP_409_CONFLICT
        code = "project_link_conflict"

    else:
        status_code = status.HTTP_400_BAD_REQUEST
        code = "project_link_operation_failed"

    raise HTTPException(
        status_code=status_code,
        detail={
            "code": code,
            "message": str(exception),
        },
    ) from exception


@router.get(
    "",
    response_model=AdminProjectLinkListResponse,
    status_code=status.HTTP_200_OK,
    summary="List project links for administration",
)
async def list_project_links(
    project_id: UUID,
    _: ProjectReader,
    session: DatabaseSession,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    search: SearchQuery = None,
    link_type: LinkTypeQuery = None,
    is_active: ActiveQuery = None,
    opens_in_new_tab: NewTabQuery = None,
    include_deleted: IncludeDeletedQuery = False,
    sort_by: SortByQuery = "sort_order",
    sort_direction: SortDirectionQuery = SortDirection.ASC,
) -> AdminProjectLinkListResponse:
    """
    Return a paginated administrative list of links for a project.

    Results support search, type filtering, activity filtering,
    deleted-record inclusion, new-tab filtering, and sorting.
    """

    offset = (page - 1) * page_size

    try:
        links, total_items = await project_link_service.list_for_admin(
            session,
            project_id=project_id,
            offset=offset,
            limit=page_size,
            search=search,
            link_type=(link_type.value if link_type is not None else None),
            is_active=is_active,
            opens_in_new_tab=opens_in_new_tab,
            include_deleted=include_deleted,
            sort_by=sort_by,
            sort_direction=sort_direction.value,
        )
    except (
        ProjectLinkNotFoundError,
        ProjectLinkProjectNotFoundError,
        ProjectLinkConflictError,
    ) as exc:
        raise_project_link_error(exc)

    total_pages = (
        ceil(
            total_items / page_size,
        )
        if total_items > 0
        else 0
    )

    return AdminProjectLinkListResponse(
        items=[
            ProjectLinkAdminRead.model_validate(
                link,
            )
            for link in links
        ],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next_page=page < total_pages,
        has_previous_page=page > 1,
    )


@router.post(
    "",
    response_model=ProjectLinkAdminRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project link",
)
async def create_project_link(
    project_id: UUID,
    payload: ProjectLinkCreate,
    _: ProjectCreator,
    session: DatabaseSession,
) -> ProjectLinkAdminRead:
    """Create an additional external link for a portfolio project."""

    try:
        link = await project_link_service.create(
            session,
            project_id,
            payload,
        )

        await session.commit()

        link = await project_link_service.get_by_id(
            session,
            link.id,
        )
    except (
        ProjectLinkNotFoundError,
        ProjectLinkProjectNotFoundError,
        ProjectLinkConflictError,
    ) as exc:
        await session.rollback()
        raise_project_link_error(exc)
    except Exception:
        await session.rollback()
        raise

    return ProjectLinkAdminRead.model_validate(
        link,
    )


@router.get(
    "/{link_id}",
    response_model=ProjectLinkAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Get a project link for administration",
)
async def get_project_link(
    project_id: UUID,
    link_id: UUID,
    _: ProjectReader,
    session: DatabaseSession,
    include_deleted: IncludeDeletedQuery = False,
) -> ProjectLinkAdminRead:
    """Return a project link belonging to the selected project."""

    try:
        link = await project_link_service.get_by_id(
            session,
            link_id,
            include_deleted=include_deleted,
        )

        if link.project_id != project_id:
            raise ProjectLinkNotFoundError(
                "Project link was not found.",
            )
    except (
        ProjectLinkNotFoundError,
        ProjectLinkProjectNotFoundError,
        ProjectLinkConflictError,
    ) as exc:
        raise_project_link_error(exc)

    return ProjectLinkAdminRead.model_validate(
        link,
    )


@router.patch(
    "/{link_id}",
    response_model=ProjectLinkAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a project link",
)
async def update_project_link(
    project_id: UUID,
    link_id: UUID,
    payload: ProjectLinkUpdate,
    _: ProjectUpdater,
    session: DatabaseSession,
) -> ProjectLinkAdminRead:
    """Update the content, type, behaviour, or ordering of a project link."""

    try:
        existing_link = await project_link_service.get_by_id(
            session,
            link_id,
        )

        if existing_link.project_id != project_id:
            raise ProjectLinkNotFoundError(
                "Project link was not found.",
            )

        link = await project_link_service.update(
            session,
            link_id,
            payload,
        )

        await session.commit()

        link = await project_link_service.get_by_id(
            session,
            link.id,
        )
    except (
        ProjectLinkNotFoundError,
        ProjectLinkProjectNotFoundError,
        ProjectLinkConflictError,
    ) as exc:
        await session.rollback()
        raise_project_link_error(exc)
    except Exception:
        await session.rollback()
        raise

    return ProjectLinkAdminRead.model_validate(
        link,
    )


@router.patch(
    "/{link_id}/status",
    response_model=ProjectLinkAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a project link status",
)
async def update_project_link_status(
    project_id: UUID,
    link_id: UUID,
    payload: ProjectLinkStatusUpdate,
    _: ProjectUpdater,
    session: DatabaseSession,
) -> ProjectLinkAdminRead:
    """Activate or deactivate a non-deleted project link."""

    try:
        existing_link = await project_link_service.get_by_id(
            session,
            link_id,
        )

        if existing_link.project_id != project_id:
            raise ProjectLinkNotFoundError(
                "Project link was not found.",
            )

        link = await project_link_service.set_active(
            session,
            link_id,
            is_active=payload.is_active,
        )

        await session.commit()

        link = await project_link_service.get_by_id(
            session,
            link.id,
        )
    except (
        ProjectLinkNotFoundError,
        ProjectLinkProjectNotFoundError,
        ProjectLinkConflictError,
    ) as exc:
        await session.rollback()
        raise_project_link_error(exc)
    except Exception:
        await session.rollback()
        raise

    return ProjectLinkAdminRead.model_validate(
        link,
    )


@router.delete(
    "/{link_id}",
    response_model=ProjectLinkAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a project link",
)
async def delete_project_link(
    project_id: UUID,
    link_id: UUID,
    _: ProjectDeleter,
    session: DatabaseSession,
    payload: ProjectLinkDeleteRequest | None = None,
) -> ProjectLinkAdminRead:
    """
    Soft-delete a project link.

    The optional reason is accepted for API consistency and future audit
    logging. The current project-link model does not persist deletion reasons.
    """

    del payload

    try:
        existing_link = await project_link_service.get_by_id(
            session,
            link_id,
        )

        if existing_link.project_id != project_id:
            raise ProjectLinkNotFoundError(
                "Project link was not found.",
            )

        link = await project_link_service.soft_delete(
            session,
            link_id,
        )

        await session.commit()
    except (
        ProjectLinkNotFoundError,
        ProjectLinkProjectNotFoundError,
        ProjectLinkConflictError,
    ) as exc:
        await session.rollback()
        raise_project_link_error(exc)
    except Exception:
        await session.rollback()
        raise

    return ProjectLinkAdminRead.model_validate(
        link,
    )


@router.post(
    "/{link_id}/restore",
    response_model=ProjectLinkAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Restore a project link",
)
async def restore_project_link(
    project_id: UUID,
    link_id: UUID,
    payload: ProjectLinkRestoreRequest,
    _: ProjectUpdater,
    session: DatabaseSession,
) -> ProjectLinkAdminRead:
    """Restore a soft-deleted project link after uniqueness checks."""

    try:
        existing_link = await project_link_service.get_by_id(
            session,
            link_id,
            include_deleted=True,
        )

        if existing_link.project_id != project_id:
            raise ProjectLinkNotFoundError(
                "Project link was not found.",
            )

        link = await project_link_service.restore(
            session,
            link_id,
            restore_as_active=payload.activate,
        )

        await session.commit()

        link = await project_link_service.get_by_id(
            session,
            link.id,
        )
    except (
        ProjectLinkNotFoundError,
        ProjectLinkProjectNotFoundError,
        ProjectLinkConflictError,
    ) as exc:
        await session.rollback()
        raise_project_link_error(exc)
    except Exception:
        await session.rollback()
        raise

    return ProjectLinkAdminRead.model_validate(
        link,
    )
