# Syndi-AI World — Monorepo

AI-платформа: умный аватар Кристина + backend + frontend. Один репозиторий — весь стек.

## Структура monorepo

```
Syndi-AI-world/
├── core/                  ← AI-ядро (из kristina-revolutionary)
│   ├── brain_unified.py   — единый мозг агента
│   ├── bot.py             — Telegram-бот
│   ├── emotional_core.py  — эмоциональный движок
│   ├── agents/            — агенты задач
│   ├── avatar_platform/   — платформа аватара
│   ├── mini_app/          — Telegram Mini App
│   ├── mobile_app/        — мобильное приложение
│   └── requirements.txt
│
├── frontend/              ← Веб-дашборд команд (из AI-avatar_command)
│   ├── src/               — React + TypeScript + Tailwind
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── backend/               ← FastAPI + PostgreSQL + Qdrant
├── agent/                 ← DeepSeek агент разработки
├── nginx/                 ← Reverse proxy конфиг
├── docker-compose.yml     ← Production стек
├── MERGE_GUIDE.md         ← Инструкция по объединению репозиториев
└── setup_vps.sh           ← Установка на VPS
```

## Компоненты

| Компонент | Репозиторий-источник | Описание |
|---|---|---|
| `core/` | kristina-revolutionary | AI-мозг, бот, память, эмоции |
| `frontend/` | AI-avatar_command | React-дашборд управления аватаром |
| `backend/` | Syndi-AI-world | FastAPI, векторный поиск, БД |

## Быстрый старт на VPS

```bash
ssh root@195.245.112.66 -p 3333

git clone https://github.com/donjonson-hash/Syndi-AI-world.git /opt/syndi-ai
cd /opt/syndi-ai
cp .env.example .env
nano .env          # заполнить ключи API
docker compose up -d --build
```

## Запуск AI-ядра (core)

```bash
cd core
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

## Запуск фронтенда (frontend)

```bash
cd frontend
npm install
npm run dev        # разработка
npm run build      # production сборка
```

## Проверка стека

```bash
docker compose ps
docker compose logs -f api
curl http://localhost/health
curl http://localhost/docs      # Swagger UI
```

## Управление

```bash
docker compose up -d --build    # запуск / пересборка
docker compose down             # остановка
docker compose pull && docker compose up -d --build  # обновление
```

## DeepSeek агент разработки

```bash
cd agent
python agent_deepseek.py
```

---

> **Репозитории-источники (архив):**
> - [kristina-revolutionary](https://github.com/donjonson-hash/kristina-revolutionary) → `core/`
> - [AI-avatar_command](https://github.com/donjonson-hash/AI-avatar_command) → `frontend/`
