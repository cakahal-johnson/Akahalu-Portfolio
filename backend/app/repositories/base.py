from collections.abc import Sequence
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import BaseModel


ModelType = TypeVar(
    "ModelType",
    bound=BaseModel,
)


class BaseRepository(Generic[ModelType]):
    def __init__(
        self,
        model: type[ModelType],
    ) -> None:
        self.model = model

    async def get_by_id(
        self,
        session: AsyncSession,
        object_id: UUID,
    ) -> ModelType | None:
        statement = select(self.model).where(
            self.model.id == object_id,
            self.model.deleted_at.is_(None),
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def list_active(
        self,
        session: AsyncSession,
    ) -> Sequence[ModelType]:
        statement = (
            select(self.model)
            .where(self.model.deleted_at.is_(None))
            .order_by(self.model.created_at.asc())
        )

        result = await session.execute(statement)

        return result.scalars().all()

    async def add(
        self,
        session: AsyncSession,
        instance: ModelType,
    ) -> ModelType:
        session.add(instance)
        await session.flush()
        await session.refresh(instance)

        return instance
