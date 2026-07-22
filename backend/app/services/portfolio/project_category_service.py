from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_category import ProjectCategory
from app.repositories.portfolio.project_category_repository import (
    ProjectCategoryRepository,
    project_category_repository,
)
from app.schemas.portfolio.project_category import (
    ProjectCategoryCreate,
    ProjectCategoryUpdate,
)


class ProjectCategoryNotFoundError(Exception):
    """Raised when a requested project category does not exist."""


class ProjectCategoryConflictError(Exception):
    """Raised when project-category data violates a uniqueness rule."""


class ProjectCategoryInUseError(Exception):
    """Raised when a category cannot be deleted because projects use it."""


class ProjectCategoryService:
    """Business operations for portfolio project categories."""

    def __init__(
        self,
        repository: ProjectCategoryRepository,
    ) -> None:
        self.repository = repository

    async def get_by_id(
        self,
        session: AsyncSession,
        category_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ProjectCategory:
        """Return a project category or raise a not-found error."""

        category = await self.repository.get_by_id(
            session,
            category_id,
            include_deleted=include_deleted,
        )

        if category is None:
            raise ProjectCategoryNotFoundError(
                "Project category was not found.",
            )

        return category

    async def get_by_slug(
        self,
        session: AsyncSession,
        slug: str,
        *,
        include_deleted: bool = False,
    ) -> ProjectCategory:
        """Return a category by slug or raise a not-found error."""

        normalized_slug = self._normalize_slug(
            slug,
        )

        category = await self.repository.get_by_slug(
            session,
            normalized_slug,
            include_deleted=include_deleted,
        )

        if category is None:
            raise ProjectCategoryNotFoundError(
                "Project category was not found.",
            )

        return category

    async def list_public(
        self,
        session: AsyncSession,
    ) -> Sequence[ProjectCategory]:
        """Return active categories available to public clients."""

        return await self.repository.list_public(
            session,
        )

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
        """Return paginated categories for administrative management."""

        return await self.repository.list_for_admin(
            session,
            offset=offset,
            limit=limit,
            search=search,
            is_active=is_active,
            include_deleted=include_deleted,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def create(
        self,
        session: AsyncSession,
        payload: ProjectCategoryCreate,
    ) -> ProjectCategory:
        """
        Create and flush a project category.

        Transaction commit remains the responsibility of the API or
        unit-of-work boundary.
        """

        data = payload.model_dump()

        name = self._normalize_name(
            data.pop("name"),
        )
        slug = self._normalize_slug(
            data.pop("slug"),
        )

        await self._ensure_name_available(
            session,
            name,
        )

        await self._ensure_slug_available(
            session,
            slug,
        )

        category = ProjectCategory(
            **data,
            name=name,
            slug=slug,
        )

        return await self.repository.add(
            session,
            category,
        )

    async def update(
        self,
        session: AsyncSession,
        category_id: UUID,
        payload: ProjectCategoryUpdate,
    ) -> ProjectCategory:
        """Update and flush an existing project category."""

        category = await self.get_by_id(
            session,
            category_id,
        )

        data = payload.model_dump(
            exclude_unset=True,
        )

        if "name" in data:
            normalized_name = self._normalize_name(
                data["name"],
            )

            await self._ensure_name_available(
                session,
                normalized_name,
                exclude_category_id=category.id,
            )

            data["name"] = normalized_name

        if "slug" in data:
            normalized_slug = self._normalize_slug(
                data["slug"],
            )

            await self._ensure_slug_available(
                session,
                normalized_slug,
                exclude_category_id=category.id,
            )

            data["slug"] = normalized_slug

        for field_name, value in data.items():
            setattr(
                category,
                field_name,
                value,
            )

        await session.flush()
        await session.refresh(
            category,
        )

        return category

    async def soft_delete(
        self,
        session: AsyncSession,
        category_id: UUID,
        *,
        allow_if_assigned: bool = False,
    ) -> ProjectCategory:
        """
        Soft-delete a category.

        Deletion is blocked when active projects use the category unless
        ``allow_if_assigned`` is explicitly enabled.
        """

        category = await self.get_by_id(
            session,
            category_id,
        )

        if not allow_if_assigned:
            has_projects = await self.repository.has_projects(
                session,
                category.id,
            )

            if has_projects:
                raise ProjectCategoryInUseError(
                    "Project category is assigned to one or more projects.",
                )

        category.soft_delete()

        await session.flush()
        await session.refresh(
            category,
        )

        return category

    async def restore(
        self,
        session: AsyncSession,
        category_id: UUID,
    ) -> ProjectCategory:
        """Restore a soft-deleted category after uniqueness validation."""

        category = await self.get_by_id(
            session,
            category_id,
            include_deleted=True,
        )

        if category.deleted_at is None:
            return category

        await self._ensure_name_available(
            session,
            category.name,
            exclude_category_id=category.id,
        )

        await self._ensure_slug_available(
            session,
            category.slug,
            exclude_category_id=category.id,
        )

        category.restore()

        await session.flush()
        await session.refresh(
            category,
        )

        return category

    async def set_active(
        self,
        session: AsyncSession,
        category_id: UUID,
        *,
        is_active: bool,
    ) -> ProjectCategory:
        """Activate or deactivate a non-deleted category."""

        category = await self.get_by_id(
            session,
            category_id,
        )

        category.is_active = is_active

        await session.flush()
        await session.refresh(
            category,
        )

        return category

    async def _ensure_name_available(
        self,
        session: AsyncSession,
        name: str,
        *,
        exclude_category_id: UUID | None = None,
    ) -> None:
        """Raise a conflict error when an active name already exists."""

        exists = await self.repository.name_exists(
            session,
            name,
            exclude_category_id=exclude_category_id,
        )

        if exists:
            raise ProjectCategoryConflictError(
                "A project category with this name already exists.",
            )

    async def _ensure_slug_available(
        self,
        session: AsyncSession,
        slug: str,
        *,
        exclude_category_id: UUID | None = None,
    ) -> None:
        """Raise a conflict error when an active slug already exists."""

        exists = await self.repository.slug_exists(
            session,
            slug,
            exclude_category_id=exclude_category_id,
        )

        if exists:
            raise ProjectCategoryConflictError(
                "A project category with this slug already exists.",
            )

    @staticmethod
    def _normalize_name(
        value: str,
    ) -> str:
        """Normalize whitespace in a category name."""

        return " ".join(
            value.split(),
        )

    @staticmethod
    def _normalize_slug(
        value: str,
    ) -> str:
        """Normalize a category slug."""

        return value.strip().lower()


project_category_service = ProjectCategoryService(
    project_category_repository,
)
