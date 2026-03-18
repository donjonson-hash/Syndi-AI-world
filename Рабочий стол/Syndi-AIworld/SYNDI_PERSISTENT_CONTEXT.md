# SYNDI — PERSISTENT_CONTEXT для AI-партнёра (Kimi)

## 🎯 Проект: Syndi
**Название:** Syndi (Synergy + Individual)  
**Слоган:** "Твой AI-напарник для мировых проектов"  
**Статус:** MVP разработка ✅

---

## 📋 Суть проекта

Платформа персональных AI-агентов для глобального профессионального сотрудничества. 
Каждый пользователь получает AI-агента, адаптированного под его психотип (Big Five) 
и профессиональные навыки.

---

## 🏗️ Архитектура

### Core Components:
1. **User Profile System** — Big Five assessment, skills, goals ✅
2. **AI Agent Engine** — Kristina-core с персонализацией
3. **Matching Algorithm** — совместимость по навыкам + психотипу ✅
4. **Workspace Platform** — проектные пространства
5. **Mobile/Web Interface** — Flutter + FastAPI

### Tech Stack:
- **Backend:** Python, FastAPI, PostgreSQL ✅ (FastAPI готово)
- **AI:** DeepSeek API, Perplexity API, Custom agents
- **Mobile:** Flutter
- **Infrastructure:** Linux, systemd, nginx

---

## 💼 Бизнес-модель

**Монетизация:** Подписка (честная модель)

| Тариф | Цена | Возможности |
|-------|------|-------------|
| Free | $0 | Профиль, 3 матча/день |
| Pro | $9/мес | Безлимит матчинг, AI-агент, 3 проекта |
| Team | $29/мес | Командные пространства, API |
| Enterprise | Custom | White-label, приоритет |

---

## 🚀 Roadmap

### Этап 1: MVP (Месяц 1) ✅ ВЫПОЛНЕНО
- [x] Big Five тест (15 вопросов)
- [x] Базовый алгоритм матчинга
- [x] Кристина как шаблон агента
- [x] FastAPI endpoints
- [ ] Telegram-бот интерфейс

### Этап 2: Beta (Месяцы 2-3)
- [ ] Flutter мобильное приложение
- [ ] PostgreSQL база данных
- [ ] Рабочие пространства (Kanban, чаты)
- [ ] 1000 тестовых пользователей
- [ ] Интеграция видеозвонков

### Этап 3: Launch (Месяцы 4-6)
- [ ] Глобальный маркетинг
- [ ] Платёжная система
- [ ] Enterprise клиенты
- [ ] Международные команды

---

## 🔑 Ключевые решения

| Параметр | Значение | Обоснование |
|----------|----------|-------------|
| Психометрика | Big Five (OCEAN) | Научно верифицирована |
| Первый шаблон | Кристина (UX-дизайнер) | Уже разработана |
| Монетизация | Подписка | Честная модель |
| Целевая аудитория | Профессионалы 25-40 лет | Глобальная удалёнка |

---

## 📁 Структура проекта

```
/mnt/okcomputer/output/syndi/
├── api/
│   ├── __init__.py
│   └── main.py              # FastAPI приложение
├── models/
│   ├── __init__.py
│   ├── big_five.py          # Модель Big Five (15 вопросов)
│   └── user.py              # Модели пользователей
├── services/
│   ├── __init__.py
│   └── matching.py          # Алгоритм матчинга
├── tests/
│   ├── __init__.py
│   ├── test_big_five.py     # Тесты Big Five
│   └── test_matching.py     # Тесты матчинга
├── docs/                    # Документация
├── __init__.py
├── requirements.txt         # Зависимости
├── .env.example            # Пример конфигурации
├── README.md               # Документация проекта
└── SYNDI_PERSISTENT_CONTEXT.md  # Этот файл
```

---

## 🔌 API Endpoints

### Big Five Test
- `GET /test/questions` — 15 вопросов теста
- `POST /test/submit` — отправить ответы, получить профиль OCEAN

### Users
- `POST /users` — создать пользователя
- `GET /users/{id}` — получить профиль
- `PATCH /users/{id}` — обновить профиль
- `POST /users/{id}/big-five` — сохранить результаты теста
- `GET /users` — список пользователей с фильтрами

### Matching
- `GET /matches/{user_id}` — найти совместимых пользователей
- `GET /matches/{user_id}/quick` — быстрый матчинг (MVP)

### Development
- `POST /seed` — создать тестовые данные

---

## 🧪 Алгоритм матчинга

```
Overall Score = Skill × 0.4 + Personality × 0.35 + Goals × 0.25
```

### Факторы:
1. **Skills (40%)** — комплементарность навыков
2. **Personality (35%)** — совместимость Big Five
3. **Goals (25%)** — совместимость целей

---

## 🎯 Текущая задача

MVP готов! Следующие шаги:
1. Интеграция PostgreSQL для постоянного хранения
2. Telegram-бот интерфейс
3. Flutter мобильное приложение

---

*Создано:* 2026-03-14  
*Автор:* Anatoly + Kimi (AI-партнёр)  
*Версия:* 1.0
