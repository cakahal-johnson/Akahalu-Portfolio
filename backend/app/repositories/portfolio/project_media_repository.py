from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import (
    asc,
    desc,
    exists,
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.models.project_media import ProjectMedia
from app.repositories.base import BaseRepository


class ProjectMediaRepository(
    BaseRepository[ProjectMedia],
):
    """Database operations for portfolio project media."""

    def __init__(self) -> None:
        super().__init__(ProjectMedia)

    async def get_by_id(
        self,
        session: AsyncSession,
        media_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ProjectMedia | None:
        """
        Return a project media record by UUID.

        Soft-deleted media records are excluded unless
        ``include_deleted`` is enabled.
        """

        statement = select(ProjectMedia).where(
            ProjectMedia.id == media_id,
        )

        if not include_deleted:
            statement = statement.where(
                ProjectMedia.deleted_at.is_(None),
            )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def get_primary(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ProjectMedia | None:
        """
        Return the primary media record for a project.

        The database permits only one active primary media record for
        each project.
        """

        statement = select(ProjectMedia).where(
            ProjectMedia.project_id == project_id,
            ProjectMedia.is_primary.is_(True),
        )

        if not include_deleted:
            statement = statement.where(
                ProjectMedia.deleted_at.is_(None),
            )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def list_for_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        media_type: str | None = None,
    ) -> Sequence[ProjectMedia]:
        """
        Return all active media records belonging to a project.

        Results are ordered with primary media first, followed by
        configured sort order, creation time, and UUID.
        """

        filters: list[ColumnElement[bool]] = [
            ProjectMedia.project_id == project_id,
            ProjectMedia.deleted_at.is_(None),
        ]

        normalized_media_type = (
            media_type.strip().lower() if media_type and media_type.strip() else None
        )

        if normalized_media_type:
            filters.append(
                ProjectMedia.media_type == normalized_media_type,
            )

        statement = (
            select(ProjectMedia)
            .where(*filters)
            .order_by(
                ProjectMedia.is_primary.desc(),
                ProjectMedia.sort_order.asc(),
                ProjectMedia.created_at.asc(),
                ProjectMedia.id.asc(),
            )
        )

        result = await session.execute(statement)

        return result.scalars().all()

    async def list_for_admin(
        self,
        session: AsyncSession,
        *,
        project_id: UUID,
        offset: int,
        limit: int,
        search: str | None = None,
        media_type: str | None = None,
        is_primary: bool | None = None,
        include_deleted: bool = False,
        sort_by: str = "sort_order",
        sort_direction: str = "asc",
    ) -> tuple[Sequence[ProjectMedia], int]:
        """
        Return paginated media records for one project.

        The returned tuple contains the matching records and the total
        number of matching rows before pagination.
        """

        filters: list[ColumnElement[bool]] = [
            ProjectMedia.project_id == project_id,
        ]

        if not include_deleted:
            filters.append(
                ProjectMedia.deleted_at.is_(None),
            )

        normalized_search = search.strip() if search and search.strip() else None

        if normalized_search:
            search_pattern = f"%{normalized_search}%"

            filters.append(
                or_(
                    ProjectMedia.url.ilike(
                        search_pattern,
                    ),
                    ProjectMedia.thumbnail_url.ilike(
                        search_pattern,
                    ),
                    ProjectMedia.alt_text.ilike(
                        search_pattern,
                    ),
                    ProjectMedia.caption.ilike(
                        search_pattern,
                    ),
                    ProjectMedia.provider.ilike(
                        search_pattern,
                    ),
                    ProjectMedia.provider_asset_id.ilike(
                        search_pattern,
                    ),
                    ProjectMedia.mime_type.ilike(
                        search_pattern,
                    ),
                )
            )

        normalized_media_type = (
            media_type.strip().lower() if media_type and media_type.strip() else None
        )

        if normalized_media_type:
            filters.append(
                ProjectMedia.media_type == normalized_media_type,
            )

        if is_primary is not None:
            filters.append(
                ProjectMedia.is_primary.is_(is_primary),
            )

        sort_columns = {
            "media_type": ProjectMedia.media_type,
            "is_primary": ProjectMedia.is_primary,
            "sort_order": ProjectMedia.sort_order,
            "created_at": ProjectMedia.created_at,
            "updated_at": ProjectMedia.updated_at,
        }

        sort_column = sort_columns.get(
            sort_by,
            ProjectMedia.sort_order,
        )

        normalized_direction = sort_direction.strip().lower()

        sort_expression = (
            asc(sort_column) if normalized_direction == "asc" else desc(sort_column)
        )

        count_statement = select(
            func.count(ProjectMedia.id),
        ).where(*filters)

        total_result = await session.execute(
            count_statement,
        )

        total = int(
            total_result.scalar_one(),
        )

        statement = (
            select(ProjectMedia)
            .where(*filters)
            .order_by(
                sort_expression,
                ProjectMedia.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(statement)

        media_records = result.scalars().all()

        return media_records, total

    async def count_for_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        media_type: str | None = None,
        include_deleted: bool = False,
    ) -> int:
        """
        Count media records belonging to a project.

        Records can optionally be filtered by media type.
        """

        conditions: list[ColumnElement[bool]] = [
            ProjectMedia.project_id == project_id,
        ]

        if not include_deleted:
            conditions.append(
                ProjectMedia.deleted_at.is_(None),
            )

        normalized_media_type = (
            media_type.strip().lower() if media_type and media_type.strip() else None
        )

        if normalized_media_type:
            conditions.append(
                ProjectMedia.media_type == normalized_media_type,
            )

        statement = select(
            func.count(ProjectMedia.id),
        ).where(*conditions)

        result = await session.execute(statement)

        return int(result.scalar_one())

    async def has_primary(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        exclude_media_id: UUID | None = None,
    ) -> bool:
        """
        Check whether a project already has active primary media.

        A media UUID can be excluded while validating updates to an
        existing record.
        """

        conditions: list[ColumnElement[bool]] = [
            ProjectMedia.project_id == project_id,
            ProjectMedia.is_primary.is_(True),
            ProjectMedia.deleted_at.is_(None),
        ]

        if exclude_media_id is not None:
            conditions.append(
                ProjectMedia.id != exclude_media_id,
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())

    async def url_exists(
        self,
        session: AsyncSession,
        project_id: UUID,
        url: str,
        *,
        exclude_media_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether a media URL already exists for a project.

        A media UUID can be excluded while validating an update.
        """

        normalized_url = url.strip()

        conditions: list[ColumnElement[bool]] = [
            ProjectMedia.project_id == project_id,
            ProjectMedia.url == normalized_url,
        ]

        if exclude_media_id is not None:
            conditions.append(
                ProjectMedia.id != exclude_media_id,
            )

        if not include_deleted:
            conditions.append(
                ProjectMedia.deleted_at.is_(None),
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())

    async def provider_asset_exists(
        self,
        session: AsyncSession,
        provider: str,
        provider_asset_id: str,
        *,
        exclude_media_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether a provider asset is already registered.

        Provider and provider-asset identifiers are normalized before
        comparison.
        """

        normalized_provider = provider.strip()
        normalized_asset_id = provider_asset_id.strip()

        conditions: list[ColumnElement[bool]] = [
            ProjectMedia.provider == normalized_provider,
            ProjectMedia.provider_asset_id == normalized_asset_id,
        ]

        if exclude_media_id is not None:
            conditions.append(
                ProjectMedia.id != exclude_media_id,
            )

        if not include_deleted:
            conditions.append(
                ProjectMedia.deleted_at.is_(None),
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())


project_media_repository = ProjectMediaRepository()
