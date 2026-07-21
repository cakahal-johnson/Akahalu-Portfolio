from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
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
    from app.models.project_associations import ProjectTechnologyAssociation
    from app.models.project_category import ProjectCategory
    from app.models.project_link import ProjectLink
    from app.models.project_media import ProjectMedia
    from app.models.user import User


class Project(BaseModel, ReprMixin):
    """
    Represents a portfolio project and its public case-study content.

    Projects support controlled publication, visibility, categorization,
    ordered technologies, media assets, and supplementary external links.

    Public repository queries must exclude soft-deleted projects and require
    published status, public visibility, and a publication timestamp.
    """

    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        CITEXT,
        nullable=False,
        unique=True,
        index=True,
    )

    short_description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    problem_statement: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    solution_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    key_features: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    technical_highlights: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "project_categories.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
        server_default=text("'draft'"),
        index=True,
    )

    visibility: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="private",
        server_default=text("'private'"),
        index=True,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    repository_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    live_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    case_study_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    thumbnail_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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

    category: Mapped[ProjectCategory | None] = relationship(
        "ProjectCategory",
        back_populates="projects",
        lazy="joined",
    )

    media: Mapped[list[ProjectMedia]] = relationship(
        "ProjectMedia",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ProjectMedia.sort_order",
        lazy="selectin",
    )

    links: Mapped[list[ProjectLink]] = relationship(
        "ProjectLink",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ProjectLink.sort_order",
        lazy="selectin",
    )

    technology_associations: Mapped[list[ProjectTechnologyAssociation]] = relationship(
        "ProjectTechnologyAssociation",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ProjectTechnologyAssociation.sort_order",
        lazy="selectin",
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
            "length(btrim(title)) >= 2",
            name="projects_title_not_blank",
        ),
        CheckConstraint(
            "length(btrim(slug::text)) >= 2",
            name="projects_slug_not_blank",
        ),
        CheckConstraint(
            "length(btrim(short_description)) >= 10",
            name="projects_short_description_min_length",
        ),
        CheckConstraint(
            "length(btrim(description)) >= 20",
            name="projects_description_min_length",
        ),
        CheckConstraint(
            ("problem_statement IS NULL OR length(btrim(problem_statement)) > 0"),
            name="projects_problem_statement_not_blank",
        ),
        CheckConstraint(
            ("solution_summary IS NULL OR length(btrim(solution_summary)) > 0"),
            name="projects_solution_summary_not_blank",
        ),
        CheckConstraint(
            ("key_features IS NULL OR length(btrim(key_features)) > 0"),
            name="projects_key_features_not_blank",
        ),
        CheckConstraint(
            ("technical_highlights IS NULL OR length(btrim(technical_highlights)) > 0"),
            name="projects_technical_highlights_not_blank",
        ),
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="projects_status_allowed",
        ),
        CheckConstraint(
            "visibility IN ('public', 'private', 'unlisted')",
            name="projects_visibility_allowed",
        ),
        CheckConstraint(
            "sort_order >= 0",
            name="projects_sort_order_non_negative",
        ),
        CheckConstraint(
            ("repository_url IS NULL OR length(btrim(repository_url)) > 0"),
            name="projects_repository_url_not_blank",
        ),
        CheckConstraint(
            "live_url IS NULL OR length(btrim(live_url)) > 0",
            name="projects_live_url_not_blank",
        ),
        CheckConstraint(
            ("case_study_url IS NULL OR length(btrim(case_study_url)) > 0"),
            name="projects_case_study_url_not_blank",
        ),
        CheckConstraint(
            ("thumbnail_url IS NULL OR length(btrim(thumbnail_url)) > 0"),
            name="projects_thumbnail_url_not_blank",
        ),
        CheckConstraint(
            (
                "completed_at IS NULL "
                "OR started_at IS NULL "
                "OR completed_at >= started_at"
            ),
            name="projects_completion_not_before_start",
        ),
        CheckConstraint(
            "status <> 'published' OR published_at IS NOT NULL",
            name="projects_published_requires_timestamp",
        ),
        CheckConstraint(
            "seo_title IS NULL OR length(btrim(seo_title)) > 0",
            name="projects_seo_title_not_blank",
        ),
        CheckConstraint(
            ("seo_description IS NULL OR length(btrim(seo_description)) > 0"),
            name="projects_seo_description_not_blank",
        ),
        Index(
            "ix_projects_admin_listing",
            "status",
            "visibility",
            "is_featured",
            "sort_order",
            "created_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_projects_category_listing",
            "category_id",
            "status",
            "sort_order",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_projects_public_listing",
            "is_featured",
            "sort_order",
            "published_at",
            postgresql_where=text(
                "deleted_at IS NULL "
                "AND status = 'published' "
                "AND visibility = 'public' "
                "AND published_at IS NOT NULL"
            ),
        ),
    )

    @property
    def is_published(self) -> bool:
        return self.status == "published" and self.published_at is not None

    @property
    def is_publicly_visible(self) -> bool:
        return self.is_published and self.visibility == "public" and not self.is_deleted

    @property
    def is_archived(self) -> bool:
        return self.status == "archived"

    @property
    def primary_media(self) -> ProjectMedia | None:
        return next(
            (
                media
                for media in self.media
                if media.is_primary and not media.is_deleted
            ),
            None,
        )
