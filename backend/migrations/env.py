import asyncio
import logging
from logging.config import fileConfig
import os

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# 動的にモデルをインポート
# 直接インポートで循環参照を回避
try:
    from models import Base

    target_metadata = Base.metadata
except ImportError:
    # フォールバック: target_metadataをNoneに設定
    target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_url():
    """環境変数からDATABASE_URLを取得"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # フォールバック: SQLite（開発時）
        database_url = "sqlite+aiosqlite:///./app.db"
        logging.warning("DATABASE_URL not found, using SQLite fallback")

    logging.info(f"Using database URL: {database_url.split('@')[0]}@***")
    return database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    database_url = get_database_url()

    # SQLiteの場合は同期エンジンを使用
    if database_url.startswith("sqlite"):
        from sqlalchemy import create_engine

        engine = create_engine(database_url.replace("+aiosqlite", ""))

        with engine.connect() as connection:
            do_run_migrations(connection)
    else:
        # PostgreSQLの場合は非同期エンジンを使用
        configuration = config.get_section(config.config_ini_section, {})
        configuration["sqlalchemy.url"] = database_url

        connectable = async_engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
