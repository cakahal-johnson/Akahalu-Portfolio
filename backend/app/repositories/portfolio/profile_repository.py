from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.repositories.base import BaseRepository


class ProfileRepository(
    BaseRepository[Profile],
):
    """
    Database operations for the singleton portfolio profile.

    The profile table is restricted to one record through the fixed,
    unique ``profile_key`` value. Repository methods therefore return
    either one profile or no profile.
    """

    def __init__(self) -> None:
        super().__init__(Profile)

    async def get_active(
        self,
        session: AsyncSession,
    ) -> Profile | None:
        """Return the active profile, excluding soft-deleted records."""

        statement = select(Profile).where(
            Profile.profile_key == "primary",
            Profile.deleted_at.is_(None),
        )

        result = await session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_public(
        self,
        session: AsyncSession,
    ) -> Profile | None:
        """Return the active profile only when publicly visible."""

        statement = select(Profile).where(
            Profile.profile_key == "primary",
            Profile.is_public.is_(True),
            Profile.deleted_at.is_(None),
        )

        result = await session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_deleted(
        self,
        session: AsyncSession,
    ) -> Profile | None:
        """Return the soft-deleted singleton profile."""

        statement = select(Profile).where(
            Profile.profile_key == "primary",
            Profile.deleted_at.is_not(None),
        )

        result = await session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_any(
        self,
        session: AsyncSession,
    ) -> Profile | None:
        """
        Return the singleton profile regardless of deletion state.

        This method is used when enforcing the permanent singleton rule.
        A soft-deleted profile must be restored rather than recreated.
        """

        statement = select(Profile).where(
            Profile.profile_key == "primary",
        )

        result = await session.execute(
            statement,
        )

        return result.scalar_one_or_none()


profile_repository = ProfileRepository()
