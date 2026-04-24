# Syndi AI — Состояние проекта
**Дата**: 24 апреля 2026, 12:15 MSK  
**HEAD**: `1960c1a5f1fcdd59b161b9df93bd5fd1c2f1514d`  
**Тег**: `v0.2.0-phase2`  
**Тестов**: 219 ✅  
**Репо**: https://github.com/donjonson-hash/Syndi-AI-world  
**Репо аватара**: https://github.com/donjonson-hash/kristina-revolutionary (приватный)

---

## Локальная среда
- **Путь**: `~/Рабочий стол/Syndi-AI-world/backend`
- **Python**: 3.12, venv: `backend/venv`
- **БД**: SQLite `backend/startup_matcher.db`, alembic_version=0006
- **Порт**: 8081 (локально)
- **Env**: `backend/.env` (MIMO_API_KEY задан)

### Команды запуска
```bash
cd ~/Рабочий\ стол/Syndi-AI-world/backend
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8081 --reload
```

### Тесты
```bash
pytest tests/ --ignore=tests/test_agents.py -q
```

### Миграции
```bash
alembic upgrade head
```

### Git sync
```bash
cd ~/Рабочий\ стол/Syndi-AI-world
git pull
```

---

## Фаза 0 — Foundation ✅ (54 теста)

| Блок | Коммит | Тесты |
|------|--------|-------|
| B1: SQLite + Alembic | `4292e32f` | 15/15 |
| C1: Cleanup | `24ac16f5` | — |
| C2: Like/Match | `935c3066` | 18/18 |
| C3: Discover | `73aa0801` | 13/13 |
| C4: Auth JWT | `08bca37e` | 8/8 |

---

## Фаза 1 — Core MVP ✅ (115 тестов)

| Блок | Коммит | Тесты |
|------|--------|-------|
| C5: JWT защита эндпоинтов | `c7bab129` | 8 |
| C6: Профиль пользователя | `aa587120` | 7 |
| C7: Kristina AI-агент | `4749437d` | 8 |
| Mimo API | `75a70835` | — |
| C8: Mystic Engine (MBTI/энеаграмма) | `75a70835` | 12 |
| fix: StaticFiles абсолютный путь | `a5a5053b` | — |
| docs: ROADMAP.md | `efbfed58` | — |

---

## Фаза 2 — AI Avatar Team ✅ (219 тестов total)

| Блок | Коммит | +Тестов |
|------|--------|---------|
| D1: ProfessionProfile (4 роли) | `09175a9f` | +6 |
| D2: EmotionalCore (mood engine) | `7af050f7` | +7 |
| D3: AgentRouter (advisor/mentor/executor) | `c8667500` | +7 |
| D4: AvatarFactory при матче | `f941ba88` | +10 |
| D7: PostgreSQL + Redis | `e38d43bb` | +7 |
| D5: Трёхуровневая память | `1960c1a5` | +13 |

---

## Эндпоинты (полный список)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| POST | /onboarding | Онбординг | — |
| POST | /api/v1/onboarding/raw | Raw онбординг | — |
| GET | /match/{user_id} | Матч-кандидаты | — |
| POST | /api/v1/auth/register | Регистрация | — |
| POST | /api/v1/auth/login | Логин → JWT | — |
| GET | /api/v1/auth/me | Текущий юзер | ✅ |
| POST | /api/v1/like/{to_user_id} | Лайк/дизлайк | ✅ |
| GET | /api/v1/matches | Список матчей | ✅ |
| GET | /api/v1/discover | Лента кандидатов | ✅ |
| GET | /api/v1/profile/me | Профиль + профессия | ✅ |
| PATCH | /api/v1/profile/me | Обновить профиль | ✅ |
| POST | /api/v1/kristina/chat | Чат с Kristina | ✅ |
| GET | /api/v1/kristina/status | Статус агента | — |
| GET | /api/v1/kristina/history | История диалога | ✅ |
| GET | /api/v1/avatar/me | Мой AI-аватар | ✅ |
| GET | /api/v1/avatar/list | Все аватары | ✅ |

---

## БД — таблицы (alembic_version=0006)

| Таблица | Описание |
|---------|----------|
| users | Пользователи (email, hashed_password) |
| founder_profiles | Профили фаундеров (mbti_type, enneagram_type) |
| match_candidates | Кандидаты на матч |
| trials | Испытания |
| trial_tasks | Задачи испытания |
| trial_events | События испытания |
| likes | Лайки/дизлайки |
| matches | Матчи (user_a_id, user_b_id, score) |
| avatar_memories | Память аватаров (dialog/semantic/persistent) |
| alembic_version | Версия миграций |

---

## avatar_platform/ — структура

```
backend/avatar_platform/
├── __init__.py
├── profession_profile.py   # ProfessionProfile + PROFESSION_REGISTRY (4 роли)
├── emotional_core.py       # EmotionalCore (Big5 + 6 эмоций + суточный ритм)
├── agent_router.py         # AgentRouter (advisor/mentor/executor)
├── avatar_factory.py       # AvatarFactory + AvatarInstance
└── memory/
    ├── __init__.py
    ├── dialog_memory.py     # In-memory буфер (20 сообщений)
    ├── semantic_memory.py   # Факты о пользователе (SQLite JSON)
    ├── persistent_memory.py # Долгосрочная история (SQLAlchemy async)
    └── memory_manager.py    # Фасад для всех трёх уровней
```

---

## Стек

| Компонент | Технология |
|-----------|-----------|
| Backend | FastAPI + Uvicorn |
| ORM | SQLAlchemy async |
| Миграции | Alembic |
| БД dev | SQLite (aiosqlite) |
| БД prod | PostgreSQL 16 (asyncpg) |
| Кэш | Redis 7 (graceful degradation) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| LLM | Mimo API (AsyncOpenAI клиент) |
| Тесты | pytest-asyncio, httpx AsyncClient |
| Контейнеры | Docker + docker-compose |

---

## Следующие блоки

| Блок | Описание |
|------|----------|
| D6 | Telegram-бот (уведомления, чат с аватаром) |
| E1 | Фронтенд — карточки, свайп, экран аватара |
| E2 | MessageBus — координация аватаров пары |
| E3 | Trial Period AI — аватар ведёт 3-дневное испытание |

---

## Восстановление системы

```bash
# 1. Клонировать репо
git clone https://github.com/donjonson-hash/Syndi-AI-world.git
cd Syndi-AI-world/backend

# 2. Создать venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Настроить env
cp .env.example .env
# Вписать MIMO_API_KEY=sk-sbh30f2hth9sjoih89gal1vpldeb10tszpac04xyykjrn1d1

# 4. Применить миграции
alembic upgrade head

# 5. (Опционально) Загрузить профили
python migrate_profiles.py

# 6. Запустить
uvicorn main:app --host 127.0.0.1 --port 8081 --reload

# 7. Проверить тесты
pytest tests/ --ignore=tests/test_agents.py -q
```
