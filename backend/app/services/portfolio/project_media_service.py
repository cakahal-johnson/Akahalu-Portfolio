from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_media import ProjectMedia
from app.repositories.portfolio.project_media_repository import (
    ProjectMediaRepository,
    project_media_repository,
)
from app.repositories.portfolio.project_repository import (
    ProjectRepository,
    project_repository,
)
from app.schemas.portfolio.project_media import (
    ProjectMediaCreate,
    ProjectMediaUpdate,
)


class ProjectMediaNotFoundError(Exception):
    """Raised when requested project media does not exist."""


class ProjectMediaProjectNotFoundError(Exception):
    """Raised when the parent project does not exist."""


class ProjectMediaConflictError(Exception):
    """Raised when media data violates a uniqueness rule."""


class ProjectMediaService:
    """Business operations for portfolio project media."""

    def __init__(
        self,
        repository: ProjectMediaRepository,
        projects: ProjectRepository,
    ) -> None:
        self.repository = repository
        self.projects = projects

    async def get_by_id(
        self,
        session: AsyncSession,
        media_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ProjectMedia:
        """Return project media or raise a not-found error."""

        media = await self.repository.get_by_id(
            session,
            media_id,
            include_deleted=include_deleted,
        )

        if media is None:
            raise ProjectMediaNotFoundError(
                "Project media was not found.",
            )

        return media

    async def get_primary(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> ProjectMedia | None:
        """Return the primary media assigned to a project."""

        await self._ensure_project_exists(
            session,
            project_id,
        )

        return await self.repository.get_primary(
            session,
            project_id,
            include_deleted=include_deleted,
        )

    async def list_for_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        media_type: str | None = None,
    ) -> Sequence[ProjectMedia]:
        """Return non-deleted media belonging to a project."""

        await self._ensure_project_exists(
            session,
            project_id,
        )

        return await self.repository.list_for_project(
            session,
            project_id,
            media_type=self._normalize_optional_value(
                media_type,
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
        media_type: str | None = None,
        is_primary: bool | None = None,
        include_deleted: bool = False,
        sort_by: str = "sort_order",
        sort_direction: str = "asc",
    ) -> tuple[Sequence[ProjectMedia], int]:
        """Return paginated media for administrative management."""

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
            media_type=self._normalize_optional_value(
                media_type,
            ),
            is_primary=is_primary,
            include_deleted=include_deleted,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def create(
        self,
        session: AsyncSession,
        project_id: UUID,
        payload: ProjectMediaCreate,
    ) -> ProjectMedia:
        """
        Create and flush project media.

        When the new media is primary, any existing primary media for
        the same project is demoted first.
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

        await self._ensure_provider_asset_available(
            session,
            provider=data.get("provider"),
            provider_asset_id=data.get("provider_asset_id"),
        )

        if data.get("is_primary", False):
            await self._clear_existing_primary(
                session,
                project_id,
            )

        media = ProjectMedia(
            project_id=project_id,
            **data,
        )

        session.add(media)
        await session.flush()
        await session.refresh(media)

        return media

    async def update(
        self,
        session: AsyncSession,
        media_id: UUID,
        payload: ProjectMediaUpdate,
    ) -> ProjectMedia:
        """Update and flush existing project media."""

        media = await self.get_by_id(
            session,
            media_id,
        )

        data = payload.model_dump(
            mode="json",
            exclude_unset=True,
        )

        if "url" in data:
            await self._ensure_url_available(
                session,
                media.project_id,
                data["url"],
                exclude_media_id=media.id,
            )

        provider = data["provider"] if "provider" in data else media.provider
        provider_asset_id = (
            data["provider_asset_id"]
            if "provider_asset_id" in data
            else media.provider_asset_id
        )

        if "provider" in data or "provider_asset_id" in data:
            await self._ensure_provider_asset_available(
                session,
                provider=provider,
                provider_asset_id=provider_asset_id,
                exclude_media_id=media.id,
            )

        if data.get("is_primary") is True:
            await self._clear_existing_primary(
                session,
                media.project_id,
                exclude_media_id=media.id,
            )

        for field_name, value in data.items():
            setattr(
                media,
                field_name,
                value,
            )

        await session.flush()
        await session.refresh(media)

        return media

    async def set_primary(
        self,
        session: AsyncSession,
        media_id: UUID,
    ) -> ProjectMedia:
        """Make one media item the project's exclusive primary media."""

        media = await self.get_by_id(
            session,
            media_id,
        )

        if media.is_primary:
            return media

        await self._clear_existing_primary(
            session,
            media.project_id,
            exclude_media_id=media.id,
        )

        media.is_primary = True

        await session.flush()
        await session.refresh(media)

        return media

    async def soft_delete(
        self,
        session: AsyncSession,
        media_id: UUID,
        *,
        assign_replacement_primary: bool = True,
    ) -> ProjectMedia:
        """
        Soft-delete project media.

        When primary media is deleted, the first remaining media item
        becomes primary unless replacement assignment is disabled.
        """

        media = await self.get_by_id(
            session,
            media_id,
        )

        project_id = media.project_id
        was_primary = media.is_primary

        media.is_primary = False
        media.soft_delete()

        await session.flush()

        if was_primary and assign_replacement_primary:
            await self._assign_replacement_primary(
                session,
                project_id,
            )

        await session.refresh(media)

        return media

    async def restore(
        self,
        session: AsyncSession,
        media_id: UUID,
        *,
        restore_as_primary: bool | None = None,
    ) -> ProjectMedia:
        """Restore soft-deleted media after uniqueness checks."""

        media = await self.get_by_id(
            session,
            media_id,
            include_deleted=True,
        )

        if media.deleted_at is None:
            return media

        await self._ensure_project_exists(
            session,
            media.project_id,
        )

        await self._ensure_url_available(
            session,
            media.project_id,
            media.url,
            exclude_media_id=media.id,
        )

        await self._ensure_provider_asset_available(
            session,
            provider=media.provider,
            provider_asset_id=media.provider_asset_id,
            exclude_media_id=media.id,
        )

        should_be_primary = (
            restore_as_primary if restore_as_primary is not None else media.is_primary
        )

        if should_be_primary:
            await self._clear_existing_primary(
                session,
                media.project_id,
                exclude_media_id=media.id,
            )

        media.restore()
        media.is_primary = should_be_primary

        await session.flush()
        await session.refresh(media)

        return media

    async def count_for_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        media_type: str | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count media records belonging to a project."""

        await self._ensure_project_exists(
            session,
            project_id,
            include_deleted=True,
        )

        return await self.repository.count_for_project(
            session,
            project_id,
            media_type=self._normalize_optional_value(
                media_type,
            ),
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
            raise ProjectMediaProjectNotFoundError(
                "The project assigned to this media was not found.",
            )

    async def _ensure_url_available(
        self,
        session: AsyncSession,
        project_id: UUID,
        url: str,
        *,
        exclude_media_id: UUID | None = None,
    ) -> None:
        """Ensure a media URL is unique within its project."""

        url_exists = await self.repository.url_exists(
            session,
            project_id,
            url,
            exclude_media_id=exclude_media_id,
        )

        if url_exists:
            raise ProjectMediaConflictError(
                "This media URL is already assigned to the project.",
            )

    async def _ensure_provider_asset_available(
        self,
        session: AsyncSession,
        *,
        provider: str | None,
        provider_asset_id: str | None,
        exclude_media_id: UUID | None = None,
    ) -> None:
        """Ensure a provider asset identity is globally unique."""

        if provider is None or provider_asset_id is None:
            return

        asset_exists = await self.repository.provider_asset_exists(
            session,
            provider,
            provider_asset_id,
            exclude_media_id=exclude_media_id,
        )

        if asset_exists:
            raise ProjectMediaConflictError(
                "This provider asset is already assigned to project media.",
            )

    async def _clear_existing_primary(
        self,
        session: AsyncSession,
        project_id: UUID,
        *,
        exclude_media_id: UUID | None = None,
    ) -> None:
        """Demote the current primary media when necessary."""

        primary = await self.repository.get_primary(
            session,
            project_id,
        )

        if primary is None:
            return

        if exclude_media_id is not None and primary.id == exclude_media_id:
            return

        primary.is_primary = False
        await session.flush()

    async def _assign_replacement_primary(
        self,
        session: AsyncSession,
        project_id: UUID,
    ) -> None:
        """Promote the first remaining project-media item."""

        remaining_media = await self.repository.list_for_project(
            session,
            project_id,
        )

        if not remaining_media:
            return

        replacement = remaining_media[0]
        replacement.is_primary = True

        await session.flush()

    @staticmethod
    def _normalize_optional_value(
        value: str | None,
    ) -> str | None:
        """Normalize an optional lowercase filter."""

        if value is None:
            return None

        normalized_value = value.strip().lower()

        return normalized_value or None


project_media_service = ProjectMediaService(
    project_media_repository,
    project_repository,
)
