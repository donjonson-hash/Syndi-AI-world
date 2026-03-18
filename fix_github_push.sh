#!/bin/bash

echo "🔧 Исправление проблем с отправкой на GitHub"

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Добавляем файлы
echo -e "${YELLOW}📦 Добавление файлов...${NC}"
git add .

# 2. Создаем коммит
echo -e "${YELLOW}💾 Создание коммита...${NC}"
git commit -m "Syndi Mobile App"

# 3. Проверяем ветку
echo -e "${YELLOW}🌿 Проверка ветки...${NC}"
current_branch=$(git branch --show-current)
echo "Текущая ветка: $current_branch"

if [ "$current_branch" != "main" ]; then
    echo "Переименовываем в main..."
    git branch -M main
fi

# 4. Пробуем pull
echo -e "${YELLOW}📥 Получение изменений с GitHub...${NC}"
git pull origin main --allow-unrelated-histories

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Возможно, нет удаленной ветки. Пробуем push...${NC}"
else
    # Если pull прошел успешно, добавляем merge-коммит
    git add .
    git commit -m "Merge remote changes"
fi

# 5. Запрос токена
echo -e "${YELLOW}🔑 Введите GitHub токен:${NC}"
read -s token

# 6. Настройка remote с токеном
git remote set-url origin https://donjonson-hash:${token}@github.com/donjonson-hash/Syndi-AI-world.git

# 7. Отправка
echo -e "${YELLOW}📤 Отправка на GitHub...${NC}"
git push -u origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Успешно отправлено!${NC}"
    echo "🌐 https://github.com/donjonson-hash/Syndi-AI-world"
    echo "🚀 GitHub Actions запустит сборку APK автоматически"
else
    echo -e "${RED}❌ Ошибка отправки. Пробуем принудительно...${NC}"
    echo "ВНИМАНИЕ: Принудительная отправка перезапишет файлы на GitHub!"
    read -p "Продолжить? (y/n): " force
    
    if [ "$force" = "y" ]; then
        git push -u origin main --force
        echo -e "${GREEN}✅ Принудительно отправлено!${NC}"
    fi
fi
