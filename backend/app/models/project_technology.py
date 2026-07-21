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
    from app.models.project_associations import ProjectTechnologyAssociation


class ProjectTechnology(BaseModel, ReprMixin):
    """
    Administrator-managed technology catalogue.

    Technologies represent programming languages, frameworks,
    databases, cloud providers, DevOps tooling, testing frameworks,
    operating systems, and other reusable skills that can be attached
    to multiple portfolio projects.
    """

    __tablename__ = "project_technologies"

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

    category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="other",
        server_default=text("'other'"),
        index=True,
    )

    icon: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    official_url: Mapped[str | None] = mapped_column(
        String(2048),
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

    project_associations: Mapped[list[ProjectTechnologyAssociation]] = relationship(
        "ProjectTechnologyAssociation",
        back_populates="technology",
        cascade="save-update, merge",
        passive_deletes=True,
        order_by="ProjectTechnologyAssociation.sort_order",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint(
            "length(btrim(name::text)) >= 2",
            name="project_technologies_name_not_blank",
        ),
        CheckConstraint(
            "length(btrim(slug::text)) >= 2",
            name="project_technologies_slug_not_blank",
        ),
        CheckConstraint(
            "description IS NULL OR length(btrim(description)) > 0",
            name="project_technologies_description_not_blank",
        ),
        CheckConstraint(
            (
                "category IN ("
                "'language',"
                "'framework',"
                "'library',"
                "'database',"
                "'platform',"
                "'cloud',"
                "'devops',"
                "'testing',"
                "'tool',"
                "'service',"
                "'other'"
                ")"
            ),
            name="project_technologies_category_allowed",
        ),
        CheckConstraint(
            "icon IS NULL OR length(btrim(icon)) > 0",
            name="project_technologies_icon_not_blank",
        ),
        CheckConstraint(
            ("official_url IS NULL OR length(btrim(official_url)) > 0"),
            name="project_technologies_official_url_not_blank",
        ),
        CheckConstraint(
            "color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'",
            name="project_technologies_color_hex_format",
        ),
        CheckConstraint(
            "sort_order >= 0",
            name="project_technologies_sort_order_non_negative",
        ),
        Index(
            "ix_project_technologies_public_listing",
            "category",
            "sort_order",
            "name",
            postgresql_where=text("deleted_at IS NULL AND is_active = true"),
        ),
    )

    @property
    def is_available(self) -> bool:
        return self.is_active and not self.is_deleted

    @property
    def is_programming_language(self) -> bool:
        return self.category == "language"

    @property
    def is_framework(self) -> bool:
        return self.category == "framework"
