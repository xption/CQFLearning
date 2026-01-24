# Makefile for CQF Learning

# Variables
PYTHON := python3
APP_DIR := app

.PHONY: help install install-dev test test-cov lint format clean run setup check all

help:  ## Show help information
	@echo "CQF Learning - Quantitative Finance Learning Project"
	@echo "Available commands:"
	@echo "  install      - Install project dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  lint         - Code quality check"
	@echo "  format       - Code formatting"
	@echo "  clean        - Clean temporary files"
	@echo "  run          - Run CLI"
	@echo "  setup        - Setup development environment"
	@echo "  check        - Run lint and tests"
	@echo "  all          - Install dev dependencies and run checks"

install:  ## Install project dependencies
	$(PYTHON) -m pip install -e .

install-dev:  ## Install development dependencies
	$(PYTHON) -m pip install -e ".[dev]"

test: install-dev  ## Run tests
	$(PYTHON) -m pytest

test-cov: install-dev  ## Run tests with coverage report
	$(PYTHON) -m pytest --cov=$(APP_DIR) --cov-report=html --cov-report=term

lint: install-dev  ## Code quality check
	$(PYTHON) -m flake8 $(APP_DIR)/ --max-line-length=999
	$(PYTHON) -m mypy $(APP_DIR)/

format: install-dev  ## Code formatting
	$(PYTHON) -m autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r $(APP_DIR)/
	$(PYTHON) -m black $(APP_DIR)/
	$(PYTHON) -m isort $(APP_DIR)/

clean:  ## Clean temporary files
	@echo "Cleaning temporary files..."
	@$(PYTHON) -c "import shutil, pathlib; \
        dirs = ['build', 'dist', 'htmlcov', '.pytest_cache'] + list(pathlib.Path('.').rglob('__pycache__')) + list(pathlib.Path('.').rglob('*.egg-info')); \
        files = ['.coverage'] + list(pathlib.Path('.').rglob('*.pyc')); \
        [shutil.rmtree(d, ignore_errors=True) for d in dirs if pathlib.Path(d).exists()]; \
        [pathlib.Path(f).unlink(missing_ok=True) for f in files if pathlib.Path(f).exists()]"

run:  ## Run CLI
	$(PYTHON) -m $(APP_DIR).run

setup: install-dev  ## Setup development environment
	@echo "Development environment setup complete"

check: lint test  ## Run lint and tests
	@echo "All checks passed"

all: install-dev check  ## Install dev dependencies and run checks
	@echo "Build complete"