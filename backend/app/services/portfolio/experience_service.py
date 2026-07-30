from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.experience import Experience
from app.repositories.portfolio.experience_repository import (
    ExperienceRepository,
    experience_repository,
)
from app.schemas.portfolio.experience import (
    ExperienceCreate,
    ExperienceUpdate,
)


class ExperienceNotFoundError(Exception):
    """Raised when a requested portfolio experience does not exist."""


class ExperienceConflictError(Exception):
    """Raised when experience data violates a uniqueness rule."""


class ExperienceLifecycleError(Exception):
    """Raised when experience dates or lifecycle fields are inconsistent."""


class ExperienceService:
    """Coordinate the complete portfolio-experience lifecycle."""

    def __init__(
        self,
        repository: ExperienceRepository,
    ) -> None:
        self.repository = repository

    async def get_by_id(
        self,
        session: AsyncSession,
        experience_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Experience:
        """Return an experience by ID or raise a not-found error."""

        experience = await self.repository.get_by_id(
            session,
            experience_id,
            include_deleted=include_deleted,
        )

        if experience is None:
            raise ExperienceNotFoundError(
                "Portfolio experience was not found.",
            )

        return experience

    async def get_by_slug(
        self,
        session: AsyncSession,
        slug: str,
        *,
        include_deleted: bool = False,
    ) -> Experience:
        """Return an experience by slug or raise a not-found error."""

        normalized_slug = self._normalize_slug(
            slug,
        )

        experience = await self.repository.get_by_slug(
            session,
            normalized_slug,
            include_deleted=include_deleted,
        )

        if experience is None:
            raise ExperienceNotFoundError(
                "Portfolio experience was not found.",
            )

        return experience

    async def get_public_by_slug(
        self,
        session: AsyncSession,
        slug: str,
    ) -> Experience:
        """Return a publicly visible experience by slug."""

        normalized_slug = self._normalize_slug(
            slug,
        )

        experience = await self.repository.get_public_by_slug(
            session,
            normalized_slug,
        )

        if experience is None:
            raise ExperienceNotFoundError(
                "Public portfolio experience was not found.",
            )

        return experience

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
        """Return paginated publicly visible experiences."""

        return await self.repository.list_public(
            session,
            offset=offset,
            limit=limit,
            search=self._normalize_optional_text(
                search,
            ),
            employment_type=self._normalize_optional_value(
                employment_type,
            ),
            location_type=self._normalize_optional_value(
                location_type,
            ),
            is_current=is_current,
            is_featured=is_featured,
        )

    async def list_featured(
        self,
        session: AsyncSession,
        *,
        limit: int,
    ) -> Sequence[Experience]:
        """Return featured publicly visible experiences."""

        return await self.repository.list_featured(
            session,
            limit=limit,
        )

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
        """Return paginated experiences for administrative management."""

        return await self.repository.list_for_admin(
            session,
            offset=offset,
            limit=limit,
            search=self._normalize_optional_text(
                search,
            ),
            employment_type=self._normalize_optional_value(
                employment_type,
            ),
            location_type=self._normalize_optional_value(
                location_type,
            ),
            is_current=is_current,
            is_public=is_public,
            is_featured=is_featured,
            include_deleted=include_deleted,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def create(
        self,
        session: AsyncSession,
        payload: ExperienceCreate,
        *,
        actor_user_id: UUID | None = None,
    ) -> Experience:
        """
        Create and flush a portfolio experience.

        Transaction commit remains the responsibility of the API or
        unit-of-work boundary.
        """

        data = payload.model_dump(
            mode="python",
        )

        data["company_name"] = self._normalize_single_line_text(
            str(data["company_name"]),
        )
        data["job_title"] = self._normalize_single_line_text(
            str(data["job_title"]),
        )
        data["slug"] = self._normalize_slug(
            str(data["slug"]),
        )
        data["employment_type"] = self._normalize_value(
            str(data["employment_type"]),
        )
        data["location_type"] = self._normalize_value(
            str(data["location_type"]),
        )

        await self._ensure_slug_available(
            session,
            str(data["slug"]),
        )

        self._validate_lifecycle_data(
            start_date=self._coerce_date(
                data["start_date"],
            ),
            end_date=self._coerce_optional_date(
                data.get("end_date"),
            ),
            is_current=bool(
                data.get(
                    "is_current",
                    False,
                )
            ),
            is_public=bool(
                data.get(
                    "is_public",
                    False,
                )
            ),
            is_featured=bool(
                data.get(
                    "is_featured",
                    False,
                )
            ),
        )

        if actor_user_id is not None:
            data["created_by_id"] = actor_user_id
            data["updated_by_id"] = actor_user_id

        experience = Experience(
            **data,
        )

        session.add(
            experience,
        )

        await session.flush()
        await session.refresh(
            experience,
        )

        return experience

    async def update(
        self,
        session: AsyncSession,
        experience_id: UUID,
        payload: ExperienceUpdate,
        *,
        actor_user_id: UUID | None = None,
    ) -> Experience:
        """Update and flush an existing portfolio experience."""

        experience = await self.get_by_id(
            session,
            experience_id,
        )

        data = payload.model_dump(
            mode="python",
            exclude_unset=True,
        )

        if "company_name" in data:
            data["company_name"] = self._normalize_single_line_text(
                str(data["company_name"]),
            )

        if "job_title" in data:
            data["job_title"] = self._normalize_single_line_text(
                str(data["job_title"]),
            )

        if "slug" in data:
            normalized_slug = self._normalize_slug(
                str(data["slug"]),
            )

            await self._ensure_slug_available(
                session,
                normalized_slug,
                exclude_experience_id=experience.id,
            )

            data["slug"] = normalized_slug

        if "employment_type" in data:
            data["employment_type"] = self._normalize_value(
                str(data["employment_type"]),
            )

        if "location_type" in data:
            data["location_type"] = self._normalize_value(
                str(data["location_type"]),
            )

        resulting_start_date = self._coerce_date(
            data.get(
                "start_date",
                experience.start_date,
            )
        )

        resulting_end_date = self._coerce_optional_date(
            data.get(
                "end_date",
                experience.end_date,
            )
        )

        resulting_is_current = bool(
            data.get(
                "is_current",
                experience.is_current,
            )
        )

        resulting_is_public = bool(
            data.get(
                "is_public",
                experience.is_public,
            )
        )

        resulting_is_featured = bool(
            data.get(
                "is_featured",
                experience.is_featured,
            )
        )

        self._validate_lifecycle_data(
            start_date=resulting_start_date,
            end_date=resulting_end_date,
            is_current=resulting_is_current,
            is_public=resulting_is_public,
            is_featured=resulting_is_featured,
        )

        if actor_user_id is not None:
            data["updated_by_id"] = actor_user_id

        for field_name, value in data.items():
            setattr(
                experience,
                field_name,
                value,
            )

        await session.flush()
        await session.refresh(
            experience,
        )

        return experience

    async def set_visibility(
        self,
        session: AsyncSession,
        experience_id: UUID,
        *,
        is_public: bool,
        actor_user_id: UUID | None = None,
    ) -> Experience:
        """Set whether an experience is publicly visible."""

        experience = await self.get_by_id(
            session,
            experience_id,
        )

        experience.is_public = is_public

        if not is_public:
            experience.is_featured = False

        if actor_user_id is not None:
            experience.updated_by_id = actor_user_id

        await session.flush()
        await session.refresh(
            experience,
        )

        return experience

    async def set_featured(
        self,
        session: AsyncSession,
        experience_id: UUID,
        *,
        is_featured: bool,
        actor_user_id: UUID | None = None,
    ) -> Experience:
        """Set whether an experience is featured publicly."""

        experience = await self.get_by_id(
            session,
            experience_id,
        )

        if is_featured and not experience.is_public:
            raise ExperienceLifecycleError(
                "Only public experiences can be featured.",
            )

        experience.is_featured = is_featured

        if actor_user_id is not None:
            experience.updated_by_id = actor_user_id

        await session.flush()
        await session.refresh(
            experience,
        )

        return experience

    async def soft_delete(
        self,
        session: AsyncSession,
        experience_id: UUID,
        *,
        actor_user_id: UUID | None = None,
    ) -> Experience:
        """Soft-delete a portfolio experience."""

        experience = await self.get_by_id(
            session,
            experience_id,
        )

        experience.is_public = False
        experience.is_featured = False

        if actor_user_id is not None:
            experience.updated_by_id = actor_user_id

        experience.soft_delete()

        await session.flush()
        await session.refresh(
            experience,
        )

        return experience

    async def restore(
        self,
        session: AsyncSession,
        experience_id: UUID,
        *,
        actor_user_id: UUID | None = None,
        make_public: bool = False,
    ) -> Experience:
        """Restore a previously soft-deleted portfolio experience."""

        experience = await self.get_by_id(
            session,
            experience_id,
            include_deleted=True,
        )

        if experience.deleted_at is None:
            if experience.is_public != make_public:
                experience.is_public = make_public

                if not make_public:
                    experience.is_featured = False

                if actor_user_id is not None:
                    experience.updated_by_id = actor_user_id

                await session.flush()
                await session.refresh(
                    experience,
                )

            return experience

        await self._ensure_slug_available(
            session,
            experience.slug,
            exclude_experience_id=experience.id,
        )

        self._validate_lifecycle_data(
            start_date=experience.start_date,
            end_date=experience.end_date,
            is_current=experience.is_current,
            is_public=make_public,
            is_featured=False,
        )

        experience.restore()
        experience.is_public = make_public
        experience.is_featured = False

        if actor_user_id is not None:
            experience.updated_by_id = actor_user_id

        await session.flush()
        await session.refresh(
            experience,
        )

        return experience

    async def count_public(
        self,
        session: AsyncSession,
        *,
        employment_type: str | None = None,
        is_current: bool | None = None,
        is_featured: bool | None = None,
    ) -> int:
        """Count public experiences matching the supplied filters."""

        return await self.repository.count_public(
            session,
            employment_type=self._normalize_optional_value(
                employment_type,
            ),
            is_current=is_current,
            is_featured=is_featured,
        )

    async def _ensure_slug_available(
        self,
        session: AsyncSession,
        slug: str,
        *,
        exclude_experience_id: UUID | None = None,
    ) -> None:
        """Ensure another non-deleted experience does not use the slug."""

        slug_exists = await self.repository.slug_exists(
            session,
            slug,
            exclude_experience_id=exclude_experience_id,
        )

        if slug_exists:
            raise ExperienceConflictError(
                "A portfolio experience with this slug already exists.",
            )

    @staticmethod
    def _validate_lifecycle_data(
        *,
        start_date: date,
        end_date: date | None,
        is_current: bool,
        is_public: bool,
        is_featured: bool,
    ) -> None:
        """Validate the complete resulting experience lifecycle."""

        if end_date is not None and end_date < start_date:
            raise ExperienceLifecycleError(
                "Experience end date cannot be before its start date.",
            )

        if is_current and end_date is not None:
            raise ExperienceLifecycleError(
                "A current experience cannot include an end date.",
            )

        if is_featured and not is_public:
            raise ExperienceLifecycleError(
                "Only public experiences can be featured.",
            )

    @staticmethod
    def _normalize_single_line_text(
        value: str,
    ) -> str:
        """Normalize whitespace in required single-line text."""

        return " ".join(
            value.split(),
        )

    @staticmethod
    def _normalize_slug(
        value: str,
    ) -> str:
        """Normalize an experience slug."""

        return value.strip().lower()

    @staticmethod
    def _normalize_value(
        value: str,
    ) -> str:
        """Normalize a required lowercase value."""

        return value.strip().lower()

    @staticmethod
    def _normalize_optional_value(
        value: str | None,
    ) -> str | None:
        """Normalize an optional lowercase value."""

        if value is None:
            return None

        normalized_value = value.strip().lower()

        return normalized_value or None

    @staticmethod
    def _normalize_optional_text(
        value: str | None,
    ) -> str | None:
        """Normalize an optional search value."""

        if value is None:
            return None

        normalized_value = value.strip()

        return normalized_value or None

    @staticmethod
    def _coerce_date(
        value: object,
    ) -> date:
        """Convert a supported date value to ``date``."""

        if isinstance(
            value,
            date,
        ):
            return value

        return date.fromisoformat(
            str(value),
        )

    @staticmethod
    def _coerce_optional_date(
        value: object,
    ) -> date | None:
        """Convert an optional supported date value to ``date``."""

        if value is None:
            return None

        return ExperienceService._coerce_date(
            value,
        )


experience_service = ExperienceService(
    experience_repository,
)
