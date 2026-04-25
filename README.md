# Syndi-AI World

Платформа умных знакомств на основе AI. Один репозиторий — весь стек.

## Архитектура

```
nginx (80/443)
  ├── /api/     → FastAPI (8000)     — основной backend
  ├── /embed/   → embed_server (8001) — векторный микросервис
  └── /health   → healthcheck

PostgreSQL (5432) — основная БД
Redis      (6379) — кэш, очереди
Qdrant     (6333) — векторный поиск профилей
```

## Быстрый старт на VPS

```bash
# Подключиться к VPS
ssh root@195.245.112.66 -p 3333

# Одной командой — установить всё и запустить
curl -fsSL https://raw.githubusercontent.com/donjonson-hash/Syndi-AI-world/main/setup_vps.sh | bash

# Или вручную:
git clone https://github.com/donjonson-hash/Syndi-AI-world.git /opt/syndi-ai
cd /opt/syndi-ai
cp .env.example .env
nano .env          # заполнить ключи
docker compose up -d --build
```

## Проверка работы

```bash
docker compose ps                    # статус контейнеров
docker compose logs -f api           # логи backend
curl http://localhost/health         # healthcheck
curl http://localhost/docs           # Swagger UI
```

## Управление

```bash
docker compose up -d --build    # запуск / пересборка
docker compose down             # остановка
docker compose pull && docker compose up -d --build  # обновление
```

## Разработка (локально)

Проект `donjonson-hash/Syndi-AI` — агент для разработки идей через DeepSeek.

```bash
python agent_deepseek.py
```
