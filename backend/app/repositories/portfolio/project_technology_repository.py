from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import (
    asc,
    desc,
    distinct,
    exists,
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.models.project import Project
from app.models.project_associations import (
    ProjectTechnologyAssociation,
)
from app.models.project_technology import ProjectTechnology
from app.repositories.base import BaseRepository


class ProjectTechnologyRepository(
    BaseRepository[ProjectTechnology],
):
    """Database operations for portfolio project technologies."""

    def __init__(self) -> None:
        super().__init__(ProjectTechnology)

    async def get_by_id(
        self,
        session: AsyncSession,
        technology_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ProjectTechnology | None:
        """
        Return a project technology by UUID.

        Soft-deleted technologies are excluded unless
        ``include_deleted`` is enabled.
        """

        statement = select(ProjectTechnology).where(
            ProjectTechnology.id == technology_id,
        )

        if not include_deleted:
            statement = statement.where(
                ProjectTechnology.deleted_at.is_(None),
            )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        session: AsyncSession,
        slug: str,
        *,
        include_deleted: bool = False,
    ) -> ProjectTechnology | None:
        """
        Return a project technology by its normalized slug.

        Soft-deleted technologies are excluded unless
        ``include_deleted`` is enabled.
        """

        normalized_slug = slug.strip().lower()

        statement = select(ProjectTechnology).where(
            ProjectTechnology.slug == normalized_slug,
        )

        if not include_deleted:
            statement = statement.where(
                ProjectTechnology.deleted_at.is_(None),
            )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def list_public(
        self,
        session: AsyncSession,
        *,
        category: str | None = None,
    ) -> Sequence[ProjectTechnology]:
        """
        Return active, non-deleted technologies for public use.

        An optional normalized category filter can be supplied.
        Results are ordered by category, configured sort order,
        name, and UUID.
        """

        filters: list[ColumnElement[bool]] = [
            ProjectTechnology.is_active.is_(True),
            ProjectTechnology.deleted_at.is_(None),
        ]

        normalized_category = (
            category.strip().lower() if category and category.strip() else None
        )

        if normalized_category:
            filters.append(
                ProjectTechnology.category == normalized_category,
            )

        statement = (
            select(ProjectTechnology)
            .where(*filters)
            .order_by(
                ProjectTechnology.category.asc(),
                ProjectTechnology.sort_order.asc(),
                ProjectTechnology.name.asc(),
                ProjectTechnology.id.asc(),
            )
        )

        result = await session.execute(statement)

        return result.scalars().all()

    async def list_for_admin(
        self,
        session: AsyncSession,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        category: str | None = None,
        is_active: bool | None = None,
        include_deleted: bool = False,
        sort_by: str = "sort_order",
        sort_direction: str = "asc",
    ) -> tuple[Sequence[ProjectTechnology], int]:
        """
        Return paginated technologies for administrative use.

        The returned tuple contains the matching technology records
        and the total number of records before pagination.
        """

        filters: list[ColumnElement[bool]] = []

        if not include_deleted:
            filters.append(
                ProjectTechnology.deleted_at.is_(None),
            )

        normalized_search = search.strip() if search and search.strip() else None

        if normalized_search:
            search_pattern = f"%{normalized_search}%"

            filters.append(
                or_(
                    ProjectTechnology.name.ilike(
                        search_pattern,
                    ),
                    ProjectTechnology.slug.ilike(
                        search_pattern,
                    ),
                    ProjectTechnology.description.ilike(
                        search_pattern,
                    ),
                    ProjectTechnology.category.ilike(
                        search_pattern,
                    ),
                )
            )

        normalized_category = (
            category.strip().lower() if category and category.strip() else None
        )

        if normalized_category:
            filters.append(
                ProjectTechnology.category == normalized_category,
            )

        if is_active is not None:
            filters.append(
                ProjectTechnology.is_active.is_(is_active),
            )

        sort_columns = {
            "name": ProjectTechnology.name,
            "slug": ProjectTechnology.slug,
            "category": ProjectTechnology.category,
            "sort_order": ProjectTechnology.sort_order,
            "created_at": ProjectTechnology.created_at,
            "updated_at": ProjectTechnology.updated_at,
        }

        sort_column = sort_columns.get(
            sort_by,
            ProjectTechnology.sort_order,
        )

        normalized_direction = sort_direction.strip().lower()

        sort_expression = (
            asc(sort_column) if normalized_direction == "asc" else desc(sort_column)
        )

        count_statement = select(
            func.count(ProjectTechnology.id),
        ).where(*filters)

        total_result = await session.execute(
            count_statement,
        )

        total = int(
            total_result.scalar_one(),
        )

        statement = (
            select(ProjectTechnology)
            .where(*filters)
            .order_by(
                sort_expression,
                ProjectTechnology.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(statement)

        technologies = result.scalars().all()

        return technologies, total

    async def name_exists(
        self,
        session: AsyncSession,
        name: str,
        *,
        exclude_technology_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether a technology name is already in use.

        The comparison is case-insensitive. A technology UUID can be
        excluded when validating an update.
        """

        normalized_name = " ".join(name.split())

        conditions: list[ColumnElement[bool]] = [
            func.lower(ProjectTechnology.name) == normalized_name.lower(),
        ]

        if exclude_technology_id is not None:
            conditions.append(
                ProjectTechnology.id != exclude_technology_id,
            )

        if not include_deleted:
            conditions.append(
                ProjectTechnology.deleted_at.is_(None),
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())

    async def slug_exists(
        self,
        session: AsyncSession,
        slug: str,
        *,
        exclude_technology_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether a normalized technology slug is already in use.

        A technology UUID can be excluded when validating an update.
        """

        normalized_slug = slug.strip().lower()

        conditions: list[ColumnElement[bool]] = [
            ProjectTechnology.slug == normalized_slug,
        ]

        if exclude_technology_id is not None:
            conditions.append(
                ProjectTechnology.id != exclude_technology_id,
            )

        if not include_deleted:
            conditions.append(
                ProjectTechnology.deleted_at.is_(None),
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())

    async def has_projects(
        self,
        session: AsyncSession,
        technology_id: UUID,
        *,
        include_deleted_associations: bool = False,
        include_deleted_projects: bool = False,
    ) -> bool:
        """
        Check whether the technology is assigned to any project.

        Soft-deleted associations and projects are ignored unless
        explicitly included.
        """

        conditions: list[ColumnElement[bool]] = [
            ProjectTechnologyAssociation.technology_id == technology_id,
            ProjectTechnologyAssociation.project_id == Project.id,
        ]

        if not include_deleted_associations:
            conditions.append(
                ProjectTechnologyAssociation.deleted_at.is_(None),
            )

        if not include_deleted_projects:
            conditions.append(
                Project.deleted_at.is_(None),
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())

    async def count_projects(
        self,
        session: AsyncSession,
        technology_id: UUID,
        *,
        include_deleted_associations: bool = False,
        include_deleted_projects: bool = False,
    ) -> int:
        """
        Count distinct projects assigned to a technology.

        Soft-deleted associations and projects are ignored unless
        explicitly included.
        """

        conditions: list[ColumnElement[bool]] = [
            ProjectTechnologyAssociation.technology_id == technology_id,
            ProjectTechnologyAssociation.project_id == Project.id,
        ]

        if not include_deleted_associations:
            conditions.append(
                ProjectTechnologyAssociation.deleted_at.is_(None),
            )

        if not include_deleted_projects:
            conditions.append(
                Project.deleted_at.is_(None),
            )

        statement = select(
            func.count(
                distinct(Project.id),
            ),
        ).where(*conditions)

        result = await session.execute(statement)

        return int(result.scalar_one())

    async def has_active_association(
        self,
        session: AsyncSession,
        technology_id: UUID,
        project_id: UUID,
    ) -> bool:
        """
        Check whether an active project-technology association exists.

        This supports duplicate prevention before assigning a
        technology to a project.
        """

        statement = select(
            exists().where(
                ProjectTechnologyAssociation.technology_id == technology_id,
                ProjectTechnologyAssociation.project_id == project_id,
                ProjectTechnologyAssociation.deleted_at.is_(None),
            ),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())


project_technology_repository = ProjectTechnologyRepository()
