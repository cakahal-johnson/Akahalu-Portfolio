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
from sqlalchemy.orm import (
    selectinload,
    with_loader_criteria,
)
from sqlalchemy.sql.elements import ColumnElement

from app.models.project import Project
from app.models.project_associations import (
    ProjectTechnologyAssociation,
)
from app.models.project_category import ProjectCategory
from app.models.project_link import ProjectLink
from app.models.project_media import ProjectMedia
from app.models.project_technology import ProjectTechnology
from app.repositories.base import BaseRepository


class ProjectRepository(
    BaseRepository[Project],
):
    """Database operations for portfolio projects."""

    def __init__(self) -> None:
        super().__init__(Project)

    async def get_by_id(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        include_deleted: bool = False,
        include_related: bool = True,
    ) -> Project | None:
        """
        Return a project by UUID.

        Related media, links, and technologies are loaded when
        ``include_related`` is enabled.
        """

        statement = select(Project).where(
            Project.id == project_id,
        )

        if not include_deleted:
            statement = statement.where(
                Project.deleted_at.is_(None),
            )

        if include_related:
            statement = statement.options(
                selectinload(Project.media),
                selectinload(Project.links),
                selectinload(
                    Project.technology_associations,
                ).selectinload(
                    ProjectTechnologyAssociation.technology,
                ),
            )

        result = await session.execute(statement)

        return result.unique().scalar_one_or_none()

    async def get_by_slug(
        self,
        session: AsyncSession,
        slug: str,
        *,
        include_deleted: bool = False,
        include_related: bool = True,
    ) -> Project | None:
        """
        Return a project by normalized slug.

        This method does not enforce public publication rules and is
        suitable for administrative use.
        """

        normalized_slug = slug.strip().lower()

        statement = select(Project).where(
            Project.slug == normalized_slug,
        )

        if not include_deleted:
            statement = statement.where(
                Project.deleted_at.is_(None),
            )

        if include_related:
            statement = statement.options(
                selectinload(Project.media),
                selectinload(Project.links),
                selectinload(
                    Project.technology_associations,
                ).selectinload(
                    ProjectTechnologyAssociation.technology,
                ),
            )

        result = await session.execute(statement)

        return result.unique().scalar_one_or_none()

    async def get_public_by_slug(
        self,
        session: AsyncSession,
        slug: str,
    ) -> Project | None:
        """
        Return a publicly available project by normalized slug.

        Public projects must be published, publicly visible,
        timestamped, and not soft-deleted.

        Only active, non-deleted related links and technologies are
        included. Soft-deleted media and associations are excluded.
        """

        normalized_slug = slug.strip().lower()

        statement = (
            select(Project)
            .where(
                Project.slug == normalized_slug,
                Project.status == "published",
                Project.visibility == "public",
                Project.published_at.is_not(None),
                Project.deleted_at.is_(None),
            )
            .options(
                selectinload(Project.media),
                selectinload(Project.links),
                selectinload(
                    Project.technology_associations,
                ).selectinload(
                    ProjectTechnologyAssociation.technology,
                ),
                with_loader_criteria(
                    ProjectMedia,
                    ProjectMedia.deleted_at.is_(None),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectLink,
                    ProjectLink.is_active.is_(True),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectLink,
                    ProjectLink.deleted_at.is_(None),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectTechnologyAssociation,
                    ProjectTechnologyAssociation.deleted_at.is_(None),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectTechnology,
                    ProjectTechnology.is_active.is_(True),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectTechnology,
                    ProjectTechnology.deleted_at.is_(None),
                    include_aliases=True,
                ),
            )
        )

        result = await session.execute(statement)

        return result.unique().scalar_one_or_none()

    async def list_public(
        self,
        session: AsyncSession,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        category_id: UUID | None = None,
        category_slug: str | None = None,
        technology_id: UUID | None = None,
        technology_slug: str | None = None,
        is_featured: bool | None = None,
    ) -> tuple[Sequence[Project], int]:
        """
        Return paginated publicly available projects.

        Projects can be filtered by category, technology, featured
        status, or search text.
        """

        filters: list[ColumnElement[bool]] = [
            Project.status == "published",
            Project.visibility == "public",
            Project.published_at.is_not(None),
            Project.deleted_at.is_(None),
        ]

        normalized_search = search.strip() if search and search.strip() else None

        if normalized_search:
            search_pattern = f"%{normalized_search}%"

            filters.append(
                or_(
                    Project.title.ilike(
                        search_pattern,
                    ),
                    Project.slug.ilike(
                        search_pattern,
                    ),
                    Project.short_description.ilike(
                        search_pattern,
                    ),
                    Project.description.ilike(
                        search_pattern,
                    ),
                    Project.problem_statement.ilike(
                        search_pattern,
                    ),
                    Project.solution_summary.ilike(
                        search_pattern,
                    ),
                    Project.key_features.ilike(
                        search_pattern,
                    ),
                    Project.technical_highlights.ilike(
                        search_pattern,
                    ),
                )
            )

        if category_id is not None:
            filters.append(
                Project.category_id == category_id,
            )

        normalized_category_slug = (
            category_slug.strip().lower()
            if category_slug and category_slug.strip()
            else None
        )

        if normalized_category_slug:
            filters.append(
                exists().where(
                    ProjectCategory.id == Project.category_id,
                    ProjectCategory.slug == normalized_category_slug,
                    ProjectCategory.is_active.is_(True),
                    ProjectCategory.deleted_at.is_(None),
                )
            )

        if is_featured is not None:
            filters.append(
                Project.is_featured.is_(is_featured),
            )

        if technology_id is not None:
            filters.append(
                exists().where(
                    ProjectTechnologyAssociation.project_id == Project.id,
                    ProjectTechnologyAssociation.technology_id == technology_id,
                    ProjectTechnologyAssociation.deleted_at.is_(None),
                )
            )

        normalized_technology_slug = (
            technology_slug.strip().lower()
            if technology_slug and technology_slug.strip()
            else None
        )

        if normalized_technology_slug:
            filters.append(
                exists().where(
                    ProjectTechnologyAssociation.project_id == Project.id,
                    ProjectTechnologyAssociation.technology_id == ProjectTechnology.id,
                    ProjectTechnologyAssociation.deleted_at.is_(None),
                    ProjectTechnology.slug == normalized_technology_slug,
                    ProjectTechnology.is_active.is_(True),
                    ProjectTechnology.deleted_at.is_(None),
                )
            )

        count_statement = select(
            func.count(
                distinct(Project.id),
            ),
        ).where(*filters)

        total_result = await session.execute(
            count_statement,
        )

        total = int(
            total_result.scalar_one(),
        )

        statement = (
            select(Project)
            .where(*filters)
            .options(
                selectinload(Project.media),
                selectinload(Project.links),
                selectinload(
                    Project.technology_associations,
                ).selectinload(
                    ProjectTechnologyAssociation.technology,
                ),
                with_loader_criteria(
                    ProjectMedia,
                    ProjectMedia.deleted_at.is_(None),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectLink,
                    ProjectLink.is_active.is_(True),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectLink,
                    ProjectLink.deleted_at.is_(None),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectTechnologyAssociation,
                    ProjectTechnologyAssociation.deleted_at.is_(None),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectTechnology,
                    ProjectTechnology.is_active.is_(True),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectTechnology,
                    ProjectTechnology.deleted_at.is_(None),
                    include_aliases=True,
                ),
            )
            .order_by(
                Project.is_featured.desc(),
                Project.sort_order.asc(),
                Project.published_at.desc(),
                Project.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(statement)

        projects = result.unique().scalars().all()

        return projects, total

    async def list_featured(
        self,
        session: AsyncSession,
        *,
        limit: int,
    ) -> Sequence[Project]:
        """
        Return featured publicly available projects.

        Results follow configured display order and publication date.
        """

        statement = (
            select(Project)
            .where(
                Project.status == "published",
                Project.visibility == "public",
                Project.published_at.is_not(None),
                Project.is_featured.is_(True),
                Project.deleted_at.is_(None),
            )
            .options(
                selectinload(Project.media),
                selectinload(Project.links),
                selectinload(
                    Project.technology_associations,
                ).selectinload(
                    ProjectTechnologyAssociation.technology,
                ),
                with_loader_criteria(
                    ProjectMedia,
                    ProjectMedia.deleted_at.is_(None),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectLink,
                    ProjectLink.is_active.is_(True),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectLink,
                    ProjectLink.deleted_at.is_(None),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectTechnologyAssociation,
                    ProjectTechnologyAssociation.deleted_at.is_(None),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectTechnology,
                    ProjectTechnology.is_active.is_(True),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    ProjectTechnology,
                    ProjectTechnology.deleted_at.is_(None),
                    include_aliases=True,
                ),
            )
            .order_by(
                Project.sort_order.asc(),
                Project.published_at.desc(),
                Project.id.asc(),
            )
            .limit(limit)
        )

        result = await session.execute(statement)

        return result.unique().scalars().all()

    async def list_for_admin(
        self,
        session: AsyncSession,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        category_id: UUID | None = None,
        status: str | None = None,
        visibility: str | None = None,
        is_featured: bool | None = None,
        technology_id: UUID | None = None,
        include_deleted: bool = False,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> tuple[Sequence[Project], int]:
        """
        Return paginated projects for administrative management.

        Administrative listings can filter by project state,
        visibility, category, technology, and featured status.
        """

        filters: list[ColumnElement[bool]] = []

        if not include_deleted:
            filters.append(
                Project.deleted_at.is_(None),
            )

        normalized_search = search.strip() if search and search.strip() else None

        if normalized_search:
            search_pattern = f"%{normalized_search}%"

            filters.append(
                or_(
                    Project.title.ilike(
                        search_pattern,
                    ),
                    Project.slug.ilike(
                        search_pattern,
                    ),
                    Project.short_description.ilike(
                        search_pattern,
                    ),
                    Project.description.ilike(
                        search_pattern,
                    ),
                    Project.problem_statement.ilike(
                        search_pattern,
                    ),
                    Project.solution_summary.ilike(
                        search_pattern,
                    ),
                )
            )

        if category_id is not None:
            filters.append(
                Project.category_id == category_id,
            )

        normalized_status = (
            status.strip().lower() if status and status.strip() else None
        )

        if normalized_status:
            filters.append(
                Project.status == normalized_status,
            )

        normalized_visibility = (
            visibility.strip().lower() if visibility and visibility.strip() else None
        )

        if normalized_visibility:
            filters.append(
                Project.visibility == normalized_visibility,
            )

        if is_featured is not None:
            filters.append(
                Project.is_featured.is_(is_featured),
            )

        if technology_id is not None:
            filters.append(
                exists().where(
                    ProjectTechnologyAssociation.project_id == Project.id,
                    ProjectTechnologyAssociation.technology_id == technology_id,
                    ProjectTechnologyAssociation.deleted_at.is_(None),
                )
            )

        sort_columns = {
            "title": Project.title,
            "slug": Project.slug,
            "status": Project.status,
            "visibility": Project.visibility,
            "is_featured": Project.is_featured,
            "sort_order": Project.sort_order,
            "started_at": Project.started_at,
            "completed_at": Project.completed_at,
            "published_at": Project.published_at,
            "created_at": Project.created_at,
            "updated_at": Project.updated_at,
        }

        sort_column = sort_columns.get(
            sort_by,
            Project.created_at,
        )

        normalized_direction = sort_direction.strip().lower()

        sort_expression = (
            asc(sort_column) if normalized_direction == "asc" else desc(sort_column)
        )

        count_statement = select(
            func.count(
                distinct(Project.id),
            ),
        ).where(*filters)

        total_result = await session.execute(
            count_statement,
        )

        total = int(
            total_result.scalar_one(),
        )

        statement = (
            select(Project)
            .where(*filters)
            .options(
                selectinload(Project.media),
                selectinload(Project.links),
                selectinload(
                    Project.technology_associations,
                ).selectinload(
                    ProjectTechnologyAssociation.technology,
                ),
            )
            .order_by(
                sort_expression,
                Project.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(statement)

        projects = result.unique().scalars().all()

        return projects, total

    async def slug_exists(
        self,
        session: AsyncSession,
        slug: str,
        *,
        exclude_project_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether a normalized project slug is already in use.

        A project UUID can be excluded when validating an update.
        """

        normalized_slug = slug.strip().lower()

        conditions: list[ColumnElement[bool]] = [
            Project.slug == normalized_slug,
        ]

        if exclude_project_id is not None:
            conditions.append(
                Project.id != exclude_project_id,
            )

        if not include_deleted:
            conditions.append(
                Project.deleted_at.is_(None),
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())

    async def count_public(
        self,
        session: AsyncSession,
        *,
        category_id: UUID | None = None,
        is_featured: bool | None = None,
    ) -> int:
        """
        Count publicly available projects.

        The count can optionally be filtered by category and featured
        status.
        """

        conditions: list[ColumnElement[bool]] = [
            Project.status == "published",
            Project.visibility == "public",
            Project.published_at.is_not(None),
            Project.deleted_at.is_(None),
        ]

        if category_id is not None:
            conditions.append(
                Project.category_id == category_id,
            )

        if is_featured is not None:
            conditions.append(
                Project.is_featured.is_(is_featured),
            )

        statement = select(
            func.count(Project.id),
        ).where(*conditions)

        result = await session.execute(statement)

        return int(result.scalar_one())

    async def has_category_projects(
        self,
        session: AsyncSession,
        category_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether a category is assigned to any project.

        This supports category deletion and reassignment validation.
        """

        conditions: list[ColumnElement[bool]] = [
            Project.category_id == category_id,
        ]

        if not include_deleted:
            conditions.append(
                Project.deleted_at.is_(None),
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(statement)

        return bool(result.scalar_one())


project_repository = ProjectRepository()
