from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_technology import ProjectTechnology
from app.repositories.portfolio.project_technology_repository import (
    ProjectTechnologyRepository,
    project_technology_repository,
)
from app.schemas.portfolio.project_technology import (
    ProjectTechnologyCreate,
    ProjectTechnologyUpdate,
)


class ProjectTechnologyNotFoundError(Exception):
    """Raised when a requested project technology does not exist."""


class ProjectTechnologyConflictError(Exception):
    """Raised when technology data violates a uniqueness rule."""


class ProjectTechnologyInUseError(Exception):
    """Raised when projects still use a technology being deleted."""


class ProjectTechnologyService:
    """Business operations for portfolio project technologies."""

    def __init__(
        self,
        repository: ProjectTechnologyRepository,
    ) -> None:
        self.repository = repository

    async def get_by_id(
        self,
        session: AsyncSession,
        technology_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ProjectTechnology:
        """Return a project technology or raise a not-found error."""

        technology = await self.repository.get_by_id(
            session,
            technology_id,
            include_deleted=include_deleted,
        )

        if technology is None:
            raise ProjectTechnologyNotFoundError(
                "Project technology was not found.",
            )

        return technology

    async def get_by_slug(
        self,
        session: AsyncSession,
        slug: str,
        *,
        include_deleted: bool = False,
    ) -> ProjectTechnology:
        """Return a technology by slug or raise a not-found error."""

        normalized_slug = self._normalize_slug(slug)

        technology = await self.repository.get_by_slug(
            session,
            normalized_slug,
            include_deleted=include_deleted,
        )

        if technology is None:
            raise ProjectTechnologyNotFoundError(
                "Project technology was not found.",
            )

        return technology

    async def list_public(
        self,
        session: AsyncSession,
        *,
        category: str | None = None,
    ) -> Sequence[ProjectTechnology]:
        """Return active technologies available to public clients."""

        normalized_category = self._normalize_optional_value(
            category,
        )

        return await self.repository.list_public(
            session,
            category=normalized_category,
        )

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
        """Return paginated technologies for administrative use."""

        normalized_category = self._normalize_optional_value(
            category,
        )

        return await self.repository.list_for_admin(
            session,
            offset=offset,
            limit=limit,
            search=search,
            category=normalized_category,
            is_active=is_active,
            include_deleted=include_deleted,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def create(
        self,
        session: AsyncSession,
        payload: ProjectTechnologyCreate,
    ) -> ProjectTechnology:
        """
        Create and flush a project technology.

        Transaction commit remains the responsibility of the API or
        unit-of-work boundary.
        """

        data = payload.model_dump(
            mode="json",
        )

        name = self._normalize_name(
            data["name"],
        )
        slug = self._normalize_slug(
            data["slug"],
        )

        await self._ensure_name_available(
            session,
            name,
        )

        await self._ensure_slug_available(
            session,
            slug,
        )

        technology = ProjectTechnology(
            **data,
            name=name,
            slug=slug,
        )

        session.add(technology)
        await session.flush()
        await session.refresh(technology)

        return technology

    async def update(
        self,
        session: AsyncSession,
        technology_id: UUID,
        payload: ProjectTechnologyUpdate,
    ) -> ProjectTechnology:
        """Update and flush an existing project technology."""

        technology = await self.get_by_id(
            session,
            technology_id,
        )

        data = payload.model_dump(
            mode="json",
            exclude_unset=True,
        )

        if "name" in data:
            normalized_name = self._normalize_name(
                data["name"],
            )

            await self._ensure_name_available(
                session,
                normalized_name,
                exclude_technology_id=technology.id,
            )

            data["name"] = normalized_name

        if "slug" in data:
            normalized_slug = self._normalize_slug(
                data["slug"],
            )

            await self._ensure_slug_available(
                session,
                normalized_slug,
                exclude_technology_id=technology.id,
            )

            data["slug"] = normalized_slug

        for field_name, value in data.items():
            setattr(
                technology,
                field_name,
                value,
            )

        await session.flush()
        await session.refresh(technology)

        return technology

    async def soft_delete(
        self,
        session: AsyncSession,
        technology_id: UUID,
        *,
        allow_if_assigned: bool = False,
    ) -> ProjectTechnology:
        """
        Soft-delete a project technology.

        Deletion is blocked when non-deleted projects still use the
        technology unless ``allow_if_assigned`` is enabled.
        """

        technology = await self.get_by_id(
            session,
            technology_id,
        )

        if not allow_if_assigned:
            has_projects = await self.repository.has_projects(
                session,
                technology.id,
            )

            if has_projects:
                raise ProjectTechnologyInUseError(
                    "Project technology is assigned to one or more projects.",
                )

        technology.soft_delete()

        await session.flush()
        await session.refresh(technology)

        return technology

    async def restore(
        self,
        session: AsyncSession,
        technology_id: UUID,
    ) -> ProjectTechnology:
        """Restore a soft-deleted technology after conflict checks."""

        technology = await self.get_by_id(
            session,
            technology_id,
            include_deleted=True,
        )

        if technology.deleted_at is None:
            return technology

        await self._ensure_name_available(
            session,
            technology.name,
            exclude_technology_id=technology.id,
        )

        await self._ensure_slug_available(
            session,
            technology.slug,
            exclude_technology_id=technology.id,
        )

        technology.restore()

        await session.flush()
        await session.refresh(technology)

        return technology

    async def set_active(
        self,
        session: AsyncSession,
        technology_id: UUID,
        *,
        is_active: bool,
    ) -> ProjectTechnology:
        """Activate or deactivate a non-deleted technology."""

        technology = await self.get_by_id(
            session,
            technology_id,
        )

        technology.is_active = is_active

        await session.flush()
        await session.refresh(technology)

        return technology

    async def count_projects(
        self,
        session: AsyncSession,
        technology_id: UUID,
        *,
        include_deleted_associations: bool = False,
        include_deleted_projects: bool = False,
    ) -> int:
        """Count projects associated with a technology."""

        await self.get_by_id(
            session,
            technology_id,
            include_deleted=True,
        )

        return await self.repository.count_projects(
            session,
            technology_id,
            include_deleted_associations=include_deleted_associations,
            include_deleted_projects=include_deleted_projects,
        )

    async def is_assigned_to_project(
        self,
        session: AsyncSession,
        technology_id: UUID,
        project_id: UUID,
    ) -> bool:
        """Check for an active technology-to-project association."""

        return await self.repository.has_active_association(
            session,
            technology_id,
            project_id,
        )

    async def _ensure_name_available(
        self,
        session: AsyncSession,
        name: str,
        *,
        exclude_technology_id: UUID | None = None,
    ) -> None:
        """Raise a conflict when a non-deleted name already exists."""

        name_exists = await self.repository.name_exists(
            session,
            name,
            exclude_technology_id=exclude_technology_id,
        )

        if name_exists:
            raise ProjectTechnologyConflictError(
                "A project technology with this name already exists.",
            )

    async def _ensure_slug_available(
        self,
        session: AsyncSession,
        slug: str,
        *,
        exclude_technology_id: UUID | None = None,
    ) -> None:
        """Raise a conflict when a non-deleted slug already exists."""

        slug_exists = await self.repository.slug_exists(
            session,
            slug,
            exclude_technology_id=exclude_technology_id,
        )

        if slug_exists:
            raise ProjectTechnologyConflictError(
                "A project technology with this slug already exists.",
            )

    @staticmethod
    def _normalize_name(value: str) -> str:
        """Normalize whitespace in a technology name."""

        return " ".join(value.split())

    @staticmethod
    def _normalize_slug(value: str) -> str:
        """Normalize a technology slug."""

        return value.strip().lower()

    @staticmethod
    def _normalize_optional_value(
        value: str | None,
    ) -> str | None:
        """Normalize an optional lowercase filter value."""

        if value is None:
            return None

        normalized_value = value.strip().lower()

        return normalized_value or None


project_technology_service = ProjectTechnologyService(
    project_technology_repository,
)
