"""
init_db.py — Инициализация БД и seed-данные.

Запуск (из backend/):
    source venv/bin/activate
    python init_db.py

Порядок действий:
  1. alembic upgrade head  — применяет все миграции
  2. Seed: создаёт тестовые профили основателей в founder_profiles
  3. Выводит статус

Для полноценного переноса данных запусти migrate_profiles.py.
"""
import asyncio
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database.database import engine, init_db as _create_tables
from migrate_profiles import seed_profiles, verify


async def apply_migrations():
    """Запускает alembic upgrade head."""
    print("Applying migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"✓ {result.stdout.strip() or 'up to date'}")
    else:
        print(f"⚠  alembic: {result.stderr.strip()}")
        # Fallback: создаём таблицы напрямую через SQLAlchemy
        print("  → fallback: create_all via SQLAlchemy")
        await _create_tables()


async def main():
    print("🚀 Syndi AI — DB initialization")
    print("=" * 50)
    await apply_migrations()
    await seed_profiles()
    await verify()
    await engine.dispose()
    print("\n✅ Done — startup_matcher.db is ready")


if __name__ == "__main__":
    asyncio.run(main())
