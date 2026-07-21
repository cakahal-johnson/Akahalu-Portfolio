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
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, ReprMixin

if TYPE_CHECKING:
    from app.models.project import Project


class ProjectMedia(BaseModel, ReprMixin):
    """
    Represents an ordered media asset associated with a portfolio project.

    Media records store references to externally hosted or application-managed
    assets. Raw binary file contents are not stored in this table.

    A project may contain multiple media records, but only one active,
    non-deleted item may be designated as primary.
    """

    __tablename__ = "project_media"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    media_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="image",
        server_default=text("'image'"),
        index=True,
    )

    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    thumbnail_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    alt_text: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    caption: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    provider_asset_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    width: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    height: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    file_size_bytes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    is_primary: Mapped[bool] = mapped_column(
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
        back_populates="media",
        lazy="joined",
    )

    __table_args__ = (
        CheckConstraint(
            ("media_type IN ('image', 'video', 'document', 'demo', 'other')"),
            name="project_media_type_allowed",
        ),
        CheckConstraint(
            "length(btrim(url)) > 0",
            name="project_media_url_not_blank",
        ),
        CheckConstraint(
            ("thumbnail_url IS NULL OR length(btrim(thumbnail_url)) > 0"),
            name="project_media_thumbnail_url_not_blank",
        ),
        CheckConstraint(
            "alt_text IS NULL OR length(btrim(alt_text)) > 0",
            name="project_media_alt_text_not_blank",
        ),
        CheckConstraint(
            "caption IS NULL OR length(btrim(caption)) > 0",
            name="project_media_caption_not_blank",
        ),
        CheckConstraint(
            "provider IS NULL OR length(btrim(provider)) > 0",
            name="project_media_provider_not_blank",
        ),
        CheckConstraint(
            ("provider_asset_id IS NULL OR length(btrim(provider_asset_id)) > 0"),
            name="project_media_provider_asset_id_not_blank",
        ),
        CheckConstraint(
            "mime_type IS NULL OR length(btrim(mime_type)) > 0",
            name="project_media_mime_type_not_blank",
        ),
        CheckConstraint(
            "width IS NULL OR width > 0",
            name="project_media_width_positive",
        ),
        CheckConstraint(
            "height IS NULL OR height > 0",
            name="project_media_height_positive",
        ),
        CheckConstraint(
            "file_size_bytes IS NULL OR file_size_bytes > 0",
            name="project_media_file_size_positive",
        ),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="project_media_duration_positive",
        ),
        CheckConstraint(
            "sort_order >= 0",
            name="project_media_sort_order_non_negative",
        ),
        Index(
            "ix_project_media_project_listing",
            "project_id",
            "sort_order",
            "created_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_project_media_primary_per_project",
            "project_id",
            unique=True,
            postgresql_where=text("is_primary = true AND deleted_at IS NULL"),
        ),
        Index(
            "ix_project_media_provider_asset",
            "provider",
            "provider_asset_id",
            postgresql_where=text(
                "provider IS NOT NULL AND provider_asset_id IS NOT NULL"
            ),
        ),
    )

    @property
    def is_image(self) -> bool:
        return self.media_type == "image"

    @property
    def is_video(self) -> bool:
        return self.media_type == "video"

    @property
    def has_dimensions(self) -> bool:
        return self.width is not None and self.height is not None
