# MERGE GUIDE — Объединение репозиториев в monorepo

Источники:
- `kristina-revolutionary` → папка `core/`
- `AI-avatar_command` → папка `frontend/`
Цель: `Syndi-AI-world` (этот репозиторий)

---

## Шаг 1 — Подготовка

```bash
# Клонируем основной репо

git clone https://github.com/donjonson-hash/Syndi-AI-world.git
cd Syndi-AI-world
```

---

## Шаг 2 — Добавыж kristina-revolutionary в core/

```bash
# Добавить репозиторий как источник
git remote add kristina https://github.com/donjonson-hash/kristina-revolutionary.git
git fetch kristina

# Создаём отдельную ветку из kristina/main
git checkout -b kristina-import kristina/main

# Возвращаемся на main
git checkout main

# Слияние через subtree в папку core/
# (subtree add сохраняет всю историю коммитов)
git subtree add --prefix=core kristina main --squash
```

**Результат:** все файлы из `kristina-revolutionary` появятся в `core/` с сохранённой историей коммитов.

---

## Шаг 3 — Добавление AI-avatar_command в frontend/

```bash
# Добавить репозиторий фронтенда как источник
git remote add avatar https://github.com/donjonson-hash/AI-avatar_command.git
git fetch avatar

# Слияние через subtree в папку frontend/
git subtree add --prefix=frontend avatar main --squash
```

**Результат:** все файлы из `AI-avatar_command` появятся в `frontend/`.

---

## Шаг 4 — Отправка в GitHub

```bash
git push origin main
```

---

## Шаг 5 — Проверка структуры

```bash
# Должно показать:
# core/   — Python файлы Кристины
# frontend/ — React/TS файлы
ls -la core/
ls -la frontend/
```

---

## Шаг 6 — Обновление в будущем

При обновлении исходных репозиториев используй `git subtree pull`:

```bash
# Обновить core/ из kristina-revolutionary
git subtree pull --prefix=core kristina main --squash

# Обновить frontend/ из AI-avatar_command
git subtree pull --prefix=frontend avatar main --squash

git push origin main
```

---

## После объединения: настройка core/

```bash
# Установка зависимостей Python
cd core
python3 -m venv venv
source venv/bin/activate     # Linux/Mac
# или: venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Запуск бота
cp .env.example .env
nano .env    # вписать TELEGRAM_TOKEN, DEEPSEEK_API_KEY, etc.
python bot.py
```

## После объединения: настройка frontend/

```bash
# Установка Node-зависимостей
cd frontend
npm install

# Скопировать переменные
cp .env.example .env
nano .env    # VITE_API_URL=http://localhost:8000

# Запуск в режиме разработки
npm run dev

# Production сборка (output: dist/)
npm run build
```

---

## Итоговая структура после всех шагов

```
Syndi-AI-world/
├── core/              (50+ Python файлов AI-ядра)
├── frontend/          (React + Vite + Tailwind дашборд)
├── backend/           (FastAPI + векторный поиск)
├── agent/             (DeepSeek агент разработки)
├── nginx/             (reverse proxy)
├── docker-compose.yml (полный стек)
└── setup_vps.sh       (автодеплой)
```

---

> После объединения исходные репозитории можно архивировать (включить readonly) на GitHub.
