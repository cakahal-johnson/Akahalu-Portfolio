from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.schemas.base import DatabaseSchema, SchemaBase
from app.schemas.portfolio.common import (
    PaginatedResponse,
    ProjectStatus,
    ProjectVisibility,
    ResourceUrl,
    Slug,
    SortOrder,
)
from app.schemas.portfolio.project_category import (
    ProjectCategorySummary,
)
from app.schemas.portfolio.project_link import ProjectLinkRead
from app.schemas.portfolio.project_media import ProjectMediaRead
from app.schemas.portfolio.project_technology import (
    ProjectTechnologySummary,
)


class ProjectTechnologyAssignmentCreate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    technology_id: UUID

    is_featured: bool = False

    sort_order: SortOrder = 0


class ProjectTechnologyAssignmentRead(SchemaBase):
    technology: ProjectTechnologySummary

    is_featured: bool

    sort_order: int


class ProjectBase(SchemaBase):
    title: str = Field(
        min_length=2,
        max_length=200,
        examples=["Akahalu Portfolio"],
    )

    slug: Slug

    short_description: str = Field(
        min_length=10,
        max_length=500,
        examples=[
            "A production-ready personal portfolio built with "
            "FastAPI, PostgreSQL, and Next.js."
        ],
    )

    description: str = Field(
        min_length=20,
        max_length=50_000,
        examples=[
            "Akahalu Portfolio is a full-stack platform designed "
            "to present professional projects, technical skills, "
            "experience, and contact information."
        ],
    )

    problem_statement: str | None = Field(
        default=None,
        max_length=20_000,
    )

    solution_summary: str | None = Field(
        default=None,
        max_length=20_000,
    )

    key_features: str | None = Field(
        default=None,
        max_length=30_000,
    )

    technical_highlights: str | None = Field(
        default=None,
        max_length=30_000,
    )

    category_id: UUID | None = None

    status: ProjectStatus = ProjectStatus.DRAFT

    visibility: ProjectVisibility = ProjectVisibility.PRIVATE

    is_featured: bool = False

    sort_order: SortOrder = 0

    repository_url: ResourceUrl | None = None

    live_url: ResourceUrl | None = None

    case_study_url: ResourceUrl | None = None

    thumbnail_url: ResourceUrl | None = None

    started_at: datetime | None = None

    completed_at: datetime | None = None

    published_at: datetime | None = None

    seo_title: str | None = Field(
        default=None,
        max_length=70,
    )

    seo_description: str | None = Field(
        default=None,
        max_length=170,
    )

    @field_validator(
        "title",
        "short_description",
        mode="before",
    )
    @classmethod
    def normalize_single_line_text(
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
        "problem_statement",
        "solution_summary",
        "key_features",
        "technical_highlights",
        mode="before",
    )
    @classmethod
    def normalize_long_text(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator(
        "repository_url",
        "live_url",
        "case_study_url",
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
        "seo_title",
        "seo_description",
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

    @model_validator(mode="after")
    def validate_project_dates_and_status(self) -> Self:
        if (
            self.started_at is not None
            and self.completed_at is not None
            and self.completed_at < self.started_at
        ):
            raise ValueError("Project completion date cannot be before its start date.")

        if self.status is ProjectStatus.PUBLISHED and self.published_at is None:
            raise ValueError("Published projects must include a publication timestamp.")

        return self


class ProjectCreate(ProjectBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    technology_assignments: list[ProjectTechnologyAssignmentCreate] = Field(
        default_factory=list,
        max_length=100,
    )

    @model_validator(mode="after")
    def validate_unique_technology_assignments(self) -> Self:
        technology_ids = [
            assignment.technology_id for assignment in self.technology_assignments
        ]

        if len(technology_ids) != len(set(technology_ids)):
            raise ValueError("Project technology assignments must be unique.")

        return self


class ProjectUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    slug: Slug | None = None

    short_description: str | None = Field(
        default=None,
        min_length=10,
        max_length=500,
    )

    description: str | None = Field(
        default=None,
        min_length=20,
        max_length=50_000,
    )

    problem_statement: str | None = Field(
        default=None,
        max_length=20_000,
    )

    solution_summary: str | None = Field(
        default=None,
        max_length=20_000,
    )

    key_features: str | None = Field(
        default=None,
        max_length=30_000,
    )

    technical_highlights: str | None = Field(
        default=None,
        max_length=30_000,
    )

    category_id: UUID | None = None

    status: ProjectStatus | None = None

    visibility: ProjectVisibility | None = None

    is_featured: bool | None = None

    sort_order: SortOrder | None = None

    repository_url: ResourceUrl | None = None

    live_url: ResourceUrl | None = None

    case_study_url: ResourceUrl | None = None

    thumbnail_url: ResourceUrl | None = None

    started_at: datetime | None = None

    completed_at: datetime | None = None

    published_at: datetime | None = None

    seo_title: str | None = Field(
        default=None,
        max_length=70,
    )

    seo_description: str | None = Field(
        default=None,
        max_length=170,
    )

    technology_assignments: list[ProjectTechnologyAssignmentCreate] | None = Field(
        default=None,
        max_length=100,
    )

    @field_validator(
        "title",
        "short_description",
        mode="before",
    )
    @classmethod
    def normalize_single_line_text(
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
        "problem_statement",
        "solution_summary",
        "key_features",
        "technical_highlights",
        mode="before",
    )
    @classmethod
    def normalize_long_text(
        cls,
        value: object,
    ) -> object:
        if value is None or not isinstance(value, str):
            return value

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator(
        "repository_url",
        "live_url",
        "case_study_url",
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
        "seo_title",
        "seo_description",
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

    @model_validator(mode="after")
    def validate_update(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one project field must be provided.")

        if (
            self.started_at is not None
            and self.completed_at is not None
            and self.completed_at < self.started_at
        ):
            raise ValueError("Project completion date cannot be before its start date.")

        if (
            self.status is ProjectStatus.PUBLISHED
            and "published_at" in self.model_fields_set
            and self.published_at is None
        ):
            raise ValueError(
                "A project cannot be published with a null publication timestamp."
            )

        if self.technology_assignments is not None:
            technology_ids = [
                assignment.technology_id for assignment in self.technology_assignments
            ]

            if len(technology_ids) != len(set(technology_ids)):
                raise ValueError("Project technology assignments must be unique.")

        return self


class ProjectSummary(SchemaBase):
    id: UUID

    title: str
    slug: str

    short_description: str

    status: ProjectStatus
    visibility: ProjectVisibility

    is_featured: bool
    sort_order: int

    thumbnail_url: str | None = None

    started_at: datetime | None = None
    completed_at: datetime | None = None
    published_at: datetime | None = None

    category: ProjectCategorySummary | None = None

    technologies: list[ProjectTechnologySummary] = Field(
        default_factory=list,
    )


class ProjectRead(ProjectSummary):
    description: str

    problem_statement: str | None = None
    solution_summary: str | None = None
    key_features: str | None = None
    technical_highlights: str | None = None

    repository_url: str | None = None
    live_url: str | None = None
    case_study_url: str | None = None

    seo_title: str | None = None
    seo_description: str | None = None

    media: list[ProjectMediaRead] = Field(
        default_factory=list,
    )

    links: list[ProjectLinkRead] = Field(
        default_factory=list,
    )


class ProjectAdminRead(
    ProjectBase,
    DatabaseSchema,
):
    created_by_id: UUID | None = None
    updated_by_id: UUID | None = None

    category: ProjectCategorySummary | None = None

    technology_assignments: list[ProjectTechnologyAssignmentRead] = Field(
        default_factory=list,
    )

    media: list[ProjectMediaRead] = Field(
        default_factory=list,
    )

    links: list[ProjectLinkRead] = Field(
        default_factory=list,
    )


class ProjectStatusUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    status: ProjectStatus

    published_at: datetime | None = None

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

    @model_validator(mode="after")
    def validate_publishing_timestamp(self) -> Self:
        if self.status is ProjectStatus.PUBLISHED and self.published_at is None:
            raise ValueError("Publishing a project requires a publication timestamp.")

        return self


class ProjectVisibilityUpdate(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    visibility: ProjectVisibility

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


class ProjectFeaturedUpdate(SchemaBase):
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
        if value is None or not isinstance(value, str):
            return value

        normalized_value = " ".join(value.split())

        return normalized_value or None


class ProjectDeleteRequest(SchemaBase):
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


class ProjectRestoreRequest(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
    )

    status: ProjectStatus = ProjectStatus.DRAFT

    visibility: ProjectVisibility = ProjectVisibility.PRIVATE

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

    @model_validator(mode="after")
    def prevent_direct_published_restore(self) -> Self:
        if self.status is ProjectStatus.PUBLISHED:
            raise ValueError("A restored project must be reviewed before publication.")

        return self


ProjectListResponse = PaginatedResponse[ProjectSummary]

AdminProjectListResponse = PaginatedResponse[ProjectAdminRead]
