# 🚀 Syndi AI — Roadmap

> **Syndi AI** — это платформа для поиска со-фаундеров по принципу "Tinder for co-founders".
> Умный алгоритм матчинга анализирует стек, роли, цели, психотип (MBTI/энеаграмма) и стиль работы,
> чтобы соединять людей, которые реально дополняют друг друга. Backend на FastAPI, AI-агент Kristina
> ведёт пользователя через онбординг и помогает найти идеального партнёра.

---

## Легенда

| Иконка | Статус |
|--------|--------|
| ✅ | **Done** — реализовано, покрыто тестами |
| 🔄 | **In Progress** — в работе прямо сейчас |
| 🔲 | **Planned** — запланировано, чёткий скоуп |
| 💡 | **Idea / Future** — исследуется, без фиксированных сроков |

---

## Фаза 0 — Foundation ✅

> Закрыта целиком. HEAD: `08bca37e` (24 апреля 2026). Все 54 теста зелёные.

| Блок | Описание | Коммит | Тесты |
|------|----------|--------|-------|
| **B1** | SQLite + Alembic (миграции 0001–0003) | `4292e32f` | ✅ 15/15 |
| **C1** | Cleanup — `.gitignore`, `app.js`, структура репо | `24ac16f5` | — |
| **C2** | Like/Match — `POST /like`, `GET /matches` | `935c3066` | ✅ 18/18 |
| **C3** | Discover — `GET /discover`, scoring-алгоритм | `73aa0801` | ✅ 13/13 |
| **C4** | Auth JWT — register / login / me, bcrypt | `08bca37e` | ✅ 8/8 |

### Текущие эндпоинты

```
POST  /onboarding
POST  /api/v1/onboarding/raw
GET   /match/{user_id}

POST  /api/v1/like/{to_user_id}
GET   /api/v1/matches
GET   /api/v1/discover

POST  /api/v1/auth/register
POST  /api/v1/auth/login
GET   /api/v1/auth/me
```

### DB-таблицы

`users` · `founder_profiles` · `match_candidates` · `trials` · `trial_tasks` · `trial_events` · `likes` · `matches` · `alembic_version`

---

## Фаза 1 — Core MVP 🔄

> Текущая фаза · ~1 неделя · Цель: рабочий MVP с AI-агентом и закрытыми эндпоинтами

| Блок | Описание | Статус |
|------|----------|--------|
| **C5** | JWT-защита эндпоинтов — `like` / `match` / `discover` требуют Bearer-токен | 🔄 |
| **C6** | Профиль пользователя — `GET /api/v1/profile/me`, `PATCH /api/v1/profile/me` | 🔲 |
| **C7** | Kristina AI-агент — `POST /api/v1/kristina/chat` (подключить `agents/kristina_routes.py`) | 🔲 |
| **C8** | Mystic Engine — MBTI / энеаграмма в онбординге и scoring (`core/mystic/`) | 🔲 |
| **C9** | Полный тестовый прогон, покрытие >80%, CI-pipeline | 🔲 |

### Детали блоков

#### C5 — JWT Protection
- Добавить `Depends(get_current_user)` на `POST /like`, `GET /matches`, `GET /discover`
- Вернуть `401 Unauthorized` при отсутствии/невалидном токене
- Обновить OpenAPI-схему (securitySchemes: Bearer)

#### C6 — Profile
- `GET /api/v1/profile/me` — возвращает полный профиль текущего пользователя
- `PATCH /api/v1/profile/me` — частичное обновление (bio, stack, role, goals, timezone)
- Валидация через Pydantic v2

#### C7 — Kristina Agent
- Подключить `agents/kristina_routes.py` к `main.py`
- Endpoint: `POST /api/v1/kristina/chat` `{ "message": "...", "session_id": "..." }`
- Kristina использует `process_message` + `memories` для контекстного диалога
- Онбординг через чат (альтернатива форме)

#### C8 — Mystic Engine
- Интегрировать `core/mystic/` (MBTI, энеаграмма, таро, интерпретации) в `scoring`
- Добавить поля `mbti_type`, `enneagram` в `founder_profiles`
- Миграция `0004_mystic_fields`

#### C9 — Test Coverage
- Добавить тесты для C5–C8
- Настроить `pytest-cov`, порог 80%
- Базовый GitHub Actions workflow (lint + test)

---

## Фаза 2 — Product Polish 🔲

> ~2 недели · Цель: production-ready продукт, первые реальные пользователи

| Блок | Описание | Статус |
|------|----------|--------|
| **D1** | Фронтенд — улучшить UI: карточки фаундеров, свайп, экран матчей | 🔲 |
| **D2** | Telegram-бот — `syndi-bot.service`, уведомления и онбординг через Telegram | 🔲 |
| **D3** | Email-нотификации — матч, новый лайк, напоминания (SMTP / SendGrid) | 🔲 |
| **D4** | Rate limiting + anti-abuse — `slowapi` / Redis, защита от флуда лайков | 🔲 |
| **D5** | PostgreSQL migration — переход с SQLite, Alembic env для двух диалектов | 🔲 |
| **D6** | Docker production deploy — `docker-compose.prod.yml`, Nginx, SSL | 🔲 |

### Детали блоков

#### D1 — Frontend Polish
- Карточки в стиле Tinder (фото, стек, роль, цели)
- Жест-свайп или кнопки Like / Skip
- Экран "Матчи" с чатом (или ссылкой на Telegram)

#### D2 — Telegram Bot
- `/start` → онбординг через Kristina
- Уведомление при новом матче
- Команда `/discover` — показать следующую карточку

#### D3 — Notifications
- Welcome-письмо при регистрации
- "У вас новый матч!" — email + Telegram push
- Еженедельный дайджест (топ-3 совместимых фаундера)

#### D4 — Rate Limiting
- Лимит: 50 лайков / час / пользователь
- Глобальный лимит на `/api/v1/discover`
- IP-блокировка при подозрительной активности

#### D5 — PostgreSQL
- `DATABASE_URL` через env (`.env`, `docker-compose`)
- Миграция данных SQLite → PostgreSQL (скрипт `scripts/migrate_sqlite_pg.py`)
- Async driver: `asyncpg`

#### D6 — Production Deploy
- `docker-compose.prod.yml`: FastAPI + PostgreSQL + Nginx + Certbot
- Health-check endpoint `GET /health`
- Логирование в stdout (structured JSON, `structlog`)

---

## Фаза 3 — Scale & AI 💡

> ~1 месяц · Цель: масштабирование, продвинутый AI, мобильное приложение

| Блок | Описание | Статус |
|------|----------|--------|
| **E1** | Quantum Matching — IonQ-интеграция (`core/quantum/`) для оптимизации матчинга | 💡 |
| **E2** | Multi-Agent System — агенты помимо Kristina (ментор, аналитик, HR-скаут) | 💡 |
| **E3** | Recommendation Engine — ML на истории лайков (collaborative filtering) | 💡 |
| **E4** | Mobile API — оптимизированный REST + WebSocket для iOS/Android-клиента | 💡 |
| **E5** | Аналитика и дашборд — метрики фаундера: конверсия, средний скор совместимости | 💡 |

### Детали блоков

#### E1 — Quantum Matching
- `core/quantum/generator.py` — генерация квантовых состояний для профилей
- `core/quantum/ionq_integration.py` — запросы к IonQ Quantum Cloud
- Quantum annealing для глобальной оптимизации пар (замена жадного scoring)

#### E2 — Multi-Agent System
- **Alex** — ментор по продукту, советует по стратегии
- **Dana** — HR-скаут, помогает оценить soft skills
- Оркестрация через `agents/orchestrator.py`
- Память агентов — векторная БД (pgvector / Qdrant)

#### E3 — Recommendation Engine
- Сбор implicit feedback (лайк, скип, время просмотра карточки)
- Matrix Factorization / LightFM на истории взаимодействий
- A/B-тест: классический scoring vs ML-рекомендации

#### E4 — Mobile API
- Версионирование: `/api/v2/`
- WebSocket-чат в матчах (`ws://host/api/v2/chat/{match_id}`)
- Push-уведомления (APNs / FCM)

#### E5 — Analytics Dashboard
- Личный дашборд: сколько лайков дал / получил, процент матчей
- Для команды: воронка онбординга, MAU, retention
- Экспорт в CSV / Metabase

---

## Архитектура — текущее состояние

```
┌─────────────────────────────────────────────────────────────┐
│                        Клиент                               │
│              (Browser SPA / Telegram Bot)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP / WebSocket
┌───────────────────────▼─────────────────────────────────────┐
│                    FastAPI App                               │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │  Auth    │  │ Profile  │  │  Match   │  │ Kristina  │  │
│  │  routes  │  │  routes  │  │  routes  │  │  Agent    │  │
│  │ /auth/*  │  │/profile/*│  │/like     │  │/kristina/ │  │
│  │          │  │          │  │/matches  │  │  chat     │  │
│  │          │  │          │  │/discover │  │           │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬─────┘  │
│       │              │             │               │        │
│  ┌────▼──────────────▼─────────────▼───────────────▼─────┐ │
│  │                   Core Services                        │ │
│  │  ┌────────────┐  ┌───────────┐  ┌──────────────────┐  │ │
│  │  │ JWT / Auth │  │ Matching  │  │   Mystic Engine  │  │ │
│  │  │  (bcrypt)  │  │  Engine   │  │ MBTI/Enneagram   │  │ │
│  │  └────────────┘  └───────────┘  └──────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                │
│  ┌─────────────────────────▼──────────────────────────────┐ │
│  │              SQLAlchemy Async ORM                       │ │
│  └─────────────────────────┬──────────────────────────────┘ │
└────────────────────────────┼────────────────────────────────┘
                             │
           ┌─────────────────▼─────────────────┐
           │      SQLite (dev)                  │
           │      PostgreSQL (prod, фаза D5)    │
           │      + Alembic migrations          │
           └───────────────────────────────────┘

Будущее (фаза E):
           ┌───────────────────────────────────┐
           │   IonQ Quantum Cloud (E1)          │
           │   Vector DB — pgvector/Qdrant (E2) │
           └───────────────────────────────────┘
```

### Слои приложения

| Слой | Папка | Назначение |
|------|-------|------------|
| Routes | `api/v1/` | HTTP-эндпоинты, валидация запросов |
| Agents | `agents/` | AI-агенты (Kristina + будущие) |
| Core | `core/` | Бизнес-логика: matching, mystic, quantum, ai |
| Services | `services/` | LLM-клиент, внешние интеграции |
| Models | `models/` | SQLAlchemy ORM-модели |
| Schemas | `schemas/` | Pydantic v2 схемы |
| Migrations | `alembic/versions/` | Alembic-миграции 0001→... |

---

## Команды для разработки

### Запуск

```bash
# Локально (dev)
make dev
# или
uvicorn app.main:app --reload --port 8000

# Docker (compose)
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### Тесты

```bash
# Все тесты
make test
# или
pytest -v

# С покрытием
pytest --cov=app --cov-report=term-missing --cov-fail-under=80

# Конкретный модуль
pytest tests/test_auth.py -v
```

### Миграции (Alembic)

```bash
# Применить все миграции
alembic upgrade head

# Создать новую миграцию
alembic revision --autogenerate -m "add_mystic_fields"

# Откатить последнюю
alembic downgrade -1

# Статус
alembic current
alembic history --verbose
```

### Утилиты

```bash
# Линтер + форматирование
make lint        # ruff check .
make format      # ruff format .

# Открыть Swagger UI
open http://localhost:8000/docs

# Открыть ReDoc
open http://localhost:8000/redoc
```

---

## Стек

| Компонент | Технология |
|-----------|------------|
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) 0.110+ |
| **ORM** | SQLAlchemy 2.x (async) |
| **Migrations** | Alembic |
| **DB (dev)** | SQLite via `aiosqlite` |
| **DB (prod)** | PostgreSQL via `asyncpg` |
| **Auth** | JWT (`python-jose`) + bcrypt (`passlib`) |
| **AI / LLM** | OpenAI API / совместимые (`core/ai/llm.py`) |
| **Personality** | MBTI, Enneagram, Tarot (`core/mystic/`) |
| **Quantum** | IonQ SDK (`core/quantum/`) — future |
| **Testing** | `pytest` + `pytest-asyncio` + `httpx` |
| **Coverage** | `pytest-cov` |
| **Linting** | `ruff` |
| **Containers** | Docker + Docker Compose |
| **CI** | GitHub Actions (planned, C9) |

---

*Последнее обновление: 24 апреля 2026 · HEAD `08bca37e`*
