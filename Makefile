# Makefile for PPG Analysis Tool
# Provides convenient commands for development, testing, and building

.PHONY: help install install-dev test test-coverage lint format clean build docs run

# Default target
help:
	@echo "PPG Analysis Tool - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test         Run all tests"
	@echo "  test-coverage Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         Run linting checks (flake8, black, isort)"
	@echo "  flake8       Run flake8 style checking only"
	@echo "  format       Format code (black, isort)"
	@echo ""
	@echo "Building:"
	@echo "  build        Build package distribution"
	@echo "  clean        Clean build artifacts"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         Build documentation"
	@echo ""
	@echo "Development:"
	@echo "  run          Run the application locally"

# Installation
install:
	python -m pip install -r requirements.txt

install-dev:
	python -m pip install -r requirements.txt
	python -m pip install -r requirements-dev.txt

# Testing
test:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

# Code Quality
lint:
	flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503,W291,W293,E501,F401,F841,E722,W605,E731,F403,F405,E402,C901
	black --check src/ tests/
	isort --check-only src/ tests/

flake8:
	flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503,W291,W293,E501,F401,F841,E722,W605,E731,F403,F405,E402,C901

format:
	black src/ tests/ src/* src/callbacks/* src/components/* src/config/* src/utils/*
	isort src/ tests/ src/* src/callbacks/* src/components/* src/config/* src/utils/*

# Building
build:
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Documentation
docs:
ifeq ($(OS),Windows_NT)
	python build_docs.py
else
	cd docs && make html
endif

# Development
run:
	python main.py

# Security checks
security:
	bandit -r src/
	safety check

# Type checking
type-check:
	mypy src/

# Full quality check
quality: lint type-check security test-coverage
	@echo "✅ All quality checks passed!"

# CI/CD helper
ci: install-dev quality build
	@echo "✅ CI/CD pipeline completed successfully!"
