from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, ReprMixin

if TYPE_CHECKING:
    from app.models.project import Project


class ProjectLink(BaseModel, ReprMixin):
    """
    Represents an additional external resource associated with a project.

    Project links supplement the primary repository, live-site, and case-study
    URLs stored on the project itself. They support multiple repositories,
    documentation pages, app-store listings, design files, articles, videos,
    downloads, and other relevant resources.

    Public queries must exclude inactive and soft-deleted links.
    """

    __tablename__ = "project_links"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    label: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    link_type: Mapped[str] = mapped_column(
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

    opens_in_new_tab: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
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

    project: Mapped[Project] = relationship(
        "Project",
        back_populates="links",
        lazy="joined",
    )

    __table_args__ = (
        CheckConstraint(
            "length(btrim(label)) >= 2",
            name="project_links_label_not_blank",
        ),
        CheckConstraint(
            "length(btrim(url)) > 0",
            name="project_links_url_not_blank",
        ),
        CheckConstraint(
            (
                "link_type IN ("
                "'repository', "
                "'live_demo', "
                "'documentation', "
                "'case_study', "
                "'video', "
                "'download', "
                "'app_store', "
                "'play_store', "
                "'design', "
                "'article', "
                "'api', "
                "'other'"
                ")"
            ),
            name="project_links_type_allowed",
        ),
        CheckConstraint(
            "icon IS NULL OR length(btrim(icon)) > 0",
            name="project_links_icon_not_blank",
        ),
        CheckConstraint(
            "sort_order >= 0",
            name="project_links_sort_order_non_negative",
        ),
        Index(
            "ix_project_links_project_listing",
            "project_id",
            "is_active",
            "sort_order",
            "created_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_project_links_public_listing",
            "project_id",
            "sort_order",
            postgresql_where=text("deleted_at IS NULL AND is_active = true"),
        ),
        Index(
            "uq_project_links_active_project_url",
            "project_id",
            "url",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    @property
    def is_available(self) -> bool:
        return self.is_active and not self.is_deleted

    @property
    def is_repository(self) -> bool:
        return self.link_type == "repository"

    @property
    def is_store_listing(self) -> bool:
        return self.link_type in {
            "app_store",
            "play_store",
        }
