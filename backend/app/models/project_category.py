from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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
    from app.models.project import Project


class ProjectCategory(BaseModel, ReprMixin):
    """
    Administrator-managed project category.

    Categories provide a stable taxonomy for portfolio projects and are
    intentionally independent of frontend presentation.
    """

    __tablename__ = "project_categories"

    name: Mapped[str] = mapped_column(
        CITEXT,
        nullable=False,
        unique=True,
        index=True,
    )

    slug: Mapped[str] = mapped_column(
        CITEXT,
        nullable=False,
        unique=True,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    icon: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    color: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        index=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    seo_title: Mapped[str | None] = mapped_column(
        String(70),
        nullable=True,
    )

    seo_description: Mapped[str | None] = mapped_column(
        String(170),
        nullable=True,
    )

    projects: Mapped[list[Project]] = relationship(
        "Project",
        back_populates="category",
        lazy="selectin",
        passive_deletes=True,
        order_by="Project.sort_order",
    )

    __table_args__ = (
        CheckConstraint(
            "length(btrim(name::text)) >= 2",
            name="project_categories_name_not_blank",
        ),
        CheckConstraint(
            "length(btrim(slug::text)) >= 2",
            name="project_categories_slug_not_blank",
        ),
        CheckConstraint(
            "description IS NULL OR length(btrim(description)) > 0",
            name="project_categories_description_not_blank",
        ),
        CheckConstraint(
            "icon IS NULL OR length(btrim(icon)) > 0",
            name="project_categories_icon_not_blank",
        ),
        CheckConstraint(
            "color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'",
            name="project_categories_color_hex_format",
        ),
        CheckConstraint(
            "sort_order >= 0",
            name="project_categories_sort_order_non_negative",
        ),
        CheckConstraint(
            "seo_title IS NULL OR length(btrim(seo_title)) > 0",
            name="project_categories_seo_title_not_blank",
        ),
        CheckConstraint(
            ("seo_description IS NULL OR length(btrim(seo_description)) > 0"),
            name="project_categories_seo_description_not_blank",
        ),
        Index(
            "ix_project_categories_public_listing",
            "is_active",
            "sort_order",
            "name",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    @property
    def is_available(self) -> bool:
        return self.is_active and not self.is_deleted
