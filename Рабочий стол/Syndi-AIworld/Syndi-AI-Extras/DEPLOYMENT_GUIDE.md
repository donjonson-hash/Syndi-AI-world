# Syndi-AI Deployment Guide

## Quick Start Options

### Option 1: Local Development (Recommended for testing)

```bash
# 1. Extract the main archive
tar -xzf Syndi-AI-Full.tar.gz
cd Syndi-AI-Full

# 2. Run setup script
./setup.sh

# 3. Edit environment variables
nano .env

# 4. Start services
make run-api      # Terminal 1
make run-bot      # Terminal 2
```

### Option 2: Docker (Recommended for production)

```bash
# 1. Extract archives
tar -xzf Syndi-AI-Full.tar.gz
cp -r Syndi-AI-Extras/.github Syndi-AI-Full/
cp Syndi-AI-Extras/Dockerfile Syndi-AI-Full/
cp Syndi-AI-Extras/docker-compose.yml Syndi-AI-Full/
cp Syndi-AI-Extras/.dockerignore Syndi-AI-Full/
cd Syndi-AI-Full

# 2. Configure environment
cp .env.example .env
nano .env

# 3. Build and run
docker-compose up -d

# 4. Check logs
docker-compose logs -f
```

---

## Detailed Setup

### Prerequisites

- Python 3.10+ (for local development)
- Docker & Docker Compose (for containerized deployment)
- Git

### Required API Keys

| Service | Purpose | Get Key At |
|---------|---------|------------|
| Telegram Bot | Bot interface | [@BotFather](https://t.me/BotFather) |
| DeepSeek | LLM responses | [platform.deepseek.com](https://platform.deepseek.com) |
| IONQ | Quantum computing | [ionq.com](https://ionq.com) (optional) |

---

## Environment Variables

Create `.env` file:

```bash
# Telegram Bot (Required)
TELEGRAM_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_user_id

# DeepSeek LLM (Required)
DEEPSEEK_API_KEY=sk-your-deepseek-api-key

# IONQ Quantum (Optional)
IONQ_API_KEY=your_ionq_api_key
USE_REAL_QUANTUM=false

# Application Settings
DEBUG=false
API_URL=http://localhost:8000
```

---

## Deployment Scenarios

### 1. VPS/Cloud Server (Ubuntu)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Clone repository
git clone https://github.com/donjonson-hash/Syndi-AI.git
cd Syndi-AI

# Configure
cp .env.example .env
nano .env

# Deploy
docker-compose up -d

# Setup auto-restart
sudo systemctl enable docker
```

### 2. Railway/Render/Heroku

Use the included `Dockerfile`:

```dockerfile
# Build command (automatic)
docker build -t syndi-ai .

# Start command
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### 3. Raspberry Pi / ARM

Docker images support `linux/arm64` platform:

```bash
docker-compose up -d
```

---

## GitHub Setup

### Enable GitHub Actions

1. Push code to GitHub
2. Go to **Actions** tab
3. Enable workflows

### Configure Secrets

Go to **Settings → Secrets and variables → Actions**:

| Secret | Description |
|--------|-------------|
| `DEEPSEEK_API_KEY` | Your DeepSeek API key |
| `TELEGRAM_TOKEN` | Bot token |
| `SERVER_HOST` | Deployment server IP |
| `SERVER_USER` | SSH username |
| `SSH_PRIVATE_KEY` | SSH key for deployment |

---

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Full status
curl http://localhost:8000/
```

### Logs

```bash
# Docker logs
docker-compose logs -f syndi-api
docker-compose logs -f syndi-bot

# Local logs
tail -f logs/api.log
tail -f logs/bot.log
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change port in docker-compose.yml |
| Bot not responding | Check TELEGRAM_TOKEN |
| LLM not working | Verify DEEPSEEK_API_KEY |
| Tests failing | Some tests need real API keys |

### Debug Mode

```bash
# Enable debug
DEBUG=true make run-api
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Users                               │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Telegram │    │  Web UI  │    │  API     │
    │   Bot    │    │ (future) │    │ Clients  │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
              ┌──────────▼──────────┐
              │   Syndi-AI API      │
              │   (FastAPI)         │
              │   Port: 8000        │
              └──────────┬──────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Big Five    │ │   Matching   │ │    Agents    │
│  Assessment  │ │  Algorithm   │ │  (Kristina)  │
└──────────────┘ └──────────────┘ └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
              ┌──────────▼──────────┐
              │   External APIs     │
              │  • DeepSeek (LLM)   │
              │  • IONQ (Quantum)   │
              └─────────────────────┘
```

---

## Support

- Documentation: `/docs`
- Issues: GitHub Issues
- API Docs: `http://localhost:8000/docs`
