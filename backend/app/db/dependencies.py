from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    Provide a request-scoped database session.

    Successful requests commit their transaction automatically.
    Exceptions roll the transaction back before the session closes.
    """

    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
