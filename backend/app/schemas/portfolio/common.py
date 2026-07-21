from enum import StrEnum
from typing import Annotated, Generic, TypeVar
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator

from app.schemas.base import SchemaBase


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ProjectVisibility(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class ProjectTechnologyCategory(StrEnum):
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    DATABASE = "database"
    PLATFORM = "platform"
    CLOUD = "cloud"
    DEVOPS = "devops"
    TESTING = "testing"
    TOOL = "tool"
    SERVICE = "service"
    OTHER = "other"


class ProjectLinkType(StrEnum):
    REPOSITORY = "repository"
    LIVE_DEMO = "live_demo"
    DOCUMENTATION = "documentation"
    CASE_STUDY = "case_study"
    VIDEO = "video"
    DOWNLOAD = "download"
    APP_STORE = "app_store"
    PLAY_STORE = "play_store"
    DESIGN = "design"
    ARTICLE = "article"
    API = "api"
    OTHER = "other"


class ProjectMediaType(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    DEMO = "demo"
    OTHER = "other"


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


class ProjectSortField(StrEnum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PUBLISHED_AT = "published_at"
    TITLE = "title"
    SORT_ORDER = "sort_order"


class ProjectCategorySortField(StrEnum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    NAME = "name"
    SORT_ORDER = "sort_order"


class ProjectTechnologySortField(StrEnum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    NAME = "name"
    CATEGORY = "category"
    SORT_ORDER = "sort_order"


Slug = Annotated[
    str,
    Field(
        min_length=2,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        examples=["akahalu-portfolio-api"],
    ),
]

HexColor = Annotated[
    str,
    Field(
        pattern=r"^#[0-9A-Fa-f]{6}$",
        examples=["#2563EB"],
    ),
]

SortOrder = Annotated[
    int,
    Field(
        ge=0,
        examples=[0],
    ),
]

ResourceUrl = Annotated[
    str,
    Field(
        min_length=1,
        max_length=2048,
        examples=["https://example.com"],
    ),
]


class PaginationQuery(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
    )


class PortfolioSearchQuery(PaginationQuery):
    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    @field_validator(
        "search",
        mode="before",
    )
    @classmethod
    def normalize_search(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        return normalized_value or None


class PublicProjectListQuery(PortfolioSearchQuery):
    category_slug: Slug | None = None
    technology_slugs: list[Slug] = Field(
        default_factory=list,
        max_length=20,
    )
    featured: bool | None = None

    sort_by: ProjectSortField = ProjectSortField.SORT_ORDER
    sort_direction: SortDirection = SortDirection.ASC

    @field_validator("technology_slugs")
    @classmethod
    def validate_technology_slugs(
        cls,
        technology_slugs: list[str],
    ) -> list[str]:
        if len(technology_slugs) != len(set(technology_slugs)):
            raise ValueError("Technology slugs must be unique.")

        return technology_slugs


class AdminProjectListQuery(PortfolioSearchQuery):
    status: ProjectStatus | None = None
    visibility: ProjectVisibility | None = None
    category_id: UUID | None = None
    technology_id: UUID | None = None
    is_featured: bool | None = None
    include_deleted: bool = False

    sort_by: ProjectSortField = ProjectSortField.CREATED_AT
    sort_direction: SortDirection = SortDirection.DESC


class AdminProjectCategoryListQuery(PortfolioSearchQuery):
    is_active: bool | None = None
    include_deleted: bool = False

    sort_by: ProjectCategorySortField = ProjectCategorySortField.SORT_ORDER
    sort_direction: SortDirection = SortDirection.ASC


class AdminProjectTechnologyListQuery(PortfolioSearchQuery):
    category: ProjectTechnologyCategory | None = None
    is_active: bool | None = None
    include_deleted: bool = False

    sort_by: ProjectTechnologySortField = ProjectTechnologySortField.SORT_ORDER
    sort_direction: SortDirection = SortDirection.ASC


PaginationItem = TypeVar(
    "PaginationItem",
    bound=SchemaBase,
)


class PaginatedResponse(
    SchemaBase,
    Generic[PaginationItem],
):
    items: list[PaginationItem] = Field(
        default_factory=list,
    )

    page: int = Field(
        ge=1,
    )

    page_size: int = Field(
        ge=1,
    )

    total_items: int = Field(
        ge=0,
    )

    total_pages: int = Field(
        ge=0,
    )

    has_next_page: bool
    has_previous_page: bool
