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
        examples=["Screenshot of the Akahalu Portfolio dashboard"],
    )

    caption: str | None = Field(
        default=None,
        max_length=5_000,
        examples=["Administrative dashboard showing portfolio project statistics."],
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
        le=100_000,
    )

    height: int | None = Field(
        default=None,
        gt=0,
        le=100_000,
    )

    file_size_bytes: int | None = Field(
        default=None,
        gt=0,
        le=10_737_418_240,
    )

    duration_seconds: int | None = Field(
        default=None,
        gt=0,
        le=604_800,
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

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator(
        "alt_text",
        "provider",
        "provider_asset_id",
        "mime_type",
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
        "caption",
        mode="before",
    )
    @classmethod
    def normalize_caption(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator(
        "mime_type",
        mode="after",
    )
    @classmethod
    def normalize_mime_type(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return value.lower()

    @model_validator(mode="after")
    def validate_media_metadata(self) -> Self:
        if (self.width is None) != (self.height is None):
            raise ValueError("Media width and height must be provided together.")

        if (
            self.media_type is ProjectMediaType.IMAGE
            and self.duration_seconds is not None
        ):
            raise ValueError("Image media cannot include a duration.")

        if (
            self.media_type
            not in {
                ProjectMediaType.VIDEO,
                ProjectMediaType.DEMO,
            }
            and self.duration_seconds is not None
        ):
            raise ValueError("Duration is only supported for video or demo media.")

        if self.thumbnail_url is not None and self.thumbnail_url == self.url:
            raise ValueError(
                "The thumbnail URL must differ from the primary media URL."
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
        max_length=5_000,
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
        le=100_000,
    )

    height: int | None = Field(
        default=None,
        gt=0,
        le=100_000,
    )

    file_size_bytes: int | None = Field(
        default=None,
        gt=0,
        le=10_737_418_240,
    )

    duration_seconds: int | None = Field(
        default=None,
        gt=0,
        le=604_800,
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

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator(
        "alt_text",
        "provider",
        "provider_asset_id",
        "mime_type",
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
        "caption",
        mode="before",
    )
    @classmethod
    def normalize_caption(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator(
        "mime_type",
        mode="after",
    )
    @classmethod
    def normalize_mime_type(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return value.lower()

    @model_validator(mode="after")
    def validate_update(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one project media field must be provided.")

        width_was_provided = "width" in self.model_fields_set
        height_was_provided = "height" in self.model_fields_set

        if width_was_provided != height_was_provided:
            raise ValueError("Media width and height must be updated together.")

        if (
            self.media_type is ProjectMediaType.IMAGE
            and self.duration_seconds is not None
        ):
            raise ValueError("Image media cannot include a duration.")

        if (
            self.media_type is not None
            and self.media_type
            not in {
                ProjectMediaType.VIDEO,
                ProjectMediaType.DEMO,
            }
            and self.duration_seconds is not None
        ):
            raise ValueError("Duration is only supported for video or demo media.")

        if (
            self.url is not None
            and self.thumbnail_url is not None
            and self.url == self.thumbnail_url
        ):
            raise ValueError(
                "The thumbnail URL must differ from the primary media URL."
            )

        return self


class ProjectMediaRead(
    ProjectMediaBase,
    DatabaseSchema,
):
    project_id: UUID


class ProjectMediaAdminRead(ProjectMediaRead):
    """
    Administrative representation of a project media record.

    This currently exposes the same persisted fields as ProjectMediaRead,
    including database timestamps and soft-deletion metadata. It remains a
    separate schema so administrative responses can evolve independently.
    """


class ProjectMediaSummary(SchemaBase):
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


class ProjectMediaPrimaryUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    is_primary: bool = True

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

    restore_as_primary: bool = False

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


ProjectMediaListResponse = PaginatedResponse[ProjectMediaRead]

AdminProjectMediaListResponse = PaginatedResponse[ProjectMediaAdminRead]
