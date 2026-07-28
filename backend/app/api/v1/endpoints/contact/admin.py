from datetime import datetime
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
from app.schemas.contact.common import (
    ContactInquiryPriority,
    ContactInquiryStatus,
    ContactInquiryType,
)
from app.schemas.contact.inquiry import (
    AdminContactInquiryListResponse,
    ContactInquiryAdminRead,
    ContactInquiryDeleteRequest,
    ContactInquiryReadUpdate,
    ContactInquiryRestoreRequest,
    ContactInquiryStatusUpdate,
    ContactInquirySummary,
    ContactInquiryUpdate,
)
from app.services.contact.inquiry_service import (
    ContactInquiryError,
    contact_inquiry_service,
)


router = APIRouter(
    prefix="/admin/contact/inquiries",
    tags=["Admin Contact Inquiries"],
)


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


ContactInquiryReader = Annotated[
    User,
    Depends(
        require_permission(
            "contact_inquiries.read",
        )
    ),
]


ContactInquiryUpdater = Annotated[
    User,
    Depends(
        require_permission(
            "contact_inquiries.update",
        )
    ),
]


ContactInquiryDeleter = Annotated[
    User,
    Depends(
        require_permission(
            "contact_inquiries.delete",
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
        description="Number of contact inquiries to return per page.",
    ),
]


SearchQuery = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=200,
        description=(
            "Search inquiries by sender name, email, company, subject, "
            "message, or internal notes."
        ),
    ),
]


InquiryTypeQuery = Annotated[
    ContactInquiryType | None,
    Query(
        description="Filter inquiries by inquiry type.",
    ),
]


InquiryStatusQuery = Annotated[
    ContactInquiryStatus | None,
    Query(
        description="Filter inquiries by workflow status.",
    ),
]


PriorityQuery = Annotated[
    ContactInquiryPriority | None,
    Query(
        description="Filter inquiries by priority.",
    ),
]


ReadStateQuery = Annotated[
    bool | None,
    Query(
        description="Filter inquiries by read state.",
    ),
]


AssignedToIdQuery = Annotated[
    UUID | None,
    Query(
        description="Filter inquiries by assigned user ID.",
    ),
]


ProjectIdQuery = Annotated[
    UUID | None,
    Query(
        description="Filter inquiries by related project ID.",
    ),
]


IncludeUnassignedQuery = Annotated[
    bool,
    Query(
        description=("Include unassigned inquiries when filtering by assigned user."),
    ),
]


IncludeDeletedQuery = Annotated[
    bool,
    Query(
        description="Include soft-deleted contact inquiries.",
    ),
]


CreatedFromQuery = Annotated[
    datetime | None,
    Query(
        description=("Return inquiries created on or after this timestamp."),
    ),
]


CreatedToQuery = Annotated[
    datetime | None,
    Query(
        description=("Return inquiries created on or before this timestamp."),
    ),
]


ContactInquirySortField = Literal[
    "name",
    "email",
    "subject",
    "inquiry_type",
    "status",
    "priority",
    "is_read",
    "created_at",
    "updated_at",
]


SortDirection = Literal[
    "asc",
    "desc",
]


SortByQuery = Annotated[
    ContactInquirySortField,
    Query(
        description="Field used to sort contact inquiry results.",
    ),
]


SortDirectionQuery = Annotated[
    SortDirection,
    Query(
        description="Direction used to sort contact inquiry results.",
    ),
]


def raise_contact_inquiry_error(
    exception: ContactInquiryError,
) -> NoReturn:
    """Translate a contact inquiry service error into an API response."""

    raise HTTPException(
        status_code=exception.status_code,
        detail={
            "code": exception.error_code,
            "message": exception.message,
        },
    ) from exception


@router.get(
    "/statistics",
    response_model=dict[str, int],
    status_code=status.HTTP_200_OK,
    summary="Get contact inquiry statistics",
)
async def get_contact_inquiry_statistics(
    _: ContactInquiryReader,
    database_session: DatabaseSession,
) -> dict[str, int]:
    """Return workflow and attention statistics for contact inquiries."""

    new_count = await contact_inquiry_service.count_by_status(
        database_session,
        ContactInquiryStatus.NEW,
    )

    in_progress_count = await contact_inquiry_service.count_by_status(
        database_session,
        ContactInquiryStatus.IN_PROGRESS,
    )

    responded_count = await contact_inquiry_service.count_by_status(
        database_session,
        ContactInquiryStatus.RESPONDED,
    )

    closed_count = await contact_inquiry_service.count_by_status(
        database_session,
        ContactInquiryStatus.CLOSED,
    )

    spam_count = await contact_inquiry_service.count_by_status(
        database_session,
        ContactInquiryStatus.SPAM,
    )

    unread_count = await contact_inquiry_service.count_unread(
        database_session,
    )

    requires_attention_count = await contact_inquiry_service.count_requires_attention(
        database_session,
    )

    return {
        "new": new_count,
        "in_progress": in_progress_count,
        "responded": responded_count,
        "closed": closed_count,
        "spam": spam_count,
        "unread": unread_count,
        "requires_attention": requires_attention_count,
    }


@router.get(
    "",
    response_model=AdminContactInquiryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List contact inquiries for administration",
)
async def list_admin_contact_inquiries(
    _: ContactInquiryReader,
    database_session: DatabaseSession,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    search: SearchQuery = None,
    inquiry_type: InquiryTypeQuery = None,
    inquiry_status: InquiryStatusQuery = None,
    priority: PriorityQuery = None,
    is_read: ReadStateQuery = None,
    assigned_to_id: AssignedToIdQuery = None,
    project_id: ProjectIdQuery = None,
    include_unassigned: IncludeUnassignedQuery = False,
    include_deleted: IncludeDeletedQuery = False,
    created_from: CreatedFromQuery = None,
    created_to: CreatedToQuery = None,
    sort_by: SortByQuery = "created_at",
    sort_direction: SortDirectionQuery = "desc",
) -> AdminContactInquiryListResponse:
    """Return paginated contact inquiries for administration."""

    try:
        inquiries, total_items = await contact_inquiry_service.list_for_admin(
            database_session,
            offset=(page - 1) * page_size,
            limit=page_size,
            search=search,
            inquiry_type=(inquiry_type.value if inquiry_type is not None else None),
            inquiry_status=(
                inquiry_status.value if inquiry_status is not None else None
            ),
            priority=(priority.value if priority is not None else None),
            is_read=is_read,
            assigned_to_id=assigned_to_id,
            project_id=project_id,
            include_unassigned=include_unassigned,
            include_deleted=include_deleted,
            created_from=created_from,
            created_to=created_to,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )
    except ContactInquiryError as exc:
        raise_contact_inquiry_error(
            exc,
        )

    total_pages = (
        ceil(
            total_items / page_size,
        )
        if total_items > 0
        else 0
    )

    return AdminContactInquiryListResponse(
        items=[
            ContactInquirySummary.model_validate(
                inquiry,
            )
            for inquiry in inquiries
        ],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next_page=page < total_pages,
        has_previous_page=page > 1,
    )


@router.get(
    "/{inquiry_id}",
    response_model=ContactInquiryAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Get a contact inquiry for administration",
)
async def get_admin_contact_inquiry(
    inquiry_id: UUID,
    _: ContactInquiryReader,
    database_session: DatabaseSession,
    include_deleted: IncludeDeletedQuery = False,
) -> ContactInquiryAdminRead:
    """Return a contact inquiry by ID."""

    try:
        inquiry = await contact_inquiry_service.get_by_id(
            database_session,
            inquiry_id,
            include_deleted=include_deleted,
        )
    except ContactInquiryError as exc:
        raise_contact_inquiry_error(
            exc,
        )

    return ContactInquiryAdminRead.model_validate(
        inquiry,
    )


@router.patch(
    "/{inquiry_id}",
    response_model=ContactInquiryAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a contact inquiry",
)
async def update_admin_contact_inquiry(
    inquiry_id: UUID,
    payload: ContactInquiryUpdate,
    _: ContactInquiryUpdater,
    database_session: DatabaseSession,
) -> ContactInquiryAdminRead:
    """Update inquiry priority, assignment, notes, or type."""

    try:
        inquiry = await contact_inquiry_service.update(
            database_session,
            inquiry_id,
            payload,
        )
    except ContactInquiryError as exc:
        raise_contact_inquiry_error(
            exc,
        )

    return ContactInquiryAdminRead.model_validate(
        inquiry,
    )


@router.patch(
    "/{inquiry_id}/read-state",
    response_model=ContactInquiryAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a contact inquiry read state",
)
async def update_admin_contact_inquiry_read_state(
    inquiry_id: UUID,
    payload: ContactInquiryReadUpdate,
    _: ContactInquiryUpdater,
    database_session: DatabaseSession,
) -> ContactInquiryAdminRead:
    """Mark a contact inquiry as read or unread."""

    try:
        inquiry = await contact_inquiry_service.set_read_state(
            database_session,
            inquiry_id,
            payload,
        )
    except ContactInquiryError as exc:
        raise_contact_inquiry_error(
            exc,
        )

    return ContactInquiryAdminRead.model_validate(
        inquiry,
    )


@router.patch(
    "/{inquiry_id}/status",
    response_model=ContactInquiryAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Update a contact inquiry status",
)
async def update_admin_contact_inquiry_status(
    inquiry_id: UUID,
    payload: ContactInquiryStatusUpdate,
    _: ContactInquiryUpdater,
    database_session: DatabaseSession,
) -> ContactInquiryAdminRead:
    """Move a contact inquiry through its workflow."""

    try:
        inquiry = await contact_inquiry_service.update_status(
            database_session,
            inquiry_id,
            payload,
        )
    except ContactInquiryError as exc:
        raise_contact_inquiry_error(
            exc,
        )

    return ContactInquiryAdminRead.model_validate(
        inquiry,
    )


@router.delete(
    "/{inquiry_id}",
    response_model=ContactInquiryAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a contact inquiry",
)
async def delete_admin_contact_inquiry(
    inquiry_id: UUID,
    payload: ContactInquiryDeleteRequest,
    _: ContactInquiryDeleter,
    database_session: DatabaseSession,
) -> ContactInquiryAdminRead:
    """Soft-delete a contact inquiry."""

    del payload.reason

    try:
        inquiry = await contact_inquiry_service.soft_delete(
            database_session,
            inquiry_id,
        )
    except ContactInquiryError as exc:
        raise_contact_inquiry_error(
            exc,
        )

    return ContactInquiryAdminRead.model_validate(
        inquiry,
    )


@router.post(
    "/{inquiry_id}/restore",
    response_model=ContactInquiryAdminRead,
    status_code=status.HTTP_200_OK,
    summary="Restore a contact inquiry",
)
async def restore_admin_contact_inquiry(
    inquiry_id: UUID,
    payload: ContactInquiryRestoreRequest,
    _: ContactInquiryUpdater,
    database_session: DatabaseSession,
) -> ContactInquiryAdminRead:
    """Restore a previously soft-deleted contact inquiry."""

    try:
        inquiry = await contact_inquiry_service.restore(
            database_session,
            inquiry_id,
            payload,
        )
    except ContactInquiryError as exc:
        raise_contact_inquiry_error(
            exc,
        )

    return ContactInquiryAdminRead.model_validate(
        inquiry,
    )
