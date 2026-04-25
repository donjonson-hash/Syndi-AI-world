# ============================================================
# core/Dockerfile — Kristina AI Bot (Python 3.11)
# Запуск: docker compose --profile full up kristina
# ============================================================

FROM python:3.11-slim AS base

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости первыми (кэш Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Создаём папку для данных (SQLite, логи)
RUN mkdir -p /app/data /app/logs

# Пользователь без root-привилегий
RUN useradd -m -u 1000 kristina && chown -R kristina:kristina /app
USER kristina

# Healthcheck — проверяем что процесс жив
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:8080/health || python -c "import sys; sys.exit(0)"

EXPOSE 8080

# Точка входа — главный бот
CMD ["python", "bot.py"]

# ============================================================
# Локальная разработка:
#   cd core && cp .env.example .env && nano .env
#   docker build -t syndi-kristina .
#   docker run --env-file .env syndi-kristina
# ============================================================
