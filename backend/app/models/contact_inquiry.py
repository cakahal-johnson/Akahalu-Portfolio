from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, ReprMixin


if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class ContactInquiry(BaseModel, ReprMixin):
    """
    Represents a message submitted through the public portfolio.

    Public visitors can submit inquiries without authentication.
    Administrative users can review, prioritize, assign, respond to,
    archive, mark as spam, soft-delete, and restore inquiry records.

    Raw client IP addresses are not stored. When request-origin
    information is retained, only a one-way hash should be persisted.
    """

    __tablename__ = "contact_inquiries"

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        CITEXT,
        nullable=False,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )

    company: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    subject: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    inquiry_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="general",
        server_default=text("'general'"),
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="new",
        server_default=text("'new'"),
        index=True,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="normal",
        server_default=text("'normal'"),
        index=True,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    assigned_to_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    project_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    internal_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    consent_given: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    source_page: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )

    ip_address_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    submission_fingerprint: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    assigned_to: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[assigned_to_id],
        lazy="joined",
    )

    project: Mapped[Project | None] = relationship(
        "Project",
        foreign_keys=[project_id],
        lazy="joined",
    )

    __table_args__ = (
        CheckConstraint(
            "length(btrim(name)) >= 2",
            name="contact_inquiries_name_min_length",
        ),
        CheckConstraint(
            "length(btrim(email::text)) >= 3",
            name="contact_inquiries_email_not_blank",
        ),
        CheckConstraint(
            "phone IS NULL OR length(btrim(phone)) > 0",
            name="contact_inquiries_phone_not_blank",
        ),
        CheckConstraint(
            "company IS NULL OR length(btrim(company)) > 0",
            name="contact_inquiries_company_not_blank",
        ),
        CheckConstraint(
            "length(btrim(subject)) >= 3",
            name="contact_inquiries_subject_min_length",
        ),
        CheckConstraint(
            "length(btrim(message)) >= 10",
            name="contact_inquiries_message_min_length",
        ),
        CheckConstraint(
            (
                "inquiry_type IN ("
                "'general', "
                "'employment', "
                "'freelance', "
                "'contract', "
                "'collaboration', "
                "'project', "
                "'support', "
                "'other'"
                ")"
            ),
            name="contact_inquiries_type_allowed",
        ),
        CheckConstraint(
            ("status IN ('new', 'in_progress', 'responded', 'closed', 'spam')"),
            name="contact_inquiries_status_allowed",
        ),
        CheckConstraint(
            "priority IN ('low', 'normal', 'high', 'urgent')",
            name="contact_inquiries_priority_allowed",
        ),
        CheckConstraint(
            (
                "(is_read = false AND read_at IS NULL) "
                "OR "
                "(is_read = true AND read_at IS NOT NULL)"
            ),
            name="contact_inquiries_read_state_consistent",
        ),
        CheckConstraint(
            ("status <> 'responded' OR responded_at IS NOT NULL"),
            name="contact_inquiries_responded_requires_timestamp",
        ),
        CheckConstraint(
            ("status <> 'closed' OR closed_at IS NOT NULL"),
            name="contact_inquiries_closed_requires_timestamp",
        ),
        CheckConstraint(
            ("internal_notes IS NULL OR length(btrim(internal_notes)) > 0"),
            name="contact_inquiries_internal_notes_not_blank",
        ),
        CheckConstraint(
            ("source_page IS NULL OR length(btrim(source_page)) > 0"),
            name="contact_inquiries_source_page_not_blank",
        ),
        CheckConstraint(
            ("user_agent IS NULL OR length(btrim(user_agent)) > 0"),
            name="contact_inquiries_user_agent_not_blank",
        ),
        CheckConstraint(
            ("ip_address_hash IS NULL OR length(ip_address_hash) = 64"),
            name="contact_inquiries_ip_hash_length",
        ),
        CheckConstraint(
            ("submission_fingerprint IS NULL OR length(submission_fingerprint) = 64"),
            name="contact_inquiries_fingerprint_length",
        ),
        Index(
            "ix_contact_inquiries_admin_listing",
            "status",
            "priority",
            "is_read",
            "created_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_contact_inquiries_assignment_listing",
            "assigned_to_id",
            "status",
            "created_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_contact_inquiries_project_listing",
            "project_id",
            "created_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_contact_inquiries_sender_listing",
            "email",
            "created_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    @property
    def is_new(self) -> bool:
        return self.status == "new"

    @property
    def is_closed(self) -> bool:
        return self.status == "closed"

    @property
    def is_spam(self) -> bool:
        return self.status == "spam"

    @property
    def requires_attention(self) -> bool:
        return (
            not self.is_deleted
            and self.status in {"new", "in_progress"}
            and self.priority in {"high", "urgent"}
        )
