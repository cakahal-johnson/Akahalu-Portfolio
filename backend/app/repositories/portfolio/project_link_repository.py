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

from app.models.project_link import ProjectLink
from app.repositories.base import BaseRepository


class ProjectLinkRepository(
    BaseRepository[ProjectLink],
):
    """Database operations for portfolio project links."""

    def __init__(self) -> None:
        super().__init__(ProjectLink)

    async def get_by_id(
        self,
        session: AsyncSession,
        link_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ProjectLink | None:
        """
        Return a project link by UUID.

        Soft-deleted links are excluded unless
        ``include_deleted`` is enabled.
        """

        statement = select(ProjectLink).where(
            ProjectLink.id == link_id,
        )

        if not include_deleted:
            statement = statement.where(
                ProjectLink.deleted_at.is_(None),
            )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def list_public_for_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        link_type: str | None = None,
    ) -> Sequence[ProjectLink]:
        """
        Return active public links belonging to a project.

        Results are ordered by configured sort order, creation time,
        and UUID.
        """

        filters: list[ColumnElement[bool]] = [
            ProjectLink.project_id == project_id,
            ProjectLink.is_active.is_(True),
            ProjectLink.deleted_at.is_(None),
        ]

        normalized_link_type = (
            link_type.strip().lower() if link_type and link_type.strip() else None
        )

        if normalized_link_type:
            filters.append(
                ProjectLink.link_type == normalized_link_type,
            )

        statement = (
            select(ProjectLink)
            .where(*filters)
            .order_by(
                ProjectLink.sort_order.asc(),
                ProjectLink.created_at.asc(),
                ProjectLink.id.asc(),
            )
        )

        result = await session.execute(statement)

        return result.scalars().all()

    async def list_for_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        include_inactive: bool = True,
        include_deleted: bool = False,
        link_type: str | None = None,
    ) -> Sequence[ProjectLink]:
        """
        Return project links for administrative project editing.

        Inactive and soft-deleted records can be included separately.
        """

        filters: list[ColumnElement[bool]] = [
            ProjectLink.project_id == project_id,
        ]

        if not include_inactive:
            filters.append(
                ProjectLink.is_active.is_(True),
            )

        if not include_deleted:
            filters.append(
                ProjectLink.deleted_at.is_(None),
            )

        normalized_link_type = (
            link_type.strip().lower() if link_type and link_type.strip() else None
        )

        if normalized_link_type:
            filters.append(
                ProjectLink.link_type == normalized_link_type,
            )

        statement = (
            select(ProjectLink)
            .where(*filters)
            .order_by(
                ProjectLink.sort_order.asc(),
                ProjectLink.created_at.asc(),
                ProjectLink.id.asc(),
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
        link_type: str | None = None,
        is_active: bool | None = None,
        opens_in_new_tab: bool | None = None,
        include_deleted: bool = False,
        sort_by: str = "sort_order",
        sort_direction: str = "asc",
    ) -> tuple[Sequence[ProjectLink], int]:
        """
        Return paginated project links for administrative use.

        The returned tuple contains the matching rows and the total
        count before pagination.
        """

        filters: list[ColumnElement[bool]] = [
            ProjectLink.project_id == project_id,
        ]

        if not include_deleted:
            filters.append(
                ProjectLink.deleted_at.is_(None),
            )

        normalized_search = search.strip() if search and search.strip() else None

        if normalized_search:
            search_pattern = f"%{normalized_search}%"

            filters.append(
                or_(
                    ProjectLink.label.ilike(
                        search_pattern,
                    ),
                    ProjectLink.url.ilike(
                        search_pattern,
                    ),
                    ProjectLink.link_type.ilike(
                        search_pattern,
                    ),
                    ProjectLink.icon.ilike(
                        search_pattern,
                    ),
                )
            )

        normalized_link_type = (
            link_type.strip().lower() if link_type and link_type.strip() else None
        )

        if normalized_link_type:
            filters.append(
                ProjectLink.link_type == normalized_link_type,
            )

        if is_active is not None:
            filters.append(
                ProjectLink.is_active.is_(is_active),
            )

        if opens_in_new_tab is not None:
            filters.append(
                ProjectLink.opens_in_new_tab.is_(
                    opens_in_new_tab,
                ),
            )

        sort_columns = {
            "label": ProjectLink.label,
            "link_type": ProjectLink.link_type,
            "is_active": ProjectLink.is_active,
            "opens_in_new_tab": ProjectLink.opens_in_new_tab,
            "sort_order": ProjectLink.sort_order,
            "created_at": ProjectLink.created_at,
            "updated_at": ProjectLink.updated_at,
        }

        sort_column = sort_columns.get(
            sort_by,
            ProjectLink.sort_order,
        )

        normalized_direction = sort_direction.strip().lower()

        sort_expression = (
            asc(sort_column) if normalized_direction == "asc" else desc(sort_column)
        )

        count_statement = select(
            func.count(ProjectLink.id),
        ).where(*filters)

        total_result = await session.execute(
            count_statement,
        )

        total = int(
            total_result.scalar_one(),
        )

        statement = (
            select(ProjectLink)
            .where(*filters)
            .order_by(
                sort_expression,
                ProjectLink.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(statement)

        links = result.scalars().all()

        return links, total

    async def count_for_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        link_type: str | None = None,
        is_active: bool | None = None,
        include_deleted: bool = False,
    ) -> int:
        """
        Count links belonging to a project.

        Records can optionally be filtered by link type and activity
        status.
        """

        conditions: list[ColumnElement[bool]] = [
            ProjectLink.project_id == project_id,
        ]

        if not include_deleted:
            conditions.append(
                ProjectLink.deleted_at.is_(None),
            )

        normalized_link_type = (
            link_type.strip().lower() if link_type and link_type.strip() else None
        )

        if normalized_link_type:
            conditions.append(
                ProjectLink.link_type == normalized_link_type,
            )

        if is_active is not None:
            conditions.append(
                ProjectLink.is_active.is_(is_active),
            )

        statement = select(
            func.count(ProjectLink.id),
        ).where(*conditions)

        result = await session.execute(statement)

        return int(result.scalar_one())

    async def url_exists(
        self,
        session: AsyncSession,
        project_id: UUID,
        url: str,
        *,
        exclude_link_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether a URL already exists for a project.

        The database enforces uniqueness for active project-and-URL
        pairs. A link UUID can be excluded while validating updates.
        """

        normalized_url = url.strip()

        conditions: list[ColumnElement[bool]] = [
            ProjectLink.project_id == project_id,
            ProjectLink.url == normalized_url,
        ]

        if exclude_link_id is not None:
            conditions.append(
                ProjectLink.id != exclude_link_id,
            )

        if not include_deleted:
            conditions.append(
                ProjectLink.deleted_at.is_(None),
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())

    async def label_exists(
        self,
        session: AsyncSession,
        project_id: UUID,
        label: str,
        *,
        exclude_link_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether a link label already exists for a project.

        The comparison is case-insensitive. This is a service-level
        usability check rather than a database uniqueness rule.
        """

        normalized_label = " ".join(label.split())

        conditions: list[ColumnElement[bool]] = [
            ProjectLink.project_id == project_id,
            func.lower(ProjectLink.label) == normalized_label.lower(),
        ]

        if exclude_link_id is not None:
            conditions.append(
                ProjectLink.id != exclude_link_id,
            )

        if not include_deleted:
            conditions.append(
                ProjectLink.deleted_at.is_(None),
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())


project_link_repository = ProjectLinkRepository()
