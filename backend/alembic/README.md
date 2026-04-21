# Alembic — SyndiAI Migrations

## Быстрый старт

```bash
cd backend/

# Установить зависимости (если не установлены)
pip install alembic sqlalchemy aiosqlite asyncpg

# Применить все миграции (SQLite по умолчанию, данные сохраняются)
alembic upgrade head

# Проверить статус
alembic current
alembic history
```

## PostgreSQL

```bash
export DATABASE_URL="postgresql+asyncpg://user:password@localhost/syndiai_db"
alembic upgrade head
```

## Откат последней миграции

```bash
alembic downgrade -1
# или полный откат:
alembic downgrade base
```

## Что делает миграция 0001

| Действие | Таблица | Безопасно? |
|---|---|---|
| ADD COLUMN (nullable) | `users` | ✅ старые строки не меняются |
| CREATE TABLE | `founder_profiles` | ✅ новая |
| CREATE TABLE | `match_candidates` | ✅ новая |
| CREATE TABLE | `trials` | ✅ новая |
| CREATE TABLE | `trial_tasks` | ✅ новая |
| CREATE TABLE | `trial_events` | ✅ новая |

## Создать новую миграцию

```bash
alembic revision --autogenerate -m "describe_your_change"
```
