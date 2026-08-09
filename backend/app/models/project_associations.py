from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import BaseModel, ReprMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.project_technology import ProjectTechnology


class ProjectTechnologyAssociation(
    BaseModel,
    ReprMixin,
):
    """
    Associate a portfolio project with a technology.

    The explicit association model stores ordering, featured state,
    timestamps, and soft-deletion history for each assignment.

    ``project`` is intentionally not loaded automatically. A project
    normally loads its association collection, so eagerly loading the
    project back from every association would recursively expand the
    same Project -> Association -> Project graph.

    ``technology`` remains joined because project response schemas need
    technology summaries for every assignment.
    """

    __tablename__ = "project_technology_associations"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    technology_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "project_technologies.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text(
            "false",
        ),
        index=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text(
            "0",
        ),
    )

    project: Mapped[Project] = relationship(
        "Project",
        back_populates="technology_associations",
        lazy="noload",
    )

    technology: Mapped[ProjectTechnology] = relationship(
        "ProjectTechnology",
        back_populates="project_associations",
        lazy="joined",
    )

    __table_args__ = (
        CheckConstraint(
            "sort_order >= 0",
            name=("project_technology_associations_sort_order_non_negative"),
        ),
        Index(
            "uq_project_technology_associations_active_pair",
            "project_id",
            "technology_id",
            unique=True,
            postgresql_where=text(
                "deleted_at IS NULL",
            ),
        ),
        Index(
            "ix_project_technology_associations_project_listing",
            "project_id",
            "is_featured",
            "sort_order",
            "created_at",
            postgresql_where=text(
                "deleted_at IS NULL",
            ),
        ),
        Index(
            "ix_project_technology_associations_technology_listing",
            "technology_id",
            "project_id",
            postgresql_where=text(
                "deleted_at IS NULL",
            ),
        ),
    )

    @property
    def is_available(self) -> bool:
        return not self.is_deleted
