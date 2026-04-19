.PHONY: help setup install dev dev-backend dev-frontend build test clean lint format

help:
	@echo "Personal Budget App - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup       - Setup the project (install dependencies)"
	@echo "  make install     - Install all dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev         - Run both backend and frontend"
	@echo "  make dev-backend - Run only backend on port 8000"
	@echo "  make dev-frontend- Run only frontend on port 5173"
	@echo ""
	@echo "Building & Deployment:"
	@echo "  make build       - Build frontend for production"
	@echo "  make build-backend - Build Python package"
	@echo ""
	@echo "Maintenance:"
	@echo "  make test        - Run tests"
	@echo "  make test-backend - Run only backend tests"
	@echo "  make test-frontend - Run only frontend tests"
	@echo "  make lint        - Lint code"
	@echo "  make format      - Format code"
	@echo "  make clean       - Clean build artifacts"
	@echo ""

setup: install
	@echo "✅ Setup complete!"
	@echo ""
	@echo "To run the app:"
	@echo "  make dev          (run both frontend and backend)"
	@echo "  make dev-backend  (run backend only)"
	@echo "  make dev-frontend (run frontend only)"

install:
	@echo "📦 Installing dependencies..."
	npm install
	uv sync
	@echo "✅ Dependencies installed"

dev: dev-backend dev-frontend

dev-backend:
	@echo "🚀 Starting backend on http://localhost:8000"
	uv run -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "🚀 Starting frontend on http://localhost:5173"
	npm run dev

build: build-frontend
	@echo "✅ Build complete! Output in dist/"

build-frontend:
	@echo "🔨 Building frontend..."
	npm run build
	@echo "✅ Frontend built"

build-backend:
	@echo "🔨 Building Python package..."
	uv build
	@echo "✅ Python package built"

test: test-backend test-frontend
test-backend:
	@echo "🧪 Running backend tests..."
	uv run pytest tests/

test-frontend:
	@echo "🧪 Running frontend tests..."
	npm test
lint:
	@echo "🔍 Linting code..."
	npm run lint
	uv run ruff check src/backend/

format:
	@echo "✨ Formatting code..."
	npm run lint -- --fix
	uv run black src/backend/
	uv run ruff check src/backend/ --fix

clean:
	@echo "🧹 Cleaning up..."
	rm -rf dist/
	rm -rf .venv/
	rm -rf node_modules/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete"

.DEFAULT_GOAL := help
