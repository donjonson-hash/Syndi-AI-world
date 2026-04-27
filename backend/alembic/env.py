"""
Alembic async env.py
Поддерживает SQLite (dev) и PostgreSQL (prod) через DATABASE_URL.
"""
import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Добавляем backend/ в sys.path чтобы импортировать модели
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import (  # noqa: E402  — импорт после sys.path
    Base,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic будет сравнивать БД именно с этой метадатой
target_metadata = Base.metadata

# Берём URL из env или из alembic.ini
DATABASE_URL = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}


def run_migrations_offline() -> None:
    """Offline mode: генерирует SQL без подключения к БД."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,      # ← ОБЯЗАТЕЛЬНО для SQLite ALTER TABLE
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,      # ← ОБЯЗАТЕЛЬНО для SQLite ALTER TABLE
        compare_type=True,         # детектировать изменения типов колонок
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(DATABASE_URL, connect_args=connect_args)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
