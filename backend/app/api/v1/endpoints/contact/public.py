from typing import Annotated, NoReturn

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.dependencies import get_db_session
from app.schemas.contact.inquiry import (
    ContactInquiryPublicCreate,
    ContactInquiryPublicResponse,
)
from app.services.contact.inquiry_service import (
    ContactInquiryDuplicateError,
    ContactInquiryError,
    ContactInquiryHoneypotError,
    contact_inquiry_service,
)


router = APIRouter(
    prefix="/contact/inquiries",
    tags=["Contact"],
)


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


def raise_public_contact_error(
    exception: ContactInquiryError,
) -> NoReturn:
    """Translate a public contact service error into an API response."""

    raise HTTPException(
        status_code=exception.status_code,
        detail={
            "code": exception.error_code,
            "message": exception.message,
        },
    ) from exception


def get_request_client_ip(
    request: Request,
) -> str | None:
    """
    Return the directly connected client IP address.

    Trusted reverse-proxy forwarding headers should be handled centrally
    by the deployment proxy or trusted-proxy middleware rather than being
    accepted directly from untrusted clients here.
    """

    if request.client is None:
        return None

    return request.client.host


@router.post(
    "",
    response_model=ContactInquiryPublicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a contact inquiry",
)
async def create_public_contact_inquiry(
    payload: ContactInquiryPublicCreate,
    request: Request,
    database_session: DatabaseSession,
) -> ContactInquiryPublicResponse:
    """
    Submit a public portfolio contact inquiry.

    Duplicate and honeypot submissions receive the same generic response as
    accepted submissions so the endpoint does not reveal spam-protection
    behaviour.
    """

    try:
        await contact_inquiry_service.create_public(
            database_session,
            payload,
            client_ip=get_request_client_ip(
                request,
            ),
            user_agent=request.headers.get(
                "user-agent",
            ),
            hash_secret=settings.contact_hash_secret_key,
        )
    except (
        ContactInquiryDuplicateError,
        ContactInquiryHoneypotError,
    ):
        return ContactInquiryPublicResponse()
    except ContactInquiryError as exc:
        raise_public_contact_error(
            exc,
        )

    return ContactInquiryPublicResponse()
