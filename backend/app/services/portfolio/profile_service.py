from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.repositories.portfolio.profile_repository import (
    ProfileRepository,
    profile_repository,
)
from app.schemas.portfolio.profile import (
    ProfileCreate,
    ProfileUpdate,
)


class ProfileNotFoundError(Exception):
    """Raised when the portfolio profile does not exist."""


class ProfileAlreadyExistsError(Exception):
    """Raised when an active portfolio profile already exists."""


class ProfileDeletedError(Exception):
    """
    Raised when the singleton profile exists but is soft-deleted.

    Deleted profiles must be restored rather than recreated.
    """


class ProfileValidationError(Exception):
    """Raised when profile data violates a business rule."""


class ProfileService:
    """Coordinate the singleton portfolio-profile lifecycle."""

    _required_fields = frozenset(
        {
            "first_name",
            "last_name",
            "display_name",
            "professional_title",
            "headline",
            "short_bio",
            "biography",
            "primary_email",
        }
    )

    def __init__(
        self,
        repository: ProfileRepository,
    ) -> None:
        self.repository = repository

    async def get_public(
        self,
        session: AsyncSession,
    ) -> Profile:
        """Return the publicly visible profile."""

        profile = await self.repository.get_public(
            session,
        )

        if profile is None:
            raise ProfileNotFoundError(
                "A public portfolio profile was not found.",
            )

        return profile

    async def get_admin(
        self,
        session: AsyncSession,
        *,
        include_deleted: bool = False,
    ) -> Profile:
        """Return the profile for administrative management."""

        if include_deleted:
            profile = await self.repository.get_any(
                session,
            )
        else:
            profile = await self.repository.get_active(
                session,
            )

        if profile is None:
            deleted_profile = await self.repository.get_deleted(
                session,
            )

            if deleted_profile is not None:
                raise ProfileDeletedError(
                    "The portfolio profile is deleted and must be restored.",
                )

            raise ProfileNotFoundError(
                "The portfolio profile was not found.",
            )

        return profile

    async def create(
        self,
        session: AsyncSession,
        payload: ProfileCreate,
        *,
        actor_user_id: UUID | None = None,
    ) -> Profile:
        """
        Create the singleton portfolio profile.

        The service flushes changes but does not commit the transaction.
        Transaction commit remains the responsibility of the API or
        unit-of-work boundary.
        """

        existing_profile = await self.repository.get_any(
            session,
        )

        if existing_profile is not None:
            if existing_profile.deleted_at is not None:
                raise ProfileDeletedError(
                    (
                        "A deleted portfolio profile already exists. "
                        "Restore the existing profile instead of creating "
                        "a new one."
                    ),
                )

            raise ProfileAlreadyExistsError(
                "A portfolio profile already exists.",
            )

        data = payload.model_dump(
            mode="json",
        )

        self._normalize_profile_data(
            data,
        )

        data["profile_key"] = "primary"

        if actor_user_id is not None:
            data["created_by_id"] = actor_user_id
            data["updated_by_id"] = actor_user_id

        profile = Profile(
            **data,
        )

        return await self.repository.add(
            session,
            profile,
        )

    async def update(
        self,
        session: AsyncSession,
        payload: ProfileUpdate,
        *,
        actor_user_id: UUID | None = None,
    ) -> Profile:
        """
        Update and flush the active portfolio profile.

        Fields explicitly supplied as ``null`` can clear nullable profile
        values. Required fields cannot be cleared.
        """

        profile = await self.get_admin(
            session,
        )

        data = payload.model_dump(
            mode="json",
            exclude_unset=True,
        )

        self._validate_required_fields(
            data,
        )

        self._normalize_profile_data(
            data,
        )

        if actor_user_id is not None:
            data["updated_by_id"] = actor_user_id

        for field_name, value in data.items():
            setattr(
                profile,
                field_name,
                value,
            )

        await session.flush()
        await session.refresh(
            profile,
        )

        return profile

    async def set_visibility(
        self,
        session: AsyncSession,
        *,
        is_public: bool,
        actor_user_id: UUID | None = None,
    ) -> Profile:
        """Set whether the active profile is publicly accessible."""

        profile = await self.get_admin(
            session,
        )

        profile.is_public = is_public

        if actor_user_id is not None:
            profile.updated_by_id = actor_user_id

        await session.flush()
        await session.refresh(
            profile,
        )

        return profile

    async def soft_delete(
        self,
        session: AsyncSession,
        *,
        actor_user_id: UUID | None = None,
    ) -> Profile:
        """
        Soft-delete the active portfolio profile.

        Deletion also disables public visibility.
        """

        profile = await self.get_admin(
            session,
        )

        profile.is_public = False

        if actor_user_id is not None:
            profile.updated_by_id = actor_user_id

        profile.soft_delete()

        await session.flush()
        await session.refresh(
            profile,
        )

        return profile

    async def restore(
        self,
        session: AsyncSession,
        *,
        restore_as_public: bool = False,
        actor_user_id: UUID | None = None,
    ) -> Profile:
        """Restore the soft-deleted singleton profile."""

        profile = await self.repository.get_deleted(
            session,
        )

        if profile is None:
            active_profile = await self.repository.get_active(
                session,
            )

            if active_profile is not None:
                return active_profile

            raise ProfileNotFoundError(
                "A deleted portfolio profile was not found.",
            )

        profile.restore()
        profile.is_public = restore_as_public

        if actor_user_id is not None:
            profile.updated_by_id = actor_user_id

        await session.flush()
        await session.refresh(
            profile,
        )

        return profile

    @classmethod
    def _validate_required_fields(
        cls,
        data: dict[str, object],
    ) -> None:
        """Prevent required profile fields from being explicitly cleared."""

        cleared_fields = sorted(
            field_name
            for field_name in cls._required_fields
            if field_name in data and data[field_name] is None
        )

        if not cleared_fields:
            return

        joined_fields = ", ".join(
            cleared_fields,
        )

        raise ProfileValidationError(
            f"Required profile fields cannot be cleared: {joined_fields}.",
        )

    @staticmethod
    def _normalize_profile_data(
        data: dict[str, object],
    ) -> None:
        """Apply service-level normalization to serialized profile data."""

        primary_email = data.get(
            "primary_email",
        )

        if isinstance(
            primary_email,
            str,
        ):
            data["primary_email"] = primary_email.strip().lower()

        availability_status = data.get(
            "availability_status",
        )

        if isinstance(
            availability_status,
            str,
        ):
            data["availability_status"] = availability_status.strip().lower()


profile_service = ProfileService(
    profile_repository,
)
