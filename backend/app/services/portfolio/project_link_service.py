from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_link import ProjectLink
from app.repositories.portfolio.project_link_repository import (
    ProjectLinkRepository,
    project_link_repository,
)
from app.repositories.portfolio.project_repository import (
    ProjectRepository,
    project_repository,
)
from app.schemas.portfolio.project_link import (
    ProjectLinkCreate,
    ProjectLinkUpdate,
)


class ProjectLinkNotFoundError(Exception):
    """Raised when requested project link does not exist."""


class ProjectLinkProjectNotFoundError(Exception):
    """Raised when the parent project does not exist."""


class ProjectLinkConflictError(Exception):
    """Raised when project-link data violates a uniqueness rule."""


class ProjectLinkService:
    """Business operations for portfolio project links."""

    def __init__(
        self,
        repository: ProjectLinkRepository,
        projects: ProjectRepository,
    ) -> None:
        self.repository = repository
        self.projects = projects

    async def get_by_id(
        self,
        session: AsyncSession,
        link_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ProjectLink:
        """Return a project link or raise a not-found error."""

        link = await self.repository.get_by_id(
            session,
            link_id,
            include_deleted=include_deleted,
        )

        if link is None:
            raise ProjectLinkNotFoundError(
                "Project link was not found.",
            )

        return link

    async def list_public_for_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        link_type: str | None = None,
    ) -> Sequence[ProjectLink]:
        """Return active public links for a project."""

        await self._ensure_project_exists(
            session,
            project_id,
        )

        return await self.repository.list_public_for_project(
            session,
            project_id,
            link_type=self._normalize_optional_value(
                link_type,
            ),
        )

    async def list_for_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        include_inactive: bool = True,
        include_deleted: bool = False,
        link_type: str | None = None,
    ) -> Sequence[ProjectLink]:
        """Return project links for administrative or internal use."""

        await self._ensure_project_exists(
            session,
            project_id,
            include_deleted=include_deleted,
        )

        return await self.repository.list_for_project(
            session,
            project_id,
            include_inactive=include_inactive,
            include_deleted=include_deleted,
            link_type=self._normalize_optional_value(
                link_type,
            ),
        )

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
        """Return paginated project links for administrators."""

        await self._ensure_project_exists(
            session,
            project_id,
            include_deleted=True,
        )

        return await self.repository.list_for_admin(
            session,
            project_id=project_id,
            offset=offset,
            limit=limit,
            search=search,
            link_type=self._normalize_optional_value(
                link_type,
            ),
            is_active=is_active,
            opens_in_new_tab=opens_in_new_tab,
            include_deleted=include_deleted,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def create(
        self,
        session: AsyncSession,
        project_id: UUID,
        payload: ProjectLinkCreate,
    ) -> ProjectLink:
        """
        Create and flush a project link.

        Transaction commit remains the responsibility of the API or
        unit-of-work boundary.
        """

        await self._ensure_project_exists(
            session,
            project_id,
        )

        data = payload.model_dump(
            mode="json",
        )

        await self._ensure_url_available(
            session,
            project_id,
            data["url"],
        )

        await self._ensure_label_available(
            session,
            project_id,
            data["label"],
        )

        link = ProjectLink(
            project_id=project_id,
            **data,
        )

        session.add(link)
        await session.flush()
        await session.refresh(link)

        return link

    async def update(
        self,
        session: AsyncSession,
        link_id: UUID,
        payload: ProjectLinkUpdate,
    ) -> ProjectLink:
        """Update and flush an existing project link."""

        link = await self.get_by_id(
            session,
            link_id,
        )

        data = payload.model_dump(
            mode="json",
            exclude_unset=True,
        )

        if "url" in data:
            await self._ensure_url_available(
                session,
                link.project_id,
                data["url"],
                exclude_link_id=link.id,
            )

        if "label" in data:
            await self._ensure_label_available(
                session,
                link.project_id,
                data["label"],
                exclude_link_id=link.id,
            )

        for field_name, value in data.items():
            setattr(
                link,
                field_name,
                value,
            )

        await session.flush()
        await session.refresh(link)

        return link

    async def set_active(
        self,
        session: AsyncSession,
        link_id: UUID,
        *,
        is_active: bool,
    ) -> ProjectLink:
        """Activate or deactivate a non-deleted project link."""

        link = await self.get_by_id(
            session,
            link_id,
        )

        link.is_active = is_active

        await session.flush()
        await session.refresh(link)

        return link

    async def soft_delete(
        self,
        session: AsyncSession,
        link_id: UUID,
    ) -> ProjectLink:
        """Soft-delete a project link."""

        link = await self.get_by_id(
            session,
            link_id,
        )

        link.is_active = False
        link.soft_delete()

        await session.flush()
        await session.refresh(link)

        return link

    async def restore(
        self,
        session: AsyncSession,
        link_id: UUID,
        *,
        restore_as_active: bool = True,
    ) -> ProjectLink:
        """Restore a deleted link after uniqueness validation."""

        link = await self.get_by_id(
            session,
            link_id,
            include_deleted=True,
        )

        if link.deleted_at is None:
            if restore_as_active and not link.is_active:
                link.is_active = True
                await session.flush()
                await session.refresh(link)

            return link

        await self._ensure_project_exists(
            session,
            link.project_id,
        )

        await self._ensure_url_available(
            session,
            link.project_id,
            link.url,
            exclude_link_id=link.id,
        )

        await self._ensure_label_available(
            session,
            link.project_id,
            link.label,
            exclude_link_id=link.id,
        )

        link.restore()
        link.is_active = restore_as_active

        await session.flush()
        await session.refresh(link)

        return link

    async def count_for_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        link_type: str | None = None,
        is_active: bool | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count project links matching the supplied filters."""

        await self._ensure_project_exists(
            session,
            project_id,
            include_deleted=True,
        )

        return await self.repository.count_for_project(
            session,
            project_id,
            link_type=self._normalize_optional_value(
                link_type,
            ),
            is_active=is_active,
            include_deleted=include_deleted,
        )

    async def _ensure_project_exists(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> None:
        """Ensure the parent project exists."""

        project = await self.projects.get_by_id(
            session,
            project_id,
            include_deleted=include_deleted,
            include_related=False,
        )

        if project is None:
            raise ProjectLinkProjectNotFoundError(
                "The project assigned to this link was not found.",
            )

    async def _ensure_url_available(
        self,
        session: AsyncSession,
        project_id: UUID,
        url: str,
        *,
        exclude_link_id: UUID | None = None,
    ) -> None:
        """Ensure a URL is unique within its project."""

        url_exists = await self.repository.url_exists(
            session,
            project_id,
            url,
            exclude_link_id=exclude_link_id,
        )

        if url_exists:
            raise ProjectLinkConflictError(
                "This URL is already assigned to the project.",
            )

    async def _ensure_label_available(
        self,
        session: AsyncSession,
        project_id: UUID,
        label: str,
        *,
        exclude_link_id: UUID | None = None,
    ) -> None:
        """Ensure a link label is unique within its project."""

        label_exists = await self.repository.label_exists(
            session,
            project_id,
            label,
            exclude_link_id=exclude_link_id,
        )

        if label_exists:
            raise ProjectLinkConflictError(
                "This link label is already assigned to the project.",
            )

    @staticmethod
    def _normalize_optional_value(
        value: str | None,
    ) -> str | None:
        """Normalize an optional lowercase filter value."""

        if value is None:
            return None

        normalized_value = value.strip().lower()

        return normalized_value or None


project_link_service = ProjectLinkService(
    project_link_repository,
    project_repository,
)
