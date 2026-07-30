from datetime import date
from enum import StrEnum
from typing import Self
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.schemas.base import DatabaseSchema, SchemaBase
from app.schemas.portfolio.common import (
    PaginatedResponse,
    ResourceUrl,
    Slug,
    SortOrder,
)


class EmploymentType(StrEnum):
    """Supported professional engagement types."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"
    APPRENTICESHIP = "apprenticeship"
    TEMPORARY = "temporary"
    VOLUNTEER = "volunteer"
    SELF_EMPLOYED = "self_employed"
    OTHER = "other"


class ExperienceLocationType(StrEnum):
    """Supported professional work-location arrangements."""

    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class ExperienceBase(SchemaBase):
    """Shared portfolio-experience fields."""

    company_name: str = Field(
        min_length=2,
        max_length=200,
        examples=[
            "ZaraDera Ltd",
        ],
    )

    job_title: str = Field(
        min_length=2,
        max_length=200,
        examples=[
            "Backend Software Developer",
        ],
    )

    slug: Slug

    employment_type: EmploymentType = EmploymentType.FULL_TIME

    location: str | None = Field(
        default=None,
        max_length=250,
        examples=[
            "London, United Kingdom",
        ],
    )

    location_type: ExperienceLocationType = ExperienceLocationType.ONSITE

    start_date: date

    end_date: date | None = None

    is_current: bool = False

    summary: str = Field(
        min_length=10,
        max_length=10_000,
        examples=[
            "Developed and maintained secure backend services for a "
            "professional cleaning and facilities-management platform."
        ],
    )

    responsibilities: str | None = Field(
        default=None,
        max_length=30_000,
    )

    achievements: str | None = Field(
        default=None,
        max_length=30_000,
    )

    company_website: ResourceUrl | None = None

    company_logo_url: ResourceUrl | None = None

    sort_order: SortOrder = 0

    is_featured: bool = False

    is_public: bool = False

    @field_validator(
        "company_name",
        "job_title",
        mode="before",
    )
    @classmethod
    def normalize_required_single_line_text(
        cls,
        value: object,
    ) -> object:
        """Normalize required single-line text fields."""

        if not isinstance(
            value,
            str,
        ):
            return value

        return " ".join(
            value.split(),
        )

    @field_validator(
        "slug",
        mode="before",
    )
    @classmethod
    def normalize_slug(
        cls,
        value: object,
    ) -> object:
        """Normalize an experience slug."""

        if not isinstance(
            value,
            str,
        ):
            return value

        return value.strip().lower()

    @field_validator(
        "employment_type",
        "location_type",
        mode="before",
    )
    @classmethod
    def normalize_enum_values(
        cls,
        value: object,
    ) -> object:
        """Normalize string-based enum values."""

        if not isinstance(
            value,
            str,
        ):
            return value

        return value.strip().lower()

    @field_validator(
        "location",
        mode="before",
    )
    @classmethod
    def normalize_optional_single_line_text(
        cls,
        value: object,
    ) -> object:
        """Normalize optional single-line text."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        normalized_value = " ".join(
            value.split(),
        )

        return normalized_value or None

    @field_validator(
        "summary",
        "responsibilities",
        "achievements",
        mode="before",
    )
    @classmethod
    def normalize_long_text(
        cls,
        value: object,
    ) -> object:
        """Trim long-form experience content."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator(
        "company_website",
        "company_logo_url",
        mode="before",
    )
    @classmethod
    def normalize_urls(
        cls,
        value: object,
    ) -> object:
        """Normalize optional company URLs."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @model_validator(mode="after")
    def validate_experience_dates(self) -> Self:
        """Validate the experience date lifecycle."""

        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError(
                "Experience end date cannot be before its start date.",
            )

        if self.is_current and self.end_date is not None:
            raise ValueError(
                "A current experience cannot include an end date.",
            )

        return self


class ExperienceCreate(ExperienceBase):
    """Payload for creating a portfolio experience."""

    model_config = ConfigDict(
        extra="forbid",
    )


class ExperienceUpdate(SchemaBase):
    """Payload for partially updating a portfolio experience."""

    model_config = ConfigDict(
        extra="forbid",
    )

    company_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    job_title: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    slug: Slug | None = None

    employment_type: EmploymentType | None = None

    location: str | None = Field(
        default=None,
        max_length=250,
    )

    location_type: ExperienceLocationType | None = None

    start_date: date | None = None

    end_date: date | None = None

    is_current: bool | None = None

    summary: str | None = Field(
        default=None,
        min_length=10,
        max_length=10_000,
    )

    responsibilities: str | None = Field(
        default=None,
        max_length=30_000,
    )

    achievements: str | None = Field(
        default=None,
        max_length=30_000,
    )

    company_website: ResourceUrl | None = None

    company_logo_url: ResourceUrl | None = None

    sort_order: SortOrder | None = None

    is_featured: bool | None = None

    is_public: bool | None = None

    @field_validator(
        "company_name",
        "job_title",
        mode="before",
    )
    @classmethod
    def normalize_required_single_line_text(
        cls,
        value: object,
    ) -> object:
        """Normalize optional updates to required single-line fields."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        return " ".join(
            value.split(),
        )

    @field_validator(
        "slug",
        mode="before",
    )
    @classmethod
    def normalize_slug(
        cls,
        value: object,
    ) -> object:
        """Normalize an optional experience slug."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        return value.strip().lower()

    @field_validator(
        "employment_type",
        "location_type",
        mode="before",
    )
    @classmethod
    def normalize_enum_values(
        cls,
        value: object,
    ) -> object:
        """Normalize optional string-based enum values."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        return value.strip().lower()

    @field_validator(
        "location",
        mode="before",
    )
    @classmethod
    def normalize_optional_single_line_text(
        cls,
        value: object,
    ) -> object:
        """Normalize an optional location update."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        normalized_value = " ".join(
            value.split(),
        )

        return normalized_value or None

    @field_validator(
        "summary",
        "responsibilities",
        "achievements",
        mode="before",
    )
    @classmethod
    def normalize_long_text(
        cls,
        value: object,
    ) -> object:
        """Trim optional long-form updates."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator(
        "company_website",
        "company_logo_url",
        mode="before",
    )
    @classmethod
    def normalize_urls(
        cls,
        value: object,
    ) -> object:
        """Normalize optional URL updates."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @model_validator(mode="after")
    def validate_update(self) -> Self:
        """Validate partial experience updates."""

        if not self.model_fields_set:
            raise ValueError(
                "At least one experience field must be provided.",
            )

        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError(
                "Experience end date cannot be before its start date.",
            )

        if self.is_current is True and self.end_date is not None:
            raise ValueError(
                "A current experience cannot include an end date.",
            )

        return self


class ExperienceSummary(SchemaBase):
    """Compact public representation of a portfolio experience."""

    id: UUID

    company_name: str

    job_title: str

    slug: str

    employment_type: EmploymentType

    location: str | None = None

    location_type: ExperienceLocationType

    start_date: date

    end_date: date | None = None

    is_current: bool

    summary: str

    company_website: str | None = None

    company_logo_url: str | None = None

    sort_order: int

    is_featured: bool


class ExperienceRead(ExperienceSummary):
    """Complete public representation of a portfolio experience."""

    responsibilities: str | None = None

    achievements: str | None = None


class ExperienceAdminRead(
    ExperienceBase,
    DatabaseSchema,
):
    """Complete administrative representation of an experience."""

    created_by_id: UUID | None = None

    updated_by_id: UUID | None = None


class ExperienceVisibilityUpdate(SchemaBase):
    """Payload for updating public experience visibility."""

    model_config = ConfigDict(
        extra="forbid",
    )

    is_public: bool

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
        """Normalize an optional visibility-change reason."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        normalized_value = " ".join(
            value.split(),
        )

        return normalized_value or None


class ExperienceFeaturedUpdate(SchemaBase):
    """Payload for updating the featured state."""

    model_config = ConfigDict(
        extra="forbid",
    )

    is_featured: bool

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
        """Normalize an optional featured-state reason."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        normalized_value = " ".join(
            value.split(),
        )

        return normalized_value or None


class ExperienceDeleteRequest(SchemaBase):
    """Payload for soft-deleting a portfolio experience."""

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
        """Normalize an optional deletion reason."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        normalized_value = " ".join(
            value.split(),
        )

        return normalized_value or None


class ExperienceRestoreRequest(SchemaBase):
    """Payload for restoring a soft-deleted experience."""

    model_config = ConfigDict(
        extra="forbid",
    )

    make_public: bool = False

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
        """Normalize an optional restoration reason."""

        if value is None or not isinstance(
            value,
            str,
        ):
            return value

        normalized_value = " ".join(
            value.split(),
        )

        return normalized_value or None


ExperienceListResponse = PaginatedResponse[ExperienceSummary]

AdminExperienceListResponse = PaginatedResponse[ExperienceAdminRead]
