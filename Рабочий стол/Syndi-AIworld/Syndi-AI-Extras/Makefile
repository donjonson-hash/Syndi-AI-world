# Syndi-AI Makefile
.PHONY: help install test lint format run-api run-bot docker-build docker-up docker-down clean

# Default target
help:
	@echo "Syndi-AI - Available Commands:"
	@echo ""
	@echo "  make install      - Install all dependencies"
	@echo "  make test         - Run all tests"
	@echo "  make lint         - Run linters (flake8, black, isort)"
	@echo "  make format       - Format code with black and isort"
	@echo "  make run-api      - Start FastAPI server"
	@echo "  make run-bot      - Start Telegram bot"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start all services with docker-compose"
	@echo "  make docker-down  - Stop all services"
	@echo "  make clean        - Clean cache and temp files"
	@echo ""

# Installation
install:
	pip install -r requirements.txt
	pip install -r requirements_bot.txt
	pip install pytest pytest-asyncio flake8 black isort mypy

# Testing
test:
	pytest tests/ -v --tb=short

test-coverage:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Linting
lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	black --check . || true
	isort --check-only . || true

# Formatting
format:
	black .
	isort .

# Running
run-api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

run-bot:
	python -m bot.main

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	docker system prune -f

# Cleaning
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true

# Setup for development
setup-dev:
	cp .env.example .env
	@echo "Edit .env file with your API keys"
	mkdir -p data logs

# Full deployment
deploy: docker-build docker-up
	@echo "Syndi-AI is running!"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
