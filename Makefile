.PHONY: help install dev stop test lint build clean
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
install:
	cd backend && pip install -r requirements.txt
	cd core && pip install -r requirements.txt 2>/dev/null || true
	cd frontend && npm ci
dev: ## Start all services with docker-compose
	docker-compose up --build -d
stop: ## Stop all services
	docker-compose down
dev-backend: ## Run backend locally
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
dev-frontend: ## Run frontend locally
	cd frontend && npm run dev
dev-db: ## Start only database services
	docker-compose up -d postgres redis qdrant
test: ## Run all tests
	cd backend && pytest tests/ -v
test-core:
	cd core && pytest tests/ -v || true
lint: ## Lint everything
	cd backend && ruff check app/ tests/ && mypy app/ --ignore-missing-imports
	cd frontend && npm run lint
build: ## Build Docker images
	docker-compose build
clean: ## Remove caches and containers
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	docker-compose down -v 2>/dev/null || true
