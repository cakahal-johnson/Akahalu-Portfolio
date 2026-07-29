from enum import StrEnum
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
from app.schemas.portfolio.common import ResourceUrl


class ProfileAvailabilityStatus(StrEnum):
    AVAILABLE = "available"
    OPEN_TO_OPPORTUNITIES = "open_to_opportunities"
    LIMITED_AVAILABILITY = "limited_availability"
    UNAVAILABLE = "unavailable"


class ProfileBase(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    first_name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Akahalu"],
    )

    middle_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        examples=["Chinonso"],
    )

    last_name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Vitalis"],
    )

    display_name: str = Field(
        min_length=2,
        max_length=200,
        examples=["Akahalu Vitalis"],
    )

    professional_title: str = Field(
        min_length=2,
        max_length=200,
        examples=["Full-Stack Software Developer"],
    )

    headline: str = Field(
        min_length=5,
        max_length=300,
        examples=[
            (
                "Building secure, scalable web APIs and modern "
                "cross-platform applications."
            )
        ],
    )

    short_bio: str = Field(
        min_length=20,
        max_length=500,
        examples=[
            (
                "Full-stack software developer focused on secure APIs, "
                "modern web applications, and mobile experiences."
            )
        ],
    )

    biography: str = Field(
        min_length=50,
        max_length=10000,
    )

    location: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        examples=["Regina, Saskatchewan"],
    )

    country: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        examples=["Canada"],
    )

    timezone: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        examples=["America/Regina"],
    )

    primary_email: EmailStr = Field(
        examples=["contact@example.com"],
    )

    phone: str | None = Field(
        default=None,
        min_length=1,
        max_length=40,
    )

    website_url: ResourceUrl | None = None
    resume_url: ResourceUrl | None = None
    profile_image_url: ResourceUrl | None = None

    years_of_experience: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    availability_status: ProfileAvailabilityStatus = (
        ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES
    )

    availability_message: str | None = Field(
        default=None,
        min_length=1,
        max_length=300,
    )

    is_public: bool = False

    seo_title: str | None = Field(
        default=None,
        min_length=1,
        max_length=70,
    )

    seo_description: str | None = Field(
        default=None,
        min_length=1,
        max_length=170,
    )

    @field_validator(
        "first_name",
        "middle_name",
        "last_name",
        "display_name",
        "professional_title",
        "headline",
        "location",
        "country",
        "availability_message",
        "seo_title",
        "seo_description",
        mode="before",
    )
    @classmethod
    def normalize_single_line_text(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(
            value.split(),
        )

        return normalized_value or None

    @field_validator(
        "short_bio",
        "biography",
        mode="before",
    )
    @classmethod
    def normalize_multiline_text(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_lines = [
            " ".join(line.split()) for line in value.strip().splitlines()
        ]

        normalized_value = "\n".join(line for line in normalized_lines if line)

        return normalized_value or None

    @field_validator(
        "timezone",
        mode="before",
    )
    @classmethod
    def normalize_timezone(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator(
        "phone",
        mode="before",
    )
    @classmethod
    def normalize_phone(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(
            value.split(),
        )

        return normalized_value or None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    middle_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    display_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    professional_title: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    headline: str | None = Field(
        default=None,
        min_length=5,
        max_length=300,
    )

    short_bio: str | None = Field(
        default=None,
        min_length=20,
        max_length=500,
    )

    biography: str | None = Field(
        default=None,
        min_length=50,
        max_length=10000,
    )

    location: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    country: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    timezone: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    primary_email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        min_length=1,
        max_length=40,
    )

    website_url: ResourceUrl | None = None
    resume_url: ResourceUrl | None = None
    profile_image_url: ResourceUrl | None = None

    years_of_experience: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    availability_status: ProfileAvailabilityStatus | None = None

    availability_message: str | None = Field(
        default=None,
        min_length=1,
        max_length=300,
    )

    is_public: bool | None = None

    seo_title: str | None = Field(
        default=None,
        min_length=1,
        max_length=70,
    )

    seo_description: str | None = Field(
        default=None,
        min_length=1,
        max_length=170,
    )

    @field_validator(
        "first_name",
        "middle_name",
        "last_name",
        "display_name",
        "professional_title",
        "headline",
        "location",
        "country",
        "availability_message",
        "seo_title",
        "seo_description",
        mode="before",
    )
    @classmethod
    def normalize_single_line_text(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(
            value.split(),
        )

        return normalized_value or None

    @field_validator(
        "short_bio",
        "biography",
        mode="before",
    )
    @classmethod
    def normalize_multiline_text(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_lines = [
            " ".join(line.split()) for line in value.strip().splitlines()
        ]

        normalized_value = "\n".join(line for line in normalized_lines if line)

        return normalized_value or None

    @field_validator(
        "timezone",
        mode="before",
    )
    @classmethod
    def normalize_timezone(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator(
        "phone",
        mode="before",
    )
    @classmethod
    def normalize_phone(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(
            value.split(),
        )

        return normalized_value or None

    @model_validator(
        mode="after",
    )
    def validate_update_fields(
        self,
    ) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "At least one profile field must be supplied.",
            )

        return self


class ProfileVisibilityUpdate(SchemaBase):
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
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(
            value.split(),
        )

        return normalized_value or None


class ProfileDeleteRequest(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    reason: str = Field(
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
        if not isinstance(value, str):
            return value

        return " ".join(
            value.split(),
        )


class ProfileRestoreRequest(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    reason: str = Field(
        min_length=3,
        max_length=500,
    )

    restore_as_public: bool = False

    @field_validator(
        "reason",
        mode="before",
    )
    @classmethod
    def normalize_reason(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, str):
            return value

        return " ".join(
            value.split(),
        )


class ProfileRead(ProfileBase, DatabaseSchema):
    pass


class ProfileAdminRead(ProfileRead):
    profile_key: str

    created_by_id: UUID | None
    updated_by_id: UUID | None
