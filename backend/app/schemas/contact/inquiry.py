from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import (
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.schemas.base import DatabaseSchema, SchemaBase
from app.schemas.contact.common import (
    ContactInquiryPriority,
    ContactInquiryStatus,
    ContactInquiryType,
    PaginatedResponse,
)


class ContactInquiryPublicCreate(SchemaBase):
    """
    Public contact-form submission payload.

    Administrative fields such as status, priority, internal notes,
    assignment, request metadata, and spam state are intentionally excluded.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str = Field(
        min_length=2,
        max_length=150,
        examples=["Akahalu Chinonso Vitalis"],
    )

    email: EmailStr

    phone: str | None = Field(
        default=None,
        max_length=40,
    )

    company: str | None = Field(
        default=None,
        max_length=150,
    )

    subject: str = Field(
        min_length=3,
        max_length=200,
        examples=["Full-stack development opportunity"],
    )

    message: str = Field(
        min_length=10,
        max_length=10_000,
    )

    inquiry_type: ContactInquiryType = ContactInquiryType.GENERAL

    project_id: UUID | None = None

    consent_given: bool = False

    source_page: str | None = Field(
        default=None,
        max_length=2048,
    )

    website: str | None = Field(
        default=None,
        max_length=200,
        exclude=True,
        description="Honeypot field. Legitimate clients must leave this empty.",
    )

    @field_validator(
        "name",
        "subject",
        mode="before",
    )
    @classmethod
    def normalize_required_single_line_text(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, str):
            return value

        return " ".join(value.split())

    @field_validator(
        "email",
        mode="before",
    )
    @classmethod
    def normalize_email(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, str):
            return value

        return value.strip().lower()

    @field_validator(
        "phone",
        "company",
        mode="before",
    )
    @classmethod
    def normalize_optional_single_line_text(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        return normalized_value or None

    @field_validator(
        "message",
        mode="before",
    )
    @classmethod
    def normalize_message(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, str):
            return value

        return value.strip()

    @field_validator(
        "source_page",
        mode="before",
    )
    @classmethod
    def normalize_source_page(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator(
        "website",
        mode="before",
    )
    @classmethod
    def normalize_honeypot(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = value.strip()

        return normalized_value or None


class ContactInquiryPublicResponse(SchemaBase):
    """
    Generic response returned after a public submission.

    The response deliberately avoids exposing whether a submission was
    stored, identified as a duplicate, or rejected by spam protection.
    """

    message: str = "Your message has been received successfully."


class ContactInquiryUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    priority: ContactInquiryPriority | None = None

    assigned_to_id: UUID | None = None

    internal_notes: str | None = Field(
        default=None,
        max_length=10_000,
    )

    inquiry_type: ContactInquiryType | None = None

    @field_validator(
        "internal_notes",
        mode="before",
    )
    @classmethod
    def normalize_internal_notes(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @model_validator(mode="after")
    def validate_update_fields(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one inquiry field must be provided.")

        return self


class ContactInquiryStatusUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    status: ContactInquiryStatus

    reason: str | None = Field(
        default=None,
        min_length=3,
        max_length=500,
    )

    @field_validator(
        "reason",
        mode="before",
    )
    @classmethod
    def normalize_reason(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        return normalized_value or None


class ContactInquiryReadUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    is_read: bool


class ContactInquiryDeleteRequest(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    reason: str | None = Field(
        default=None,
        min_length=3,
        max_length=500,
    )

    @field_validator(
        "reason",
        mode="before",
    )
    @classmethod
    def normalize_reason(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        return normalized_value or None


class ContactInquiryRestoreRequest(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    status: ContactInquiryStatus = ContactInquiryStatus.NEW

    priority: ContactInquiryPriority = ContactInquiryPriority.NORMAL

    reason: str | None = Field(
        default=None,
        min_length=3,
        max_length=500,
    )

    @field_validator(
        "reason",
        mode="before",
    )
    @classmethod
    def normalize_reason(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        return normalized_value or None

    @model_validator(mode="after")
    def validate_restore_status(self) -> Self:
        if self.status in {
            ContactInquiryStatus.RESPONDED,
            ContactInquiryStatus.CLOSED,
        }:
            raise ValueError(
                "A restored inquiry must be reviewed before being marked "
                "as responded or closed."
            )

        return self


class ContactInquirySummary(SchemaBase):
    id: UUID

    name: str
    email: EmailStr

    subject: str

    inquiry_type: ContactInquiryType
    status: ContactInquiryStatus
    priority: ContactInquiryPriority

    is_read: bool

    assigned_to_id: UUID | None = None
    project_id: UUID | None = None

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class ContactInquiryAdminRead(
    DatabaseSchema,
):
    name: str
    email: EmailStr

    phone: str | None = None
    company: str | None = None

    subject: str
    message: str

    inquiry_type: ContactInquiryType
    status: ContactInquiryStatus
    priority: ContactInquiryPriority

    is_read: bool
    read_at: datetime | None = None
    responded_at: datetime | None = None
    closed_at: datetime | None = None

    assigned_to_id: UUID | None = None
    project_id: UUID | None = None

    internal_notes: str | None = None

    consent_given: bool

    source_page: str | None = None

    user_agent: str | None = None
    ip_address_hash: str | None = None
    submission_fingerprint: str | None = None


AdminContactInquiryListResponse = PaginatedResponse[ContactInquirySummary]
