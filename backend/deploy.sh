#!/bin/bash
# Syndi — быстрый деплой на VPS
# Запускать из папки backend/ на сервере:
#   bash deploy.sh

set -e

echo "=== Syndi Deploy ==="

# 1. Pull последние изменения
cd "$(dirname "$0")"
git pull origin main

# 2. Сборка и запуск
docker compose -f docker-compose.prod.yml up -d --build

# 3. Ждём health check
echo "Waiting for service to be healthy..."
sleep 5

STATUS=$(docker compose -f docker-compose.prod.yml ps --format json | python3 -c "
import sys, json
data = sys.stdin.read().strip()
if data:
    for line in data.splitlines():
        try:
            s = json.loads(line)
            print(s.get('Health', s.get('Status', 'unknown')))
        except:
            pass
" 2>/dev/null || echo "starting")

echo "Status: $STATUS"

# 4. Проверяем /health
curl -sf http://localhost:8081/health && echo "" && echo "✓ Service is UP"
echo ""
echo "=== Done ==="
echo "UI:      http://$(curl -s ifconfig.me):8081"
echo "API docs: http://$(curl -s ifconfig.me):8081/docs"
