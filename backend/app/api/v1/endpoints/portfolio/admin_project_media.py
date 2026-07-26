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
    AdminProjectMediaListResponse,
    ProjectMediaAdminRead,
    ProjectMediaCreate,
    ProjectMediaDeleteRequest,
    ProjectMediaPrimaryUpdate,
    ProjectMediaRestoreRequest,
    ProjectMediaType,
    ProjectMediaUpdate,
)
from app.services.portfolio.project_media_service import (
    ProjectMediaConflictError,
    ProjectMediaNotFoundError,
    ProjectMediaProjectNotFoundError,
    project_media_service,
)


router = APIRouter(
    prefix="/admin/portfolio",
    tags=["Admin Portfolio Project Media"],
)


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


ProjectMediaReader = Annotated[
    User,
    Depends(
        require_permission(
            "projects.read",
        )
    ),
]


ProjectMediaCreator = Annotated[
    User,
    Depends(
        require_permission(
            "projects.create",
        )
    ),
]


ProjectMediaUpdater = Annotated[
    User,
    Depends(
        require_permission(
            "projects.update",
        )
    ),
]


ProjectMediaDeleter = Annotated[
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
        description="Number of media records to return per page.",
    ),
]


SearchQuery = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=200,
        description=(
            "Search media URLs, alternative text, captions, providers, "
            "provider asset IDs, and MIME types."
        ),
    ),
]


MediaTypeQuery = Annotated[
    ProjectMediaType | None,
    Query(
        description="Filter records by media type.",
    ),
]


PrimaryQuery = Annotated[
    bool | None,
    Query(
        description="Filter records by primary-media status.",
    ),
]


IncludeDeletedQuery = Annotated[
    bool,
    Query(
        description="Include soft-deleted media records.",
    ),
]


MediaSortField = Literal[
    "media_type",
    "is_primary",
    "sort_order",
    "created_at",
    "updated_at",
]


SortByQuery = Annotated[
    MediaSortField,
    Query(
        description="Field used to sort project media.",
    ),
]


SortDirectionQuery = Annotated[
    Literal["asc", "desc"],
    Query(
        description="Sort direction.",
    ),
]


def raise_media_error(
    *,
    status_code: int,
    code: str,
    message: str,
) -> NoReturn:
    """Raise a structured project-media API error."""

    raise HTTPException(
        status_code=status_code,
        detail={
            "code": code,
            "message": message,
        },
    )


def handle_media_not_found() -> NoReturn:
    """Raise a standard project-media not-found response."""

    raise_media_error(
        status_code=status.HTTP_404_NOT_FOUND,
        code="project_media_not_found",
        message="Project media was not found.",
    )


def handle_project_not_found() -> NoReturn:
    """Raise a standard parent-project not-found response."""

    raise_media_error(
        status_code=status.HTTP_404_NOT_FOUND,
        code="project_not_found",
        message="Portfolio project was not found.",
    )


def handle_media_conflict(
    exception: ProjectMediaConflictError,
) -> NoReturn:
    """Raise a standard project-media conflict response."""

    raise_media_error(
        status_code=status.HTTP_409_CONFLICT,
        code="project_media_conflict",
        message=str(exception),
    )


@router.get(
    "/projects/{project_id}/media",
    response_model=AdminProjectMediaListResponse,
    status_code=status.HTTP_200_OK,
    summary="List project media",
)
async def list_admin_project_media(
    project_id: UUID,
    session: DatabaseSession,
    _: ProjectMediaReader,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    search: SearchQuery = None,
    media_type: MediaTypeQuery = None,
    is_primary: PrimaryQuery = None,
    include_deleted: IncludeDeletedQuery = False,
    sort_by: SortByQuery = "sort_order",
    sort_direction: SortDirectionQuery = "asc",
) -> AdminProjectMediaListResponse:
    """Return paginated media records belonging to one project."""

    offset = (page - 1) * page_size

    try:
        media_records, total_items = await project_media_service.list_for_admin(
            session,
            project_id=project_id,
            offset=offset,
            limit=page_size,
            search=search,
            media_type=media_type.value if media_type is not None else None,
            is_primary=is_primary,
            include_deleted=include_deleted,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )
    except ProjectMediaProjectNotFoundError:
        handle_project_not_found()

    total_pages = (
        ceil(
            total_items / page_size,
        )
        if total_items > 0
        else 0
    )

    return AdminProjectMediaListResponse(
        items=[
            ProjectMediaAdminRead.model_validate(
                media,
            )
            for media in media_records
        ],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next_page=page < total_pages,
        has_previous_page=page > 1,
    )


@router.get(
    "/media/{media_id}",
    response_model=ProjectMediaAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Get project media",
)
async def get_admin_project_media(
    media_id: UUID,
    session: DatabaseSession,
    _: ProjectMediaReader,
    include_deleted: IncludeDeletedQuery = False,
) -> ProjectMediaAdminRead:
    """Return one project-media record by UUID."""

    try:
        media = await project_media_service.get_by_id(
            session,
            media_id,
            include_deleted=include_deleted,
        )
    except ProjectMediaNotFoundError:
        handle_media_not_found()

    return ProjectMediaAdminRead.model_validate(
        media,
    )


@router.post(
    "/projects/{project_id}/media",
    response_model=ProjectMediaAdminRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create project media",
)
async def create_admin_project_media(
    project_id: UUID,
    payload: ProjectMediaCreate,
    session: DatabaseSession,
    _: ProjectMediaCreator,
) -> ProjectMediaAdminRead:
    """Create a media record for a portfolio project."""

    try:
        media = await project_media_service.create(
            session,
            project_id,
            payload,
        )
    except ProjectMediaProjectNotFoundError:
        handle_project_not_found()
    except ProjectMediaConflictError as exception:
        handle_media_conflict(
            exception,
        )

    await session.commit()
    await session.refresh(
        media,
    )

    return ProjectMediaAdminRead.model_validate(
        media,
    )


@router.patch(
    "/media/{media_id}",
    response_model=ProjectMediaAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update project media",
)
async def update_admin_project_media(
    media_id: UUID,
    payload: ProjectMediaUpdate,
    session: DatabaseSession,
    _: ProjectMediaUpdater,
) -> ProjectMediaAdminRead:
    """Update an existing project-media record."""

    try:
        media = await project_media_service.update(
            session,
            media_id,
            payload,
        )
    except ProjectMediaNotFoundError:
        handle_media_not_found()
    except ProjectMediaConflictError as exception:
        handle_media_conflict(
            exception,
        )

    await session.commit()
    await session.refresh(
        media,
    )

    return ProjectMediaAdminRead.model_validate(
        media,
    )


@router.patch(
    "/media/{media_id}/primary",
    response_model=ProjectMediaAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Set primary project media",
)
async def set_admin_project_media_primary(
    media_id: UUID,
    payload: ProjectMediaPrimaryUpdate,
    session: DatabaseSession,
    _: ProjectMediaUpdater,
) -> ProjectMediaAdminRead:
    """
    Set or clear the primary state of a project-media record.

    Setting a record as primary automatically demotes the project's
    existing primary media.
    """

    try:
        if payload.is_primary:
            media = await project_media_service.set_primary(
                session,
                media_id,
            )
        else:
            media = await project_media_service.update(
                session,
                media_id,
                ProjectMediaUpdate(
                    is_primary=False,
                ),
            )
    except ProjectMediaNotFoundError:
        handle_media_not_found()
    except ProjectMediaConflictError as exception:
        handle_media_conflict(
            exception,
        )

    await session.commit()
    await session.refresh(
        media,
    )

    return ProjectMediaAdminRead.model_validate(
        media,
    )


@router.delete(
    "/media/{media_id}",
    response_model=ProjectMediaAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Delete project media",
)
async def delete_admin_project_media(
    media_id: UUID,
    payload: ProjectMediaDeleteRequest,
    session: DatabaseSession,
    _: ProjectMediaDeleter,
) -> ProjectMediaAdminRead:
    """
    Soft-delete project media.

    If the deleted record was primary, the next available media record
    becomes the project's primary media.
    """

    del payload

    try:
        media = await project_media_service.soft_delete(
            session,
            media_id,
            assign_replacement_primary=True,
        )
    except ProjectMediaNotFoundError:
        handle_media_not_found()

    await session.commit()
    await session.refresh(
        media,
    )

    return ProjectMediaAdminRead.model_validate(
        media,
    )


@router.post(
    "/media/{media_id}/restore",
    response_model=ProjectMediaAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Restore project media",
)
async def restore_admin_project_media(
    media_id: UUID,
    payload: ProjectMediaRestoreRequest,
    session: DatabaseSession,
    _: ProjectMediaDeleter,
) -> ProjectMediaAdminRead:
    """Restore a soft-deleted project-media record."""

    try:
        media = await project_media_service.restore(
            session,
            media_id,
            restore_as_primary=payload.restore_as_primary,
        )
    except ProjectMediaNotFoundError:
        handle_media_not_found()
    except ProjectMediaProjectNotFoundError:
        handle_project_not_found()
    except ProjectMediaConflictError as exception:
        handle_media_conflict(
            exception,
        )

    await session.commit()
    await session.refresh(
        media,
    )

    return ProjectMediaAdminRead.model_validate(
        media,
    )
