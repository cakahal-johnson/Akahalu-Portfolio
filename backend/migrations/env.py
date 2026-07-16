import asyncio
import selectors
import sys
from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.db.model_registry import Base


config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.database_url.replace("%", "%%"),
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    database_url = config.get_main_option(
        "sqlalchemy.url",
    )

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_sync_migrations(
    connection: Connection,
) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration: dict[str, Any] = config.get_section(
        config.config_ini_section,
        {},
    )

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(
                run_sync_migrations,
            )
    finally:
        await connectable.dispose()


def create_windows_selector_loop() -> asyncio.AbstractEventLoop:
    return asyncio.SelectorEventLoop(
        selectors.SelectSelector(),
    )


def run_migrations_online() -> None:
    if sys.platform == "win32":
        with asyncio.Runner(
            loop_factory=create_windows_selector_loop,
        ) as runner:
            runner.run(run_async_migrations())

        return

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
