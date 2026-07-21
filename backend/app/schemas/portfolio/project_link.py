from typing import Self
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.schemas.base import DatabaseSchema, SchemaBase
from app.schemas.portfolio.common import (
    PaginatedResponse,
    ProjectLinkType,
    ResourceUrl,
    SortOrder,
)


class ProjectLinkBase(SchemaBase):
    label: str = Field(
        min_length=2,
        max_length=100,
        examples=["View source code"],
    )

    url: ResourceUrl

    link_type: ProjectLinkType = ProjectLinkType.OTHER

    icon: str | None = Field(
        default=None,
        max_length=100,
        examples=["github"],
    )

    opens_in_new_tab: bool = True

    is_active: bool = True

    sort_order: SortOrder = 0

    @field_validator(
        "label",
        mode="before",
    )
    @classmethod
    def normalize_label(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, str):
            return value

        return " ".join(value.split())

    @field_validator(
        "url",
        mode="before",
    )
    @classmethod
    def normalize_url(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, str):
            return value

        return value.strip()

    @field_validator(
        "icon",
        mode="before",
    )
    @classmethod
    def normalize_icon(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        return normalized_value or None


class ProjectLinkCreate(ProjectLinkBase):
    model_config = ConfigDict(
        extra="forbid",
    )


class ProjectLinkUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    label: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    url: ResourceUrl | None = None

    link_type: ProjectLinkType | None = None

    icon: str | None = Field(
        default=None,
        max_length=100,
    )

    opens_in_new_tab: bool | None = None

    is_active: bool | None = None

    sort_order: SortOrder | None = None

    @field_validator(
        "label",
        mode="before",
    )
    @classmethod
    def normalize_label(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        return " ".join(value.split())

    @field_validator(
        "url",
        mode="before",
    )
    @classmethod
    def normalize_url(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        return value.strip()

    @field_validator(
        "icon",
        mode="before",
    )
    @classmethod
    def normalize_icon(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        return normalized_value or None

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one project-link field must be provided.")

        return self


class ProjectLinkRead(SchemaBase):
    id: UUID
    project_id: UUID

    label: str
    url: str
    link_type: ProjectLinkType

    icon: str | None = None

    opens_in_new_tab: bool

    sort_order: int


class ProjectLinkAdminRead(
    ProjectLinkBase,
    DatabaseSchema,
):
    project_id: UUID


class ProjectLinkStatusUpdate(SchemaBase):
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


class ProjectLinkDeleteRequest(SchemaBase):
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


class ProjectLinkRestoreRequest(SchemaBase):
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


ProjectLinkListResponse = PaginatedResponse[ProjectLinkRead]

AdminProjectLinkListResponse = PaginatedResponse[ProjectLinkAdminRead]
