from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, JSON, Integer, Float
from typing import Optional, List, Dict, Any

# Замени на свой реальный URL базы данных
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
# Для локального тестирования можно оставить заглушку или использовать SQLite:
DATABASE_URL = "sqlite+aiosqlite:///./startup_matcher.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Зависимость для получения сессии в FastAPI (когда до него дойдем)
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
