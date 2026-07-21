from typing import Self
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.schemas.base import DatabaseSchema, SchemaBase
from app.schemas.portfolio.common import (
    HexColor,
    PaginatedResponse,
    ProjectTechnologyCategory,
    ResourceUrl,
    Slug,
    SortOrder,
)


class ProjectTechnologyBase(SchemaBase):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["FastAPI"],
    )

    slug: Slug

    description: str | None = Field(
        default=None,
        max_length=2000,
        examples=["A modern Python framework for building high-performance APIs."],
    )

    category: ProjectTechnologyCategory = ProjectTechnologyCategory.OTHER

    icon: str | None = Field(
        default=None,
        max_length=100,
        examples=["fastapi"],
    )

    official_url: ResourceUrl | None = None

    color: HexColor | None = None

    is_active: bool = True

    sort_order: SortOrder = 0

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
        "official_url",
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


class ProjectTechnologyCreate(ProjectTechnologyBase):
    model_config = ConfigDict(
        extra="forbid",
    )


class ProjectTechnologyUpdate(SchemaBase):
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

    category: ProjectTechnologyCategory | None = None

    icon: str | None = Field(
        default=None,
        max_length=100,
    )

    official_url: ResourceUrl | None = None

    color: HexColor | None = None

    is_active: bool | None = None

    sort_order: SortOrder | None = None

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
        "official_url",
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
            raise ValueError("At least one project-technology field must be provided.")

        return self


class ProjectTechnologySummary(SchemaBase):
    id: UUID

    name: str
    slug: str
    category: ProjectTechnologyCategory

    icon: str | None = None
    official_url: str | None = None
    color: str | None = None

    sort_order: int


class ProjectTechnologyRead(ProjectTechnologySummary):
    description: str | None = None


class ProjectTechnologyAdminRead(
    ProjectTechnologyBase,
    DatabaseSchema,
):
    pass


class ProjectTechnologyDeleteRequest(SchemaBase):
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


class ProjectTechnologyRestoreRequest(SchemaBase):
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


class ProjectTechnologyStatusUpdate(SchemaBase):
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


ProjectTechnologyListResponse = PaginatedResponse[ProjectTechnologyRead]

AdminProjectTechnologyListResponse = PaginatedResponse[ProjectTechnologyAdminRead]
