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

from app.models.experience import Experience
from app.repositories.base import BaseRepository


class ExperienceRepository(
    BaseRepository[Experience],
):
    """Database operations for portfolio experiences."""

    def __init__(self) -> None:
        super().__init__(Experience)

    async def get_by_id(
        self,
        session: AsyncSession,
        experience_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Experience | None:
        """
        Return an experience by UUID.

        Soft-deleted records are excluded unless
        ``include_deleted`` is enabled.
        """

        statement = select(Experience).where(
            Experience.id == experience_id,
        )

        if not include_deleted:
            statement = statement.where(
                Experience.deleted_at.is_(None),
            )

        result = await session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        session: AsyncSession,
        slug: str,
        *,
        include_deleted: bool = False,
    ) -> Experience | None:
        """
        Return an experience by normalized slug.

        This method does not apply public-visibility rules and is
        therefore suitable for administrative access.
        """

        normalized_slug = slug.strip().lower()

        statement = select(Experience).where(
            Experience.slug == normalized_slug,
        )

        if not include_deleted:
            statement = statement.where(
                Experience.deleted_at.is_(None),
            )

        result = await session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_public_by_slug(
        self,
        session: AsyncSession,
        slug: str,
    ) -> Experience | None:
        """
        Return a publicly visible experience by normalized slug.

        Public records must be visible and not soft-deleted.
        """

        normalized_slug = slug.strip().lower()

        statement = select(Experience).where(
            Experience.slug == normalized_slug,
            Experience.is_public.is_(True),
            Experience.deleted_at.is_(None),
        )

        result = await session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def list_public(
        self,
        session: AsyncSession,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        employment_type: str | None = None,
        location_type: str | None = None,
        is_current: bool | None = None,
        is_featured: bool | None = None,
    ) -> tuple[Sequence[Experience], int]:
        """
        Return paginated publicly visible experiences.

        Results may be filtered by engagement type, work-location
        arrangement, current status, featured status, or search text.
        """

        filters: list[ColumnElement[bool]] = [
            Experience.is_public.is_(True),
            Experience.deleted_at.is_(None),
        ]

        normalized_search = search.strip() if search and search.strip() else None

        if normalized_search:
            search_pattern = f"%{normalized_search}%"

            filters.append(
                or_(
                    Experience.company_name.ilike(
                        search_pattern,
                    ),
                    Experience.job_title.ilike(
                        search_pattern,
                    ),
                    Experience.slug.ilike(
                        search_pattern,
                    ),
                    Experience.location.ilike(
                        search_pattern,
                    ),
                    Experience.summary.ilike(
                        search_pattern,
                    ),
                    Experience.responsibilities.ilike(
                        search_pattern,
                    ),
                    Experience.achievements.ilike(
                        search_pattern,
                    ),
                )
            )

        normalized_employment_type = (
            employment_type.strip().lower()
            if employment_type and employment_type.strip()
            else None
        )

        if normalized_employment_type:
            filters.append(
                Experience.employment_type == normalized_employment_type,
            )

        normalized_location_type = (
            location_type.strip().lower()
            if location_type and location_type.strip()
            else None
        )

        if normalized_location_type:
            filters.append(
                Experience.location_type == normalized_location_type,
            )

        if is_current is not None:
            filters.append(
                Experience.is_current.is_(is_current),
            )

        if is_featured is not None:
            filters.append(
                Experience.is_featured.is_(is_featured),
            )

        count_statement = select(
            func.count(Experience.id),
        ).where(*filters)

        total_result = await session.execute(
            count_statement,
        )

        total = int(
            total_result.scalar_one(),
        )

        statement = (
            select(Experience)
            .where(*filters)
            .order_by(
                Experience.is_current.desc(),
                Experience.is_featured.desc(),
                Experience.sort_order.asc(),
                Experience.start_date.desc(),
                Experience.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(
            statement,
        )

        experiences = result.scalars().all()

        return experiences, total

    async def list_featured(
        self,
        session: AsyncSession,
        *,
        limit: int,
    ) -> Sequence[Experience]:
        """
        Return featured publicly visible experiences.

        Current positions appear before completed positions, followed
        by configured sort order and start date.
        """

        statement = (
            select(Experience)
            .where(
                Experience.is_public.is_(True),
                Experience.is_featured.is_(True),
                Experience.deleted_at.is_(None),
            )
            .order_by(
                Experience.is_current.desc(),
                Experience.sort_order.asc(),
                Experience.start_date.desc(),
                Experience.id.asc(),
            )
            .limit(limit)
        )

        result = await session.execute(
            statement,
        )

        return result.scalars().all()

    async def list_for_admin(
        self,
        session: AsyncSession,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        employment_type: str | None = None,
        location_type: str | None = None,
        is_current: bool | None = None,
        is_public: bool | None = None,
        is_featured: bool | None = None,
        include_deleted: bool = False,
        sort_by: str = "start_date",
        sort_direction: str = "desc",
    ) -> tuple[Sequence[Experience], int]:
        """
        Return paginated experiences for administrative management.

        Administrative results support lifecycle, visibility,
        engagement, location, search, sorting, and deletion filters.
        """

        filters: list[ColumnElement[bool]] = []

        if not include_deleted:
            filters.append(
                Experience.deleted_at.is_(None),
            )

        normalized_search = search.strip() if search and search.strip() else None

        if normalized_search:
            search_pattern = f"%{normalized_search}%"

            filters.append(
                or_(
                    Experience.company_name.ilike(
                        search_pattern,
                    ),
                    Experience.job_title.ilike(
                        search_pattern,
                    ),
                    Experience.slug.ilike(
                        search_pattern,
                    ),
                    Experience.location.ilike(
                        search_pattern,
                    ),
                    Experience.summary.ilike(
                        search_pattern,
                    ),
                    Experience.responsibilities.ilike(
                        search_pattern,
                    ),
                    Experience.achievements.ilike(
                        search_pattern,
                    ),
                )
            )

        normalized_employment_type = (
            employment_type.strip().lower()
            if employment_type and employment_type.strip()
            else None
        )

        if normalized_employment_type:
            filters.append(
                Experience.employment_type == normalized_employment_type,
            )

        normalized_location_type = (
            location_type.strip().lower()
            if location_type and location_type.strip()
            else None
        )

        if normalized_location_type:
            filters.append(
                Experience.location_type == normalized_location_type,
            )

        if is_current is not None:
            filters.append(
                Experience.is_current.is_(is_current),
            )

        if is_public is not None:
            filters.append(
                Experience.is_public.is_(is_public),
            )

        if is_featured is not None:
            filters.append(
                Experience.is_featured.is_(is_featured),
            )

        sort_columns = {
            "company_name": Experience.company_name,
            "job_title": Experience.job_title,
            "slug": Experience.slug,
            "employment_type": Experience.employment_type,
            "location_type": Experience.location_type,
            "start_date": Experience.start_date,
            "end_date": Experience.end_date,
            "is_current": Experience.is_current,
            "is_public": Experience.is_public,
            "is_featured": Experience.is_featured,
            "sort_order": Experience.sort_order,
            "created_at": Experience.created_at,
            "updated_at": Experience.updated_at,
        }

        sort_column = sort_columns.get(
            sort_by,
            Experience.start_date,
        )

        normalized_direction = sort_direction.strip().lower()

        sort_expression = (
            asc(sort_column) if normalized_direction == "asc" else desc(sort_column)
        )

        count_statement = select(
            func.count(Experience.id),
        ).where(*filters)

        total_result = await session.execute(
            count_statement,
        )

        total = int(
            total_result.scalar_one(),
        )

        statement = (
            select(Experience)
            .where(*filters)
            .order_by(
                sort_expression,
                Experience.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(
            statement,
        )

        experiences = result.scalars().all()

        return experiences, total

    async def slug_exists(
        self,
        session: AsyncSession,
        slug: str,
        *,
        exclude_experience_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether an experience slug is already in use.

        An experience UUID can be excluded when validating an update.
        """

        normalized_slug = slug.strip().lower()

        conditions: list[ColumnElement[bool]] = [
            Experience.slug == normalized_slug,
        ]

        if exclude_experience_id is not None:
            conditions.append(
                Experience.id != exclude_experience_id,
            )

        if not include_deleted:
            conditions.append(
                Experience.deleted_at.is_(None),
            )

        statement = select(
            exists().where(*conditions),
        )

        result = await session.execute(
            statement,
        )

        return bool(
            result.scalar_one(),
        )

    async def count_public(
        self,
        session: AsyncSession,
        *,
        employment_type: str | None = None,
        is_current: bool | None = None,
        is_featured: bool | None = None,
    ) -> int:
        """
        Count publicly visible experiences.

        The count can be filtered by engagement type, current status,
        or featured status.
        """

        conditions: list[ColumnElement[bool]] = [
            Experience.is_public.is_(True),
            Experience.deleted_at.is_(None),
        ]

        normalized_employment_type = (
            employment_type.strip().lower()
            if employment_type and employment_type.strip()
            else None
        )

        if normalized_employment_type:
            conditions.append(
                Experience.employment_type == normalized_employment_type,
            )

        if is_current is not None:
            conditions.append(
                Experience.is_current.is_(is_current),
            )

        if is_featured is not None:
            conditions.append(
                Experience.is_featured.is_(is_featured),
            )

        statement = select(
            func.count(Experience.id),
        ).where(*conditions)

        result = await session.execute(
            statement,
        )

        return int(
            result.scalar_one(),
        )


experience_repository = ExperienceRepository()
