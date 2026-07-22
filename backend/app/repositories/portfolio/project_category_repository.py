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

from app.models.project import Project
from app.models.project_category import ProjectCategory
from app.repositories.base import BaseRepository


class ProjectCategoryRepository(
    BaseRepository[ProjectCategory],
):
    """Database operations for portfolio project categories."""

    def __init__(self) -> None:
        super().__init__(ProjectCategory)

    async def get_by_id(
        self,
        session: AsyncSession,
        category_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ProjectCategory | None:
        """
        Return a project category by UUID.

        Soft-deleted records are excluded unless
        ``include_deleted`` is enabled.
        """

        statement = select(ProjectCategory).where(
            ProjectCategory.id == category_id,
        )

        if not include_deleted:
            statement = statement.where(
                ProjectCategory.deleted_at.is_(None),
            )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        session: AsyncSession,
        slug: str,
        *,
        include_deleted: bool = False,
    ) -> ProjectCategory | None:
        """
        Return a project category by its normalized slug.

        Soft-deleted records are excluded unless
        ``include_deleted`` is enabled.
        """

        normalized_slug = slug.strip().lower()

        statement = select(ProjectCategory).where(
            ProjectCategory.slug == normalized_slug,
        )

        if not include_deleted:
            statement = statement.where(
                ProjectCategory.deleted_at.is_(None),
            )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def list_public(
        self,
        session: AsyncSession,
    ) -> Sequence[ProjectCategory]:
        """
        Return all active, non-deleted categories for public use.

        Categories are ordered deterministically by their configured
        sort order, name, and UUID.
        """

        statement = (
            select(ProjectCategory)
            .where(
                ProjectCategory.is_active.is_(True),
                ProjectCategory.deleted_at.is_(None),
            )
            .order_by(
                ProjectCategory.sort_order.asc(),
                ProjectCategory.name.asc(),
                ProjectCategory.id.asc(),
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
        is_active: bool | None = None,
        include_deleted: bool = False,
        sort_by: str = "sort_order",
        sort_direction: str = "asc",
    ) -> tuple[Sequence[ProjectCategory], int]:
        """
        Return paginated project categories for administrative use.

        The returned tuple contains the selected records and the total
        number of records matching the supplied filters.
        """

        filters: list[ColumnElement[bool]] = []

        if not include_deleted:
            filters.append(
                ProjectCategory.deleted_at.is_(None),
            )

        normalized_search = search.strip() if search else None

        if normalized_search:
            search_pattern = f"%{normalized_search}%"

            filters.append(
                or_(
                    ProjectCategory.name.ilike(
                        search_pattern,
                    ),
                    ProjectCategory.slug.ilike(
                        search_pattern,
                    ),
                    ProjectCategory.description.ilike(
                        search_pattern,
                    ),
                    ProjectCategory.seo_title.ilike(
                        search_pattern,
                    ),
                    ProjectCategory.seo_description.ilike(
                        search_pattern,
                    ),
                )
            )

        if is_active is not None:
            filters.append(
                ProjectCategory.is_active.is_(is_active),
            )

        sort_columns = {
            "name": ProjectCategory.name,
            "slug": ProjectCategory.slug,
            "sort_order": ProjectCategory.sort_order,
            "created_at": ProjectCategory.created_at,
            "updated_at": ProjectCategory.updated_at,
        }

        sort_column = sort_columns.get(
            sort_by,
            ProjectCategory.sort_order,
        )

        normalized_direction = sort_direction.strip().lower()

        sort_expression = (
            asc(sort_column) if normalized_direction == "asc" else desc(sort_column)
        )

        count_statement = select(
            func.count(ProjectCategory.id),
        ).where(*filters)

        total_result = await session.execute(
            count_statement,
        )

        total = int(
            total_result.scalar_one(),
        )

        statement = (
            select(ProjectCategory)
            .where(*filters)
            .order_by(
                sort_expression,
                ProjectCategory.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(statement)

        categories = result.scalars().all()

        return categories, total

    async def name_exists(
        self,
        session: AsyncSession,
        name: str,
        *,
        exclude_category_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether a category name is already in use.

        The comparison is case-insensitive. A category UUID can be
        excluded when validating an update to an existing record.
        """

        normalized_name = " ".join(name.split())

        conditions: list[ColumnElement[bool]] = [
            func.lower(ProjectCategory.name) == normalized_name.lower(),
        ]

        if exclude_category_id is not None:
            conditions.append(
                ProjectCategory.id != exclude_category_id,
            )

        if not include_deleted:
            conditions.append(
                ProjectCategory.deleted_at.is_(None),
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
        exclude_category_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether a normalized category slug is already in use.

        A category UUID can be excluded when validating an update to
        an existing category.
        """

        normalized_slug = slug.strip().lower()

        conditions: list[ColumnElement[bool]] = [
            ProjectCategory.slug == normalized_slug,
        ]

        if exclude_category_id is not None:
            conditions.append(
                ProjectCategory.id != exclude_category_id,
            )

        if not include_deleted:
            conditions.append(
                ProjectCategory.deleted_at.is_(None),
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())

    async def has_projects(
        self,
        session: AsyncSession,
        category_id: UUID,
        *,
        include_deleted_projects: bool = False,
    ) -> bool:
        """
        Check whether any project is assigned to the category.

        Soft-deleted projects are ignored unless explicitly included.
        """

        conditions: list[ColumnElement[bool]] = [
            Project.category_id == category_id,
        ]

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
        category_id: UUID,
        *,
        include_deleted_projects: bool = False,
    ) -> int:
        """
        Count projects assigned to a category.

        Soft-deleted projects are ignored unless explicitly included.
        """

        conditions: list[ColumnElement[bool]] = [
            Project.category_id == category_id,
        ]

        if not include_deleted_projects:
            conditions.append(
                Project.deleted_at.is_(None),
            )

        statement = select(
            func.count(Project.id),
        ).where(*conditions)

        result = await session.execute(statement)

        return int(result.scalar_one())


project_category_repository = ProjectCategoryRepository()
