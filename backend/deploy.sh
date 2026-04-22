#!/bin/bash
# Syndi — деплой без Docker (venv + uvicorn)
# Запускать из папки backend/:
#   bash deploy.sh

set -e
cd "$(dirname "$0")"

echo "=== Syndi Deploy (venv + uvicorn) ==="

# 1. Активируем venv (создаём если нет)
if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "✓ venv activated"

# 2. Устанавливаем зависимости
pip install -q -r requirements.txt
echo "✓ dependencies installed"

# 3. Останавливаем старый процесс если был
OLD_PID=$(lsof -ti :8081 2>/dev/null || true)
if [ -n "$OLD_PID" ]; then
    echo "Stopping old process (PID $OLD_PID)..."
    kill "$OLD_PID" 2>/dev/null || true
    sleep 1
fi

# 4. Запускаем uvicorn в фоне
echo "Starting uvicorn on port 8081..."
nohup uvicorn main:app \
    --host 0.0.0.0 \
    --port 8081 \
    --workers 1 \
    --log-level info \
    > uvicorn.log 2>&1 &

UVICORN_PID=$!
echo $UVICORN_PID > uvicorn.pid
echo "✓ uvicorn started (PID $UVICORN_PID)"

# 5. Ждём запуска
echo "Waiting for startup..."
for i in $(seq 1 10); do
    sleep 1
    if curl -sf http://localhost:8081/health > /dev/null 2>&1; then
        echo "✓ Health check passed"
        break
    fi
    if [ "$i" -eq 10 ]; then
        echo "✗ Health check failed. Last log lines:"
        tail -20 uvicorn.log
        exit 1
    fi
done

# 6. Результат
PUBLIC_IP=$(curl -sf https://api.ipify.org 2>/dev/null || echo "YOUR_SERVER_IP")
echo ""
echo "=== Syndi is running ==="
echo "  UI:       http://${PUBLIC_IP}:8081"
echo "  API docs: http://${PUBLIC_IP}:8081/docs"
echo "  Health:   http://${PUBLIC_IP}:8081/health"
echo ""
echo "Logs: tail -f $(pwd)/uvicorn.log"
echo "Stop: kill \$(cat $(pwd)/uvicorn.pid)"
