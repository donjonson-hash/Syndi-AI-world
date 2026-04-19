# Syndi-AI Makefile
# Quick commands for Docker operations

.PHONY: help build up down logs shell test clean restart

# Default target
help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║              Syndi-AI Docker Commands                      ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  make build      - Build all Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - View logs from all services"
	@echo "  make logs-api   - View API logs only"
	@echo "  make logs-bot   - View Bot logs only"
	@echo "  make shell-api  - Open shell in API container"
	@echo "  make shell-bot  - Open shell in Bot container"
	@echo "  make test       - Run tests in Docker"
	@echo "  make clean      - Remove all containers and volumes"
	@echo "  make prune      - Clean up unused Docker resources"
	@echo "  make status     - Show running containers"
	@echo ""

# Build images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start services
up:
	@echo "Starting Syndi-AI services..."
	docker-compose up -d
	@echo ""
	@echo "Services started:"
	@echo "  API:    http://localhost:8000"
	@echo "  Docs:   http://localhost:8000/docs"
	@echo "  Redis:  localhost:6379"
	@echo "  Postgres: localhost:5432"

# Stop services
down:
	@echo "Stopping services..."
	docker-compose down

# Restart services
restart: down up

# View logs
logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-bot:
	docker-compose logs -f bot

logs-redis:
	docker-compose logs -f redis

logs-db:
	docker-compose logs -f postgres

# Open shell in containers
shell-api:
	docker-compose exec api /bin/bash

shell-bot:
	docker-compose exec bot /bin/bash

shell-db:
	docker-compose exec postgres psql -U syndi -d syndi_db

# Run tests
test:
	docker-compose exec api pytest tests/ -v

# Clean up
clean:
	@echo "Removing containers and volumes..."
	docker-compose down -v
	docker-compose rm -f

prune:
	@echo "Cleaning up unused Docker resources..."
	docker system prune -f
	docker volume prune -f

# Show status
status:
	@echo "Running containers:"
	docker-compose ps
	@echo ""
	@echo "Container stats:"
	docker stats --no-stream

# Production deployment
prod-up:
	@echo "Starting production services..."
	docker-compose --profile production up -d

prod-down:
	docker-compose --profile production down

# Database operations
db-migrate:
	docker-compose exec api alembic upgrade head

db-backup:
	@echo "Creating database backup..."
	docker-compose exec postgres pg_dump -U syndi syndi_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore:
	@echo "Restoring database from backup..."
	cat $(file) | docker-compose exec -T postgres psql -U syndi -d syndi_db

# Development helpers
dev-setup:
	@echo "Setting up development environment..."
	cp .env.example .env
	@echo "Edit .env file with your API keys"

dev-logs:
	docker-compose logs -f api bot

# Health check
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | jq . || echo "API is not responding"
