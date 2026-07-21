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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, ReprMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.project_technology import ProjectTechnology


class ProjectTechnologyAssociation(BaseModel, ReprMixin):
    """
    Associates a portfolio project with a technology.

    This explicit association model supports relationship metadata such as
    display order and featured status. It also preserves timestamps and
    soft-deletion history for administrative auditing and restoration.

    Public queries must exclude soft-deleted associations and technologies
    that are inactive or soft-deleted.
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
        server_default=text("false"),
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
        back_populates="technology_associations",
        lazy="joined",
    )

    technology: Mapped[ProjectTechnology] = relationship(
        "ProjectTechnology",
        back_populates="project_associations",
        lazy="joined",
    )

    __table_args__ = (
        CheckConstraint(
            "sort_order >= 0",
            name="project_technology_associations_sort_order_non_negative",
        ),
        Index(
            "uq_project_technology_associations_active_pair",
            "project_id",
            "technology_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_project_technology_associations_project_listing",
            "project_id",
            "is_featured",
            "sort_order",
            "created_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_project_technology_associations_technology_listing",
            "technology_id",
            "project_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    @property
    def is_available(self) -> bool:
        return not self.is_deleted
