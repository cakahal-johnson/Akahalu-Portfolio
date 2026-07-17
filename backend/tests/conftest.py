from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from app.core.config import settings
from app.db import model_registry as _model_registry  # noqa: F401
from app.db.base import Base
from app.db.dependencies import get_db_session
from app.main import app as application


@pytest.fixture(scope="session")
def test_database_url() -> str:
    database_url = settings.test_database_url

    if not database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL must be configured before running "
            "database integration tests."
        )

    if "test" not in database_url.lower():
        raise RuntimeError("TEST_DATABASE_URL must point to a dedicated test database.")

    return database_url


@pytest.fixture(scope="session")
async def test_engine(
    test_database_url: str,
) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        test_database_url,
        pool_pre_ping=True,
    )

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.drop_all,
        )
        await connection.run_sync(
            Base.metadata.create_all,
        )

    try:
        yield engine
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(
                Base.metadata.drop_all,
            )

        await engine.dispose()


@pytest.fixture
async def database_connection(
    test_engine: AsyncEngine,
) -> AsyncIterator[AsyncConnection]:
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        try:
            yield connection
        finally:
            if transaction.is_active:
                await transaction.rollback()


@pytest.fixture
async def database_session(
    database_connection: AsyncConnection,
) -> AsyncIterator[AsyncSession]:
    session = AsyncSession(
        bind=database_connection,
        autoflush=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        await session.close()


@pytest.fixture
def app(
    database_session: AsyncSession,
) -> Iterator[FastAPI]:
    async def override_database_session() -> AsyncIterator[AsyncSession]:
        yield database_session

    application.dependency_overrides[get_db_session] = override_database_session

    try:
        yield application
    finally:
        application.dependency_overrides.clear()


@pytest.fixture
async def client(
    app: FastAPI,
) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(
        app=app,
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as async_client:
        yield async_client
