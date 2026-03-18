# Загрузка Syndi на GitHub

## 📦 Вариант 1: Загрузка архива (Рекомендуется)

### Шаг 1: Скачайте архив

Архив проекта создан: `/mnt/okcomputer/output/Syndi.tar.gz`

### Шаг 2: Создайте репозиторий на GitHub

1. Перейдите на https://github.com/new
2. **Repository name:** `Syndi`
3. **Description:** `AI-powered platform for professional collaboration with Big Five matching`
4. Выберите **Public** или **Private**
5. ❌ **НЕ** отмечайте "Add a README file"
6. ❌ **НЕ** отмечайте "Add .gitignore"
7. ❌ **НЕ** отмечайте "Choose a license"
8. Нажмите **"Create repository"**

### Шаг 3: Загрузите файлы

На странице нового репозитория:

1. Нажмите **"uploading an existing file"**
2. Перетащите файлы из папки `syndi/` или выберите их
3. В поле "Commit changes" введите:
   - **Commit message:** `Initial commit: Syndi MVP with DeepSeek integration`
   - **Description:** 
     ```
     Features:
     - Big Five Assessment (15 questions, OCEAN model)
     - Smart Matching Algorithm
     - AI Agent Architecture
     - Kristina - UX Designer Agent
     - DeepSeek API integration
     - FastAPI backend (18 endpoints)
     - 36 unit tests
     ```
4. Нажмите **"Commit changes"**

---

## 💻 Вариант 2: Через командную строку

### Шаг 1: Откройте терминал на вашем компьютере

### Шаг 2: Клонируйте или создайте репозиторий

```bash
# Создайте папку для проекта
mkdir -p ~/Projects
cd ~/Projects

# Скачайте и распакуйте архив
# (замените путь на актуальный)
tar -xzf /path/to/Syndi.tar.gz

# Перейдите в папку проекта
cd syndi
```

### Шаг 3: Инициализируйте Git

```bash
# Инициализация
git init

# Настройка (замените на ваши данные)
git config user.name "Ваше Имя"
git config user.email "your@email.com"

# Добавление файлов
git add .

# Коммит
git commit -m "Initial commit: Syndi MVP with DeepSeek integration"
```

### Шаг 4: Подключение к GitHub

```bash
# Добавьте remote
git remote add origin https://github.com/donjonson-hash/Syndi.git

# Переименуйте ветку
git branch -M main

# Push на GitHub
git push -u origin main
```

При запросе пароля используйте **Personal Access Token**:
1. Создайте токен: https://github.com/settings/tokens
2. Выберите scope: `repo`
3. Используйте токен как пароль

---

## ✅ Проверка

После загрузки перейдите на:
https://github.com/donjonson-hash/Syndi

Убедитесь, что все файлы на месте:
- ✅ `api/`
- ✅ `agents/`
- ✅ `models/`
- ✅ `services/`
- ✅ `tests/`
- ✅ `docs/`
- ✅ `README.md`
- ✅ `requirements.txt`
- ✅ `.gitignore`

---

## 🔐 Важно: API ключи

Файл `.env` с API ключами **автоматически исключён** из загрузки благодаря `.gitignore`.

**Никогда не загружайте `.env` на GitHub!**

---

## 🎯 Следующие шаги

1. Добавьте описание репозитория
2. Добавьте topics: `python`, `fastapi`, `ai`, `llm`, `matching`
3. Создайте LICENSE файл
4. Включите GitHub Discussions для обратной связи

---

**Готово!** 🚀
