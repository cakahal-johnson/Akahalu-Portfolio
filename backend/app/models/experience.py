from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, ReprMixin

if TYPE_CHECKING:
    from app.models.user import User


class Experience(BaseModel, ReprMixin):
    """
    Represents a professional portfolio experience.

    Experience records describe employment, contract, freelance,
    internship, volunteer, or other professional engagements.

    Public repository queries must exclude soft-deleted records and
    require ``is_public`` to be enabled.
    """

    __tablename__ = "experiences"

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    job_title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        CITEXT,
        nullable=False,
        unique=True,
        index=True,
    )

    employment_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="full_time",
        server_default=text("'full_time'"),
        index=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    location_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="onsite",
        server_default=text("'onsite'"),
        index=True,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    responsibilities: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    achievements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    company_website: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    company_logo_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
    )

    created_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    updated_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_by: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[created_by_id],
        lazy="raise",
    )

    updated_by: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[updated_by_id],
        lazy="raise",
    )

    __table_args__ = (
        CheckConstraint(
            "length(btrim(company_name)) >= 2",
            name="experiences_company_name_not_blank",
        ),
        CheckConstraint(
            "length(btrim(job_title)) >= 2",
            name="experiences_job_title_not_blank",
        ),
        CheckConstraint(
            "length(btrim(slug::text)) >= 2",
            name="experiences_slug_not_blank",
        ),
        CheckConstraint(
            """
            employment_type IN (
                'full_time',
                'part_time',
                'contract',
                'freelance',
                'internship',
                'apprenticeship',
                'temporary',
                'volunteer',
                'self_employed',
                'other'
            )
            """,
            name="experiences_employment_type_allowed",
        ),
        CheckConstraint(
            """
            location_type IN (
                'onsite',
                'remote',
                'hybrid'
            )
            """,
            name="experiences_location_type_allowed",
        ),
        CheckConstraint(
            "location IS NULL OR length(btrim(location)) > 0",
            name="experiences_location_not_blank",
        ),
        CheckConstraint(
            "length(btrim(summary)) >= 10",
            name="experiences_summary_min_length",
        ),
        CheckConstraint(
            """
            responsibilities IS NULL
            OR length(btrim(responsibilities)) > 0
            """,
            name="experiences_responsibilities_not_blank",
        ),
        CheckConstraint(
            """
            achievements IS NULL
            OR length(btrim(achievements)) > 0
            """,
            name="experiences_achievements_not_blank",
        ),
        CheckConstraint(
            """
            company_website IS NULL
            OR length(btrim(company_website)) > 0
            """,
            name="experiences_company_website_not_blank",
        ),
        CheckConstraint(
            """
            company_logo_url IS NULL
            OR length(btrim(company_logo_url)) > 0
            """,
            name="experiences_company_logo_url_not_blank",
        ),
        CheckConstraint(
            """
            end_date IS NULL
            OR end_date >= start_date
            """,
            name="experiences_end_date_not_before_start",
        ),
        CheckConstraint(
            """
            is_current = false
            OR end_date IS NULL
            """,
            name="experiences_current_has_no_end_date",
        ),
        CheckConstraint(
            "sort_order >= 0",
            name="experiences_sort_order_non_negative",
        ),
        CheckConstraint(
            """
            is_featured = false
            OR is_public = true
            """,
            name="experiences_featured_requires_public",
        ),
        Index(
            "ix_experiences_admin_listing",
            "is_public",
            "is_featured",
            "is_current",
            "sort_order",
            "start_date",
            postgresql_where=text(
                "deleted_at IS NULL",
            ),
        ),
        Index(
            "ix_experiences_public_listing",
            "is_current",
            "is_featured",
            "sort_order",
            "start_date",
            postgresql_where=text(
                "deleted_at IS NULL AND is_public = true",
            ),
        ),
        Index(
            "ix_experiences_employment_filter",
            "employment_type",
            "location_type",
            "start_date",
            postgresql_where=text(
                "deleted_at IS NULL",
            ),
        ),
    )

    @property
    def is_active_experience(self) -> bool:
        """Return whether the experience represents a current position."""

        return self.is_current and self.end_date is None and not self.is_deleted

    @property
    def is_publicly_visible(self) -> bool:
        """Return whether the experience can appear publicly."""

        return self.is_public and not self.is_deleted

    @property
    def date_range_label(self) -> str:
        """
        Return a simple display label for the experience date range.

        The frontend may replace this with locale-aware formatting.
        """

        start_label = self.start_date.strftime(
            "%b %Y",
        )

        if self.is_current:
            return f"{start_label} - Present"

        if self.end_date is None:
            return start_label

        end_label = self.end_date.strftime(
            "%b %Y",
        )

        return f"{start_label} - {end_label}"
