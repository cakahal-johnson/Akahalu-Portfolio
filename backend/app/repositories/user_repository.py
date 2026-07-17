from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(
    BaseRepository[User],
):
    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:
        statement = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(
                    Role.permissions,
                ),
            )
            .where(
                User.email == email,
                User.deleted_at.is_(None),
            )
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()


user_repository = UserRepository()
