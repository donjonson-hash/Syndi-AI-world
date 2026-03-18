# Syndi-AI Development Guide

## Быстрый старт для разработки (без Docker)

### 1. Установка

```bash
# Клонировать репозиторий
git clone https://github.com/donjonson-hash/Syndi-AI-world.git
cd Syndi-AI-world

# Запустить установку
./install.sh
```

### 2. Настройка

```bash
# Отредактировать .env файл
nano .env
```

Добавьте свои API ключи:
```bash
TELEGRAM_TOKEN=your_telegram_bot_token
DEEPSEEK_API_KEY=sk-your-deepseek-key
```

### 3. Запуск

```bash
# Только API
./run-dev.sh api

# Только Bot
./run-dev.sh bot

# Оба (API в фоне, Bot на переднем плане)
./run-dev.sh both
```

---

## Команды разработки

| Команда | Описание |
|---------|----------|
| `./run-dev.sh api` | Запустить API сервер |
| `./run-dev.sh bot` | Запустить Telegram бот |
| `./run-dev.sh both` | Запустить оба |
| `./run-dev.sh test` | Запустить тесты |
| `./run-dev.sh lint` | Проверить код линтером |
| `./run-dev.sh format` | Отформатировать код |
| `./run-dev.sh setup` | Настроить окружение |

---

## Ручная установка (если скрипты не работают)

```bash
# 1. Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 2. Установить зависимости
pip install -r requirements.txt
pip install -r requirements_bot.txt

# 3. Создать .env
cp .env.example .env
# Отредактировать .env

# 4. Запустить API
uvicorn api.main:app --reload

# 5. Запустить Bot (в другом терминале)
python -m bot.main
```

---

## Структура проекта

```
Syndi-AI-world/
├── api/              # FastAPI endpoints
├── bot/              # Telegram bot
├── core/             # Core modules
│   ├── agents/       # AI agents (Kristina)
│   ├── ai/           # LLM integration
│   ├── matching/     # Matching algorithm
│   ├── mystic/       # MBTI, Enneagram, Tarot
│   └── quantum/      # Quantum computing
├── models/           # Pydantic models
├── services/         # Business logic
├── tests/            # Unit tests
└── docs/             # Documentation
```

---

## API Endpoints

После запуска API доступны:

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

## Полезные ссылки

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Aiogram Docs](https://docs.aiogram.dev/)
- [DeepSeek API](https://platform.deepseek.com/)
