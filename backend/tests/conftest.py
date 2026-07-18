import asyncio
import sys
from collections.abc import AsyncIterator, Iterator

from sqlalchemy import text
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db import model_registry as _model_registry  # noqa: F401
from app.db.base import Base
from app.db.dependencies import get_db_session
from app.main import app as application


@pytest.fixture(scope="session")
def event_loop_policy() -> asyncio.AbstractEventLoopPolicy:
    if sys.platform == "win32":
        return asyncio.WindowsSelectorEventLoopPolicy()

    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="session")
def test_database_url() -> str:
    database_url = settings.test_database_url

    if not database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL must be configured before running "
            "database integration tests."
        )

    parsed_url = make_url(database_url)

    if parsed_url.database != "portfolio_test_db":
        raise RuntimeError(
            "TEST_DATABASE_URL must point to portfolio_test_db. "
            f"Received database: {parsed_url.database!r}."
        )

    if parsed_url.username != "portfolio_user":
        raise RuntimeError("TEST_DATABASE_URL must use the portfolio_user role.")

    password = parsed_url.password or ""

    invalid_password_values = {
        "",
        "YOUR_DATABASE_PASSWORD",
        "****************",
        "********",
    }

    if password in invalid_password_values:
        raise RuntimeError(
            "TEST_DATABASE_URL contains a missing, masked, or placeholder password."
        )

    return database_url


@pytest_asyncio.fixture(
    scope="session",
    loop_scope="session",
)
async def test_engine(
    test_database_url: str,
) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        test_database_url,
        pool_pre_ping=True,
        poolclass=NullPool,
    )

    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            text("CREATE EXTENSION IF NOT EXISTS citext")
            await connection.run_sync(Base.metadata.create_all)

        yield engine
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)

        await engine.dispose()


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
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
