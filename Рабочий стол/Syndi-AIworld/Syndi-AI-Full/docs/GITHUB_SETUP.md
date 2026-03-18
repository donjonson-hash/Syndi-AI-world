# Публикация Syndi на GitHub

Это руководство поможет опубликовать проект Syndi на GitHub.

## 📋 Предварительные требования

1. **GitHub аккаунт** — зарегистрируйтесь на [github.com](https://github.com)
2. **Git** — установлен на вашей системе
3. **Доступ к репозиторию** — `https://github.com/donjonson-hash/Syndi.git`

## 🚀 Быстрый старт (Автоматический способ)

### Шаг 1: Запустите скрипт

```bash
cd /mnt/okcomputer/output/syndi
./push_to_github.sh
```

Скрипт автоматически:
- Инициализирует Git репозиторий
- Настроит Git (имя и email)
- Создаст коммит
- Отправит код на GitHub

### Шаг 2: Аутентификация

При первом push GitHub запросит аутентификацию:

**Вариант 1: Personal Access Token (рекомендуется)**
1. Создайте токен: https://github.com/settings/tokens
2. Выберите scope: `repo`
3. Используйте токен как пароль

**Вариант 2: SSH ключ**
```bash
# Сгенерируйте SSH ключ
ssh-keygen -t ed25519 -C "your@email.com"

# Добавьте ключ в GitHub
cat ~/.ssh/id_ed25519.pub
# Скопируйте и добавьте на https://github.com/settings/keys

# Используйте SSH URL
git remote set-url origin git@github.com:donjonson-hash/Syndi.git
```

---

## 📝 Ручной способ

Если автоматический скрипт не работает, выполните шаги вручную:

### Шаг 1: Инициализация Git

```bash
cd /mnt/okcomputer/output/syndi
git init
```

### Шаг 2: Настройка Git

```bash
git config user.name "Ваше Имя"
git config user.email "your@email.com"
```

### Шаг 3: Добавление файлов

```bash
git add .
```

### Шаг 4: Создание коммита

```bash
git commit -m "Initial commit: Syndi MVP with DeepSeek integration

Features:
- Big Five Assessment (15 questions, OCEAN model)
- Smart Matching Algorithm (Skills + Personality + Goals)
- AI Agent Architecture with memory
- Kristina - UX Designer Agent
- DeepSeek API integration
- FastAPI backend (18 endpoints)
- 36 unit tests"
```

### Шаг 5: Добавление remote

```bash
git remote add origin https://github.com/donjonson-hash/Syndi.git
```

### Шаг 6: Push на GitHub

```bash
git branch -M main
git push -u origin main
```

---

## 🔧 Создание репозитория на GitHub (если не существует)

1. Перейдите на https://github.com/new
2. **Repository name:** `Syndi`
3. **Description:** `AI-powered platform for professional collaboration with Big Five matching`
4. **Public** или **Private** (на ваш выбор)
5. ❌ **НЕ** отмечайте "Add a README file" (он уже есть)
6. ❌ **НЕ** отмечайте "Add .gitignore" (он уже есть)
7. ❌ **НЕ** отмечайте "Choose a license" (можно добавить позже)
8. Нажмите **"Create repository"**

---

## ✅ Проверка публикации

После успешного push:

1. Перейдите на https://github.com/donjonson-hash/Syndi
2. Убедитесь, что все файлы загружены:
   - `api/`
   - `agents/`
   - `models/`
   - `services/`
   - `tests/`
   - `docs/`
   - `README.md`
   - `requirements.txt`

---

## 🔐 Безопасность

### ⚠️ Важно: API ключи

Файл `.env` с API ключами **НЕ должен** попасть на GitHub!

Проверьте `.gitignore`:
```
# Environment Variables
.env
.env.local
.env.*.local
```

Проверьте, что `.env` не в репозитории:
```bash
git status
# .env должен быть в untracked files
```

### GitHub Secrets (для CI/CD)

Если настраиваете GitHub Actions, добавьте секреты:
1. Перейдите в Settings → Secrets and variables → Actions
2. Добавьте `DEEPSEEK_API_KEY`
3. Добавьте `SECRET_KEY`

---

## 🔄 Обновление репозитория

После внесения изменений:

```bash
# Добавить изменённые файлы
git add .

# Создать коммит
git commit -m "Описание изменений"

# Отправить на GitHub
git push
```

---

## 🆘 Решение проблем

### Ошибка: "Repository not found"

**Причина:** Репозиторий не существует или нет доступа

**Решение:**
1. Создайте репозиторий на GitHub
2. Проверьте правильность URL
3. Убедитесь, что у вас есть права на запись

### Ошибка: "Authentication failed"

**Причина:** Неверные учётные данные

**Решение:**
1. Используйте Personal Access Token вместо пароля
2. Проверьте настройки двухфакторной аутентификации
3. Для SSH: проверьте, что ключ добавлен в GitHub

### Ошибка: "Permission denied"

**Причина:** Нет прав на запись в репозиторий

**Решение:**
1. Проверьте, что вы владелец репозитория
2. Для чужих репозиториев: создайте fork
3. Используйте pull request

### Ошибка: "Updates were rejected"

**Причина:** В репозитории есть изменения, которых нет локально

**Решение:**
```bash
# Сначала получите изменения
git pull origin main

# Разрешите конфликты (если есть)
# Затем push
git push
```

---

## 📚 Полезные команды

```bash
# Проверить статус
git status

# Просмотреть историю коммитов
git log --oneline

# Отменить изменения в файле
git checkout -- filename

# Удалить файл из индекса (но не из рабочей директории)
git reset HEAD filename

# Изменить последний коммит
git commit --amend

# Просмотреть удалённые репозитории
git remote -v
```

---

## 🎯 Следующие шаги после публикации

1. **Добавьте описание** в About секцию на GitHub
2. **Добавьте topics:** `python`, `fastapi`, `ai`, `matching`, `big-five`
3. **Включите GitHub Actions** для CI/CD
4. **Настройте GitHub Pages** для документации (опционально)
5. **Добавьте LICENSE** файл
6. **Создайте Issues** для планируемых функций

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте документацию GitHub: https://docs.github.com
2. Поищите решение на Stack Overflow
3. Создайте issue в репозитории

---

**Успешной публикации!** 🚀
