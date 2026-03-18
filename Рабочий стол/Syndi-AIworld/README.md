# 🔮 Syndi-AI 2.0

AI-powered платформа для профессионального сотрудничества и глубокого анализа личности.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com)
[![aiogram](https://img.shields.io/badge/aiogram-3.0%2B-orange)](https://docs.aiogram.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Возможности

### 🧠 Психометрический анализ
- **Big Five (OCEAN)** — научно обоснованная модель личности (15 вопросов)
- **MBTI** — типология личности (16 типов)
- **Эннеаграмма** — 9 типов личности с крыльями
- **Психоматрица** — числа судьбы по дате рождения

### 🔮 Мистические системы
- **Таро** — расклады карт с AI-интерпретацией
- **Ба Цзы** — китайская астрология
- **Биоритмы** — физические, эмоциональные, интеллектуальные циклы
- **Теневая сторона** — анализ по Юнгу
- **Индекс безумия** — творческий потенциал

### ⚛️ Квантовые вычисления
- **IONQ интеграция** — реальные квантовые вычисления
- **Генерация квантовых путей** — уникальные траектории развития
- **Квантовый анализ** — вероятностные предсказания

### 🤝 Smart Matching
- **Алгоритм совместимости** — Skills 40% + Personality 35% + Goals 25%
- **Комплементарность навыков** — поиск идеальных партнеров
- **Big Five matching** — совместимость психотипов

### 🤖 AI-Агенты
- **Kristina** — UX Designer Agent с DeepSeek API
- **Персонализированные рекомендации** — на основе профиля
- **Память и контекст** — сохранение истории диалогов

### 📱 Интерфейсы
- **FastAPI** — REST API (18 endpoints)
- **Telegram Bot** — интерактивный интерфейс
- **Ежедневные рекомендации** — автоматические уведомления

## 🚀 Быстрый старт

### Установка

```bash
# Клонировать репозиторий
git clone https://github.com/donjonson-hash/Syndi-AI.git
cd Syndi-AI

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

### Настройка окружения

```bash
# Скопировать шаблон конфигурации
cp .env.example .env

# Отредактировать .env и добавить свои ключи
nano .env
```

**Обязательные переменные:**
```env
# Telegram Bot (для бота)
TELEGRAM_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_id

# DeepSeek API (для AI)
DEEPSEEK_API_KEY=your_deepseek_api_key

# IONQ (опционально, для квантовых вычислений)
IONQ_API_KEY=your_ionq_api_key
```

### Запуск

**FastAPI сервер:**
```bash
python main.py
# или
uvicorn api.main:app --reload
```

**Telegram бот:**
```bash
python bot_main.py
```

## 🏗️ Архитектура

```
Syndi-AI/
│
├── api/                    # FastAPI endpoints
│   ├── main.py
│   └── routers/
│
├── bot/                    # Telegram Bot
│   ├── handlers/           # Хендлеры команд
│   ├── routers/            # Роутеры
│   ├── states/             # FSM состояния
│   └── middlewares/        # Мидлвары
│
├── core/                   # Ядро системы
│   ├── ai/                 # AI интеграция
│   │   ├── deepseek.py
│   │   └── recommender.py
│   ├── quantum/            # Квантовые вычисления
│   │   ├── ionq_integration.py
│   │   ├── generator.py
│   │   └── analysis.py
│   ├── mystic/             # Мистические системы
│   │   ├── mbti.py
│   │   ├── enneagram.py
│   │   ├── psychomatrix.py
│   │   ├── tarot.py
│   │   ├── baizi.py
│   │   └── biorhythm.py
│   ├── matching/           # Алгоритм матчинга
│   │   └── engine.py
│   └── agents/             # AI-агенты
│       ├── base.py
│       └── kristina.py
│
├── models/                 # Pydantic модели
│   ├── user.py
│   ├── big_five.py
│   └── mystic.py
│
├── services/               # Сервисы
│   ├── llm.py
│   └── matching.py
│
└── tests/                  # Тесты
```

## 📚 API Endpoints

### Big Five Test
- `GET /test/questions` — получить 15 вопросов
- `POST /test/submit` — отправить ответы, получить профиль

### Users
- `POST /users` — создать пользователя
- `GET /users/{id}` — получить профиль
- `POST /users/{id}/big-five` — сохранить результаты теста

### Matching
- `GET /matches/{user_id}` — найти совместимых пользователей
- `GET /matches/{user_id}/quick` — быстрый матчинг

### AI Agents
- `GET /agents` — список агентов
- `POST /agents/{id}/chat` — отправить сообщение агенту

## 🛡️ Безопасность

- Никогда не коммитьте файл `.env` с реальными ключами
- Используйте `.env.example` как шаблон
- Храните API ключи в безопасности

## 📝 Лицензия

Распространяется под лицензией MIT. См. [LICENSE](LICENSE) для подробностей.

## 👤 Автор

**donjonson-hash** — [GitHub](https://github.com/donjonson-hash)

---

⭐ Если проект вам понравился, поставьте звезду!
