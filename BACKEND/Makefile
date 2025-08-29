# PlayRight Backend Makefile

.PHONY: help setup build up down logs clean test lint format

# Default target
help:
	@echo "PlayRight Backend Commands:"
	@echo "  setup     - Initial setup (copy env files, install dependencies)"
	@echo "  build     - Build all Docker containers"
	@echo "  up        - Start all services with Docker Compose"
	@echo "  down      - Stop all services"
	@echo "  logs      - View logs from all services"
	@echo "  clean     - Clean up containers and volumes"
	@echo "  test      - Run all tests"
	@echo "  lint      - Run linting on Python code"
	@echo "  format    - Format Python code with Black"

# Initial setup
setup:
	@echo "🛠️  Setting up PlayRight Backend..."
	cp .env.example .env
	cp api-server/.env.example api-server/.env
	cp ai-engine/.env.example ai-engine/.env
	@echo "✅ Environment files created. Please update them with your configuration."
	@echo "📖 See BACKEND/README.md for configuration details."

# Build containers
build:
	@echo "🔨 Building Docker containers..."
	docker-compose build

# Start services
up:
	@echo "🚀 Starting PlayRight Backend services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "📊 PocketBase Admin: http://localhost:8090/_/"
	@echo "🔗 API Server: http://localhost:3001"
	@echo "🤖 AI Engine: http://localhost:8000"

# Start services with logs
up-logs:
	@echo "🚀 Starting PlayRight Backend services with logs..."
	docker-compose up

# Stop services
down:
	@echo "🛑 Stopping PlayRight Backend services..."
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# View specific service logs
logs-api:
	docker-compose logs -f api-server

logs-ai:
	docker-compose logs -f ai-engine

logs-pb:
	docker-compose logs -f pocketbase

# Clean up
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v
	docker system prune -f

# Deep clean (removes images too)
clean-all:
	@echo "🧹 Deep cleaning (removes all containers, volumes, and images)..."
	docker-compose down -v --rmi all
	docker system prune -af

# Development commands
dev-api:
	@echo "🔧 Starting API server in development mode..."
	cd api-server && python -m uvicorn app.main:app --reload --port 3001

dev-ai:
	@echo "🤖 Starting AI engine in development mode..."
	cd ai-engine && python -m uvicorn main:app --reload --port 8000

dev-worker:
	@echo "⚡ Starting Celery worker..."
	cd api-server && python -m celery worker -A app.worker.celery --loglevel=info

# Testing
test:
	@echo "🧪 Running tests..."
	cd api-server && python -m pytest tests/ -v
	cd ai-engine && python -m pytest tests/ -v

test-api:
	cd api-server && python -m pytest tests/ -v

test-ai:
	cd ai-engine && python -m pytest tests/ -v

# Code quality
lint:
	@echo "🔍 Running linting..."
	cd api-server && python -m flake8 app/
	cd ai-engine && python -m flake8 .

format:
	@echo "✨ Formatting code with Black..."
	cd api-server && python -m black app/
	cd ai-engine && python -m black .
	cd api-server && python -m isort app/
	cd ai-engine && python -m isort .

# Health checks
health:
	@echo "🏥 Checking service health..."
	curl -f http://localhost:3001/health || echo "❌ API Server unhealthy"
	curl -f http://localhost:8000/health || echo "❌ AI Engine unhealthy"
	curl -f http://localhost:8090/api/health || echo "❌ PocketBase unhealthy"

# Database operations
db-reset:
	@echo "🗄️  Resetting database..."
	docker-compose down
	docker volume rm playright-backend_pb_data 2>/dev/null || true
	docker-compose up -d pocketbase
	@echo "✅ Database reset complete"

db-backup:
	@echo "💾 Creating database backup..."
	docker-compose exec pocketbase cp -r /pb/pb_data /pb/backup-$(shell date +%Y%m%d-%H%M%S)
	@echo "✅ Database backup created"

# Installation helpers
install-deps-api:
	cd api-server && pip install -r requirements.txt

install-deps-ai:
	cd ai-engine && pip install -r requirements.txt

# Monitoring
monitor:
	@echo "📊 Service status:"
	docker-compose ps

# Quick start for new developers
quickstart: setup build up
	@echo "🎉 PlayRight Backend is ready!"
	@echo "📖 Visit http://localhost:8090/_ to set up PocketBase admin"
	@echo "🔗 API documentation: http://localhost:3001/docs"
	@echo "🤖 AI Engine docs: http://localhost:8000/docs"