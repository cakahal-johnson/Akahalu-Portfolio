from typing import Self
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.schemas.base import DatabaseSchema, SchemaBase
from app.schemas.portfolio.common import (
    HexColor,
    PaginatedResponse,
    Slug,
    SortOrder,
)


class ProjectCategoryBase(SchemaBase):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Web Development"],
    )

    slug: Slug

    description: str | None = Field(
        default=None,
        max_length=2000,
        examples=["Full-stack web applications, APIs, and responsive websites."],
    )

    icon: str | None = Field(
        default=None,
        max_length=100,
        examples=["code"],
    )

    color: HexColor | None = None

    is_active: bool = True

    sort_order: SortOrder = 0

    seo_title: str | None = Field(
        default=None,
        max_length=70,
        examples=["Web Development Projects"],
    )

    seo_description: str | None = Field(
        default=None,
        max_length=170,
        examples=[
            "Explore production-ready web development projects built with "
            "modern frontend and backend technologies."
        ],
    )

    @field_validator(
        "name",
        mode="before",
    )
    @classmethod
    def normalize_name(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, str):
            return value

        return " ".join(value.split())

    @field_validator(
        "slug",
        mode="before",
    )
    @classmethod
    def normalize_slug(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, str):
            return value

        return value.strip().lower()

    @field_validator(
        "description",
        "icon",
        "seo_title",
        "seo_description",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        return normalized_value or None

    @field_validator(
        "color",
        mode="before",
    )
    @classmethod
    def normalize_color(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = value.strip()

        return normalized_value.upper() or None


class ProjectCategoryCreate(ProjectCategoryBase):
    model_config = ConfigDict(
        extra="forbid",
    )


class ProjectCategoryUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    slug: Slug | None = None

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    icon: str | None = Field(
        default=None,
        max_length=100,
    )

    color: HexColor | None = None

    is_active: bool | None = None

    sort_order: SortOrder | None = None

    seo_title: str | None = Field(
        default=None,
        max_length=70,
    )

    seo_description: str | None = Field(
        default=None,
        max_length=170,
    )

    @field_validator(
        "name",
        mode="before",
    )
    @classmethod
    def normalize_name(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        return " ".join(value.split())

    @field_validator(
        "slug",
        mode="before",
    )
    @classmethod
    def normalize_slug(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        return value.strip().lower()

    @field_validator(
        "description",
        "icon",
        "seo_title",
        "seo_description",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        return normalized_value or None

    @field_validator(
        "color",
        mode="before",
    )
    @classmethod
    def normalize_color(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = value.strip()

        return normalized_value.upper() or None

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one project-category field must be provided.")

        return self


class ProjectCategorySummary(SchemaBase):
    id: UUID

    name: str
    slug: str

    description: str | None = None
    icon: str | None = None
    color: str | None = None

    sort_order: int


class ProjectCategoryRead(ProjectCategorySummary):
    seo_title: str | None = None
    seo_description: str | None = None


class ProjectCategoryAdminRead(
    ProjectCategoryBase,
    DatabaseSchema,
):
    pass


class ProjectCategoryDeleteRequest(SchemaBase):
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


class ProjectCategoryRestoreRequest(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    activate: bool = True

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


class ProjectCategoryStatusUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    is_active: bool

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


ProjectCategoryListResponse = PaginatedResponse[ProjectCategoryRead]

AdminProjectCategoryListResponse = PaginatedResponse[ProjectCategoryAdminRead]
