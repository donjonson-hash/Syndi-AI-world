#!/bin/bash
# setup.sh — быстрая установка окружения для agent_deepseek
# Запуск: bash setup.sh

set -e

PYTHON=$(which python3 || which python)
echo "[1/4] Используем Python: $PYTHON"

echo "[2/4] Создаём venv..."
$PYTHON -m venv venv

echo "[3/4] Устанавливаем зависимости..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "[4/4] Проверяем .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  ⚠️  Создан .env из .env.example — заполни DEEPSEEK_API_KEY и GITHUB_TOKEN!"
else
    echo "  ✅ .env уже существует"
fi

echo ""
echo "✅ Готово! Теперь запусти:"
echo "   source venv/bin/activate"
echo "   python agent_deepseek.py"
