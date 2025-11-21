# ============================================
# CodeRenew Makefile
# ============================================

.PHONY: help dev staging prod stop logs shell migrate test build clean

# Default target
help:
	@echo "CodeRenew Docker Commands"
	@echo "========================="
	@echo ""
	@echo "Environment Commands:"
	@echo "  make dev        - Start development environment"
	@echo "  make staging    - Start staging environment"
	@echo "  make prod       - Start production environment"
	@echo "  make stop       - Stop all containers"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make logs       - View all container logs"
	@echo "  make logs-f     - Follow all container logs"
	@echo "  make shell      - Open shell in backend container"
	@echo "  make shell-db   - Open psql shell in database"
	@echo "  make migrate    - Run database migrations"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build      - Build all images"
	@echo "  make build-nc   - Build all images (no cache)"
	@echo "  make clean      - Remove all containers and volumes"
	@echo ""
	@echo "Celery Commands:"
	@echo "  make celery-logs    - View Celery worker logs"
	@echo "  make celery-shell   - Open shell in Celery worker"
	@echo ""

# ===================
# Environment Commands
# ===================

dev:
	@echo "Starting development environment..."
	@cp -n .env.development .env 2>/dev/null || true
	docker compose up -d
	@echo "Development environment started!"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

staging:
	@echo "Starting staging environment..."
	@test -f .env.staging || (echo "Error: .env.staging not found" && exit 1)
	docker compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging up -d
	@echo "Staging environment started!"

prod:
	@echo "Starting production environment..."
	@test -f .env.production || (echo "Error: .env.production not found" && exit 1)
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production up -d
	@echo "Production environment started!"

stop:
	@echo "Stopping all containers..."
	docker compose down
	@echo "All containers stopped."

# ===================
# Logging Commands
# ===================

logs:
	docker compose logs

logs-f:
	docker compose logs -f

logs-backend:
	docker compose logs backend

logs-frontend:
	docker compose logs frontend

celery-logs:
	docker compose logs celery_worker celery_beat

# ===================
# Shell Commands
# ===================

shell:
	docker compose exec backend /bin/bash

shell-db:
	docker compose exec db psql -U $${POSTGRES_USER:-coderenew} -d $${POSTGRES_DB:-coderenew}

celery-shell:
	docker compose exec celery_worker /bin/bash

# ===================
# Database Commands
# ===================

migrate:
	@echo "Running database migrations..."
	docker compose exec backend alembic upgrade head
	@echo "Migrations complete."

migrate-create:
	@read -p "Migration message: " msg; \
	docker compose exec backend alembic revision --autogenerate -m "$$msg"

migrate-downgrade:
	docker compose exec backend alembic downgrade -1

# ===================
# Build Commands
# ===================

build:
	docker compose build

build-nc:
	docker compose build --no-cache

build-staging:
	docker compose -f docker-compose.yml -f docker-compose.staging.yml build

build-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# ===================
# Testing Commands
# ===================

test:
	docker compose exec backend pytest

test-cov:
	docker compose exec backend pytest --cov=app --cov-report=html

# ===================
# Cleanup Commands
# ===================

clean:
	@echo "Removing all containers, networks, and volumes..."
	docker compose down -v --remove-orphans
	@echo "Cleanup complete."

clean-all:
	@echo "Removing all containers, images, and volumes..."
	docker compose down -v --remove-orphans --rmi all
	@echo "Full cleanup complete."

# ===================
# Status Commands
# ===================

ps:
	docker compose ps

status:
	@echo "Container Status:"
	@docker compose ps
	@echo ""
	@echo "Resource Usage:"
	@docker stats --no-stream $$(docker compose ps -q) 2>/dev/null || echo "No running containers"
