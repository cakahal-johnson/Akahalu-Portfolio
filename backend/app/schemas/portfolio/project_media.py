from typing import Self
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.schemas.base import DatabaseSchema, SchemaBase
from app.schemas.portfolio.common import (
    PaginatedResponse,
    ProjectMediaType,
    ResourceUrl,
    SortOrder,
)


class ProjectMediaBase(SchemaBase):
    media_type: ProjectMediaType = ProjectMediaType.IMAGE

    url: ResourceUrl

    thumbnail_url: ResourceUrl | None = None

    alt_text: str | None = Field(
        default=None,
        max_length=255,
        examples=["Screenshot of the portfolio project dashboard."],
    )

    caption: str | None = Field(
        default=None,
        max_length=5000,
        examples=["Administrative dashboard showing portfolio analytics."],
    )

    provider: str | None = Field(
        default=None,
        max_length=50,
        examples=["cloudinary"],
    )

    provider_asset_id: str | None = Field(
        default=None,
        max_length=255,
        examples=["portfolio/projects/dashboard"],
    )

    mime_type: str | None = Field(
        default=None,
        max_length=100,
        examples=["image/webp"],
    )

    width: int | None = Field(
        default=None,
        gt=0,
        examples=[1920],
    )

    height: int | None = Field(
        default=None,
        gt=0,
        examples=[1080],
    )

    file_size_bytes: int | None = Field(
        default=None,
        gt=0,
        examples=[245760],
    )

    duration_seconds: int | None = Field(
        default=None,
        gt=0,
        examples=[90],
    )

    is_primary: bool = False

    sort_order: SortOrder = 0

    @field_validator(
        "url",
        "thumbnail_url",
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
        "alt_text",
        "caption",
        "provider",
        "provider_asset_id",
        "mime_type",
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

    @model_validator(mode="after")
    def validate_provider_metadata(self) -> Self:
        has_provider = self.provider is not None
        has_provider_asset_id = self.provider_asset_id is not None

        if has_provider != has_provider_asset_id:
            raise ValueError(
                "Provider and provider asset ID must be supplied together."
            )

        return self


class ProjectMediaCreate(ProjectMediaBase):
    model_config = ConfigDict(
        extra="forbid",
    )


class ProjectMediaUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    media_type: ProjectMediaType | None = None

    url: ResourceUrl | None = None

    thumbnail_url: ResourceUrl | None = None

    alt_text: str | None = Field(
        default=None,
        max_length=255,
    )

    caption: str | None = Field(
        default=None,
        max_length=5000,
    )

    provider: str | None = Field(
        default=None,
        max_length=50,
    )

    provider_asset_id: str | None = Field(
        default=None,
        max_length=255,
    )

    mime_type: str | None = Field(
        default=None,
        max_length=100,
    )

    width: int | None = Field(
        default=None,
        gt=0,
    )

    height: int | None = Field(
        default=None,
        gt=0,
    )

    file_size_bytes: int | None = Field(
        default=None,
        gt=0,
    )

    duration_seconds: int | None = Field(
        default=None,
        gt=0,
    )

    is_primary: bool | None = None

    sort_order: SortOrder | None = None

    @field_validator(
        "url",
        "thumbnail_url",
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
        "alt_text",
        "caption",
        "provider",
        "provider_asset_id",
        "mime_type",
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

    @model_validator(mode="after")
    def validate_update(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one project-media field must be provided.")

        provider_was_set = "provider" in self.model_fields_set
        asset_id_was_set = "provider_asset_id" in self.model_fields_set

        if provider_was_set != asset_id_was_set:
            raise ValueError("Provider and provider asset ID must be updated together.")

        has_provider = self.provider is not None
        has_provider_asset_id = self.provider_asset_id is not None

        if provider_was_set and has_provider != has_provider_asset_id:
            raise ValueError(
                "Provider and provider asset ID must both contain values "
                "or both be null."
            )

        return self


class ProjectMediaRead(SchemaBase):
    id: UUID
    project_id: UUID

    media_type: ProjectMediaType

    url: str
    thumbnail_url: str | None = None

    alt_text: str | None = None
    caption: str | None = None

    width: int | None = None
    height: int | None = None

    duration_seconds: int | None = None

    is_primary: bool
    sort_order: int


class ProjectMediaAdminRead(
    ProjectMediaBase,
    DatabaseSchema,
):
    project_id: UUID


class ProjectMediaDeleteRequest(SchemaBase):
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


class ProjectMediaRestoreRequest(SchemaBase):
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


class ProjectMediaPrimaryUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    is_primary: bool = True


ProjectMediaListResponse = PaginatedResponse[ProjectMediaRead]

AdminProjectMediaListResponse = PaginatedResponse[ProjectMediaAdminRead]
