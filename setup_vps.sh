#!/usr/bin/env bash
# ============================================================
# setup_vps.sh — первичная установка на VPS
# Запуск: bash setup_vps.sh
# ============================================================
set -e

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

log "=== Syndi-AI VPS Setup ==="

# 1. Система
log "Обновление системы..."
apt-get update -qq && apt-get upgrade -y -qq
apt-get install -y -qq git curl wget unzip nginx-common

# 2. Docker
if ! command -v docker &>/dev/null; then
    log "Установка Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker && systemctl start docker
    ok "Docker установлен: $(docker --version)"
else
    ok "Docker уже установлен: $(docker --version)"
fi

# 3. Docker Compose plugin
if ! docker compose version &>/dev/null; then
    log "Установка Docker Compose plugin..."
    apt-get install -y docker-compose-plugin
    ok "Docker Compose: $(docker compose version)"
else
    ok "Docker Compose: $(docker compose version)"
fi

# 4. Клонируем репозиторий
PROJECT_DIR="/opt/syndi-ai"
if [ -d "$PROJECT_DIR/.git" ]; then
    log "Репозиторий уже существует — обновляем..."
    cd "$PROJECT_DIR" && git pull origin main
else
    log "Клонируем репозиторий..."
    git clone https://github.com/donjonson-hash/Syndi-AI-world.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# 5. .env файл
if [ ! -f .env ]; then
    log "Создаём .env из примера..."
    cp .env.example .env
    warn "⚠️  ОБЯЗАТЕЛЬНО отредактируй .env перед запуском!"
    warn "    nano /opt/syndi-ai/.env"
else
    ok ".env уже существует"
fi

# 6. Nginx папка для сертификатов
mkdir -p nginx/certs

# 7. Запуск стека
log "Запуск Docker Compose..."
docker compose pull
docker compose up -d --build

# 8. Статус
sleep 5
echo ""
log "=== Статус сервисов ==="
docker compose ps

echo ""
ok "✅ Syndi-AI запущен!"
echo ""
echo "  API:     http://$(hostname -I | awk '{print $1}')/api/"
echo "  Docs:    http://$(hostname -I | awk '{print $1}')/docs"
echo "  Health:  http://$(hostname -I | awk '{print $1}')/health"
echo ""
warn "Логи: docker compose logs -f api"
warn "Стоп: docker compose down"
