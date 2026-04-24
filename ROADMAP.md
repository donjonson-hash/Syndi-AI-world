# 🚀 Syndi AI — ROADMAP

> **Syndi** — платформа, где каждая команда со-фаундеров получает живую AI-команду.  
> Мы не просто матчим людей — после матча каждый фаундер получает персонального AI-аватара по своей роли,  
> который помогает строить продукт, держать ритм и синхронизировать партнёров.

---

## 📖 Легенда

| Символ | Значение |
|--------|----------|
| ✅ | Завершено |
| 🔄 | В процессе |
| 🔲 | Запланировано |
| 💡 | Идея / будущее |

---

## Фаза 0 — Foundation ✅

> База данных, миграции, базовые механики. **54 теста.**

| Блок | Описание | Коммит | Тесты |
|------|----------|--------|-------|
| B1 | SQLite + Alembic (миграции 0001–0004) | `4292e32f` | — |
| C1 | Cleanup | `24ac16f5` | — |
| C2 | Like / Match | `935c3066` | 18/18 |
| C3 | Discover | `73aa0801` | 13/13 |
| C4 | Auth JWT | `08bca37e` | 8/8 |

---

## Фаза 1 — Core MVP ✅

> Авторизация, профили, AI-агент Kristina, движок совместимости. **169 тестов, всё зелёное.**

| Блок | Описание | Коммит | Тесты |
|------|----------|--------|-------|
| C5 | JWT-защита эндпоинтов | `c7bab129` | 8/8 |
| C6 | Профиль пользователя GET/PATCH | `aa587120` | 7/7 |
| C7 | Kristina AI-агент (chat / history / status) | `4749437d` | 8/8 |
| Mimo | AsyncOpenAI-клиент для Kristina | `75a70835` | — |
| C8 | Mystic Engine (MBTI / энеаграмма в scoring) | `75a70835` | 12/12 |

### Эндпоинты

| Метод | Путь |
|-------|------|
| POST | `/onboarding`, `/api/v1/onboarding/raw` |
| GET | `/match/{user_id}` |
| POST | `/api/v1/like/{to_user_id}` |
| GET | `/api/v1/matches` |
| GET | `/api/v1/discover` |
| POST | `/api/v1/auth/register`, `/api/v1/auth/login` |
| GET | `/api/v1/auth/me` |
| GET/PATCH | `/api/v1/profile/me` |
| POST | `/api/v1/kristina/chat` |
| GET | `/api/v1/kristina/status`, `/api/v1/kristina/history` |

### Таблицы БД

`users` · `founder_profiles` (+ `mbti_type`, `enneagram_type`) · `match_candidates` · `trials` · `trial_tasks` · `trial_events` · `likes` · `matches` · `alembic_version`

---

## Фаза 2 — AI Avatar Team 🔄

> **Главная идея:** когда два со-фаундера матчатся, каждый получает персонального AI-аватара под свою роль.  
> Аватар знает твой контекст, помнит историю и действует как напарник — от code review до customer discovery.  
> Технологическая база — проект **kristina-revolutionary** (`github.com/donjonson-hash/kristina-revolutionary`).

### Маппинг ролей

| Роль фаундера | ProfessionProfile | Что делает аватар |
|---------------|-------------------|-------------------|
| `builder` | `backend_dev` | Code review, архитектура, tech debt alerts |
| `seller` | `pm` | OKR трекинг, приоритизация, customer discovery |
| `operator` | `devops` + `pm` | CI/CD, процессы, метрики, risk management |
| `researcher` | `ux_designer` | User research, прототипы, CJM |

### Блоки фазы

| Блок | Описание | Источник | Сложность | Статус |
|------|----------|----------|-----------|--------|
| D1 | `ProfessionProfile` + `PROFESSION_REGISTRY` (6 ролей: builder / seller / operator / researcher / devops / qa) | `avatar_platform/profession_profile.py` | S | 🔲 |
| D2 | `EmotionalCore` — аватар меняет состояние (`energy`, `happiness`, `curiosity`) через `evolve()` | `emotional_core.py` | S | 🔲 |
| D3 | `AgentRouter` — три режима Kristina: советник / ментор / исполнитель | `agents/router.py` | M | 🔲 |
| D4 | `AvatarFactory` — создание аватара при матче | `avatar_platform/` | M | 🔲 |
| D5 | Трёхуровневая память (semantic + dialog + persistent) | `semantic_memory.py` | L | 🔲 |
| D6 | Telegram-бот — уведомления, чат с аватаром | `bot.py` | M | 🔲 |
| D7 | PostgreSQL + Redis migration | `migrate_to_postgres.py` | M | 🔲 |

**Порядок реализации:** D1 → D2 → D3 → D4 → D7 → D5 → D6

---

## Фаза 3 — Product Polish 🔲

> Фронтенд, координация аватаров, проактивный AI, продакшн.

| Блок | Описание |
|------|----------|
| E1 | Фронтенд — карточки, свайп, экран матчей + аватара |
| E2 | `MessageBus` — координация аватаров двух со-фаундеров |
| E3 | Trial Period AI — аватар ведёт 3-дневное испытание пары |
| E4 | Проактивные сообщения ("Вы не общались 2 дня — стоит синхронизироваться") |
| E5 | Docker production deploy (`docker-compose.prod.yml` уже есть) |

---

## Фаза 4 — Scale & AI 💡

> Квантовый матчинг, мультиагентность, мобайл.

| Блок | Описание |
|------|----------|
| F1 | Quantum Matching (IonQ — `core/quantum/` уже есть) |
| F2 | Multi-agent system (несколько агентов помимо Kristina) |
| F3 | ML Recommendation Engine |
| F4 | Mobile API (WebSocket чат) |
| F5 | Аналитика и дашборд |

---

## 🏗️ Архитектура — AI Avatar Team

```
Founder A (builder) ──матч──► AvatarFactory ──► Avatar A (backend_dev)
                                                       │ EmotionalCore
                                                       │ AgentRouter
                                                       │ TaskManager
                                                       ▼
                                                MessageBus ◄──────────────┐
                                                       ▲                   │
Founder B (seller) ──матч──► AvatarFactory ──► Avatar B (pm)              │
                                                       │ EmotionalCore     │
                                                       │ AgentRouter       │
                                                       └───────────────────┘
                               Shared Memory: semantic + dialog + persistent
                               PostgreSQL + Redis
```

---

## 💻 Команды для разработки

```bash
# Активация venv
cd ~/Рабочий\ стол/Syndi-AI-world/backend
source venv/bin/activate

# Запуск сервера
uvicorn main:app --host 127.0.0.1 --port 8081 --reload

# Тесты (из backend/)
pytest tests/ --ignore=tests/test_agents.py -q

# Миграции
alembic upgrade head

# Docker
docker-compose up --build
```

---

## 🛠️ Стек

| Компонент | Технология |
|-----------|------------|
| Web Framework | FastAPI |
| ORM | SQLAlchemy async |
| Миграции | Alembic |
| База данных | SQLite → PostgreSQL |
| Кэш / очередь | Redis (Фаза 2+) |
| Аутентификация | JWT / bcrypt |
| LLM | Mimo (AsyncOpenAI-совместимый клиент) |
| Avatar Platform | kristina-revolutionary |
| Тесты | pytest-asyncio |
| Деплой | Docker / docker-compose |

---

## 🔗 Связанные репозитории

| Репозиторий | Ссылка | Доступ |
|-------------|--------|--------|
| Syndi-AI-world | [github.com/donjonson-hash/Syndi-AI-world](https://github.com/donjonson-hash/Syndi-AI-world) | Публичный |
| kristina-revolutionary | [github.com/donjonson-hash/kristina-revolutionary](https://github.com/donjonson-hash/kristina-revolutionary) | Приватный — источник Avatar Platform |

---

*Последнее обновление: 24 апреля 2026 · HEAD `75a70835` · 169 тестов ✅*
