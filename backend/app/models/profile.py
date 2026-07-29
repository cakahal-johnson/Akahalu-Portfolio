from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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


class Profile(BaseModel, ReprMixin):
    """
    Represents the singleton professional portfolio profile.

    Only one profile record may exist, including soft-deleted records.
    Deleted profiles must be restored rather than recreated.

    Public queries must require:
    - is_public = true
    - deleted_at IS NULL
    """

    __tablename__ = "profiles"

    profile_key: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="primary",
        server_default=text("'primary'"),
        unique=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    middle_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    professional_title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    headline: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    short_bio: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    biography: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    timezone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    primary_email: Mapped[str] = mapped_column(
        CITEXT,
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )

    website_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    resume_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    profile_image_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    years_of_experience: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    availability_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="open_to_opportunities",
        server_default=text("'open_to_opportunities'"),
        index=True,
    )

    availability_message: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
    )

    seo_title: Mapped[str | None] = mapped_column(
        String(70),
        nullable=True,
    )

    seo_description: Mapped[str | None] = mapped_column(
        String(170),
        nullable=True,
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
        lazy="joined",
    )

    updated_by: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[updated_by_id],
        lazy="joined",
    )

    __table_args__ = (
        CheckConstraint(
            "profile_key = 'primary'",
            name="profiles_profile_key_primary",
        ),
        CheckConstraint(
            "length(btrim(first_name)) >= 2",
            name="profiles_first_name_min_length",
        ),
        CheckConstraint(
            "middle_name IS NULL OR length(btrim(middle_name)) >= 2",
            name="profiles_middle_name_min_length",
        ),
        CheckConstraint(
            "length(btrim(last_name)) >= 2",
            name="profiles_last_name_min_length",
        ),
        CheckConstraint(
            "length(btrim(display_name)) >= 2",
            name="profiles_display_name_min_length",
        ),
        CheckConstraint(
            "length(btrim(professional_title)) >= 2",
            name="profiles_professional_title_min_length",
        ),
        CheckConstraint(
            "length(btrim(headline)) >= 5",
            name="profiles_headline_min_length",
        ),
        CheckConstraint(
            "length(btrim(short_bio)) >= 20",
            name="profiles_short_bio_min_length",
        ),
        CheckConstraint(
            "length(btrim(biography)) >= 50",
            name="profiles_biography_min_length",
        ),
        CheckConstraint(
            "location IS NULL OR length(btrim(location)) > 0",
            name="profiles_location_not_blank",
        ),
        CheckConstraint(
            "country IS NULL OR length(btrim(country)) > 0",
            name="profiles_country_not_blank",
        ),
        CheckConstraint(
            "timezone IS NULL OR length(btrim(timezone)) > 0",
            name="profiles_timezone_not_blank",
        ),
        CheckConstraint(
            "length(btrim(primary_email::text)) >= 3",
            name="profiles_primary_email_not_blank",
        ),
        CheckConstraint(
            "phone IS NULL OR length(btrim(phone)) > 0",
            name="profiles_phone_not_blank",
        ),
        CheckConstraint(
            "website_url IS NULL OR length(btrim(website_url)) > 0",
            name="profiles_website_url_not_blank",
        ),
        CheckConstraint(
            "resume_url IS NULL OR length(btrim(resume_url)) > 0",
            name="profiles_resume_url_not_blank",
        ),
        CheckConstraint(
            "profile_image_url IS NULL OR length(btrim(profile_image_url)) > 0",
            name="profiles_profile_image_url_not_blank",
        ),
        CheckConstraint(
            "years_of_experience >= 0",
            name="profiles_years_of_experience_non_negative",
        ),
        CheckConstraint(
            (
                "availability_status IN ("
                "'available', "
                "'open_to_opportunities', "
                "'limited_availability', "
                "'unavailable'"
                ")"
            ),
            name="profiles_availability_status_allowed",
        ),
        CheckConstraint(
            ("availability_message IS NULL OR length(btrim(availability_message)) > 0"),
            name="profiles_availability_message_not_blank",
        ),
        CheckConstraint(
            "seo_title IS NULL OR length(btrim(seo_title)) > 0",
            name="profiles_seo_title_not_blank",
        ),
        CheckConstraint(
            "seo_description IS NULL OR length(btrim(seo_description)) > 0",
            name="profiles_seo_description_not_blank",
        ),
        Index(
            "ix_profiles_public",
            "is_public",
            postgresql_where=text(
                "deleted_at IS NULL AND is_public = true",
            ),
        ),
    )

    @property
    def is_publicly_visible(self) -> bool:
        """Return whether the profile is available through the public API."""

        return self.is_public and not self.is_deleted
