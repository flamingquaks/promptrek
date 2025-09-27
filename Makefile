# Makefile for PrompTrek - uv/uvx compatible development workflows

.PHONY: help install sync test test-fast lint format typecheck build clean dev run
.DEFAULT_GOAL := help

# Colors for output
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)PrompTrek Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Note: All commands use uv for dependency management$(NC)"

install: ## Install the package and dev dependencies with uv
	@echo "$(BLUE)Installing package and dependencies with uv...$(NC)"
	uv sync --group dev

sync: ## Sync dependencies with uv (equivalent to install)
	@echo "$(BLUE)Syncing dependencies with uv...$(NC)"
	uv sync --group dev

test: ## Run all tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	uv run python -m pytest

test-fast: ## Run tests without coverage for faster feedback
	@echo "$(BLUE)Running tests without coverage...$(NC)"
	uv run python -m pytest --no-cov

test-unit: ## Run only unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	uv run python -m pytest tests/unit/

test-integration: ## Run only integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	uv run python -m pytest tests/integration/

lint: ## Run all linting checks
	@echo "$(BLUE)Running linting checks...$(NC)"
	uv run black --check src/ tests/
	uv run isort --check-only src/ tests/
	uv run flake8 src/ tests/

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run black src/ tests/
	uv run isort src/ tests/

typecheck: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(NC)"
	uv run mypy src/

build: ## Build the package
	@echo "$(BLUE)Building package...$(NC)"
	@if command -v uv >/dev/null 2>&1; then \
		echo "$(YELLOW)Using uv build...$(NC)"; \
		uv build; \
	else \
		echo "$(YELLOW)uv not found, using python -m build in a temporary virtual environment...$(NC)"; \
		python -m venv .build-venv; \
		. .build-venv/bin/activate; \
		pip install --upgrade pip >/dev/null 2>&1; \
		pip install build wheel >/dev/null 2>&1; \
		python -m build --wheel --no-isolation; \
		deactivate; \
		rm -rf .build-venv; \
	fi

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf dist/ build/ *.egg-info/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

dev: sync ## Set up development environment (alias for sync)
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo "To activate the environment manually, run: $(YELLOW)source .venv/bin/activate$(NC)"
	@echo "Installing pre-commit hooks..."
	uv run pre-commit install || echo "$(YELLOW)Warning: pre-commit not available, install with: uv add --group dev pre-commit$(NC)"

pre-commit-install: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	uv run pre-commit install

pre-commit-run: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks on all files...$(NC)"
	uv run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hook versions
	@echo "$(BLUE)Updating pre-commit hooks...$(NC)"
	uv run pre-commit autoupdate

run: ## Run promptrek CLI (with uv)
	@echo "$(BLUE)Running promptrek CLI...$(NC)"
	uv run promptrek

# Convenience targets for common uv workflows
uv-shell: ## Start a shell in the uv environment
	@echo "$(BLUE)Starting shell in uv environment...$(NC)"
	uv run bash

uv-python: ## Run Python in the uv environment
	@echo "$(BLUE)Starting Python in uv environment...$(NC)"
	uv run python

# CI/CD friendly targets
ci-test: ## Run tests in CI mode (with coverage but brief output)
	@echo "$(BLUE)Running CI tests...$(NC)"
	uv run python -m pytest --cov=src/promptrek --cov-report=term --cov-report=xml -v

ci-lint: ## Run linting in CI mode
	@echo "$(BLUE)Running CI linting...$(NC)"
	uv run black --check src/ tests/
	uv run isort --check-only src/ tests/
	uv run flake8 src/ tests/
	uv run mypy src/

all: clean install lint typecheck test build ## Run full development workflow
	@echo "$(GREEN)All checks passed!$(NC)"
