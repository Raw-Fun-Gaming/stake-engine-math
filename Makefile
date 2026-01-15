PYTHON := python3
VENV_DIR := env
VENV_PY := $(VENV_DIR)/bin/python

ifeq ($(OS),Windows_NT)
	VENV_PY := $(VENV_DIR)\Scripts\python.exe
	ACTIVATE := $(VENV_DIR)\Scripts\activate.bat
else
	ACTIVATE := source $(VENV_DIR)/bin/activate
endif

help:
	@echo "Available commands:"
	@echo ""
	@echo "Setup & Environment:"
	@echo "  make setup                      - Set up virtual environment and install dependencies"
	@echo "  make clean                      - Clean up build artifacts"
	@echo ""
	@echo "Running Games:"
	@echo "  make run GAME=<game>            - Run game simulation"
	@echo "  make validate GAME=<game>       - Validate game configuration"
	@echo "  make list-games                 - List all available games"
	@echo ""
	@echo "Testing:"
	@echo "  make test                       - Run main project tests"
	@echo "  make unit-test GAME=<game>      - Run game-specific unit tests"
	@echo "  make coverage                   - Run tests with coverage report"
	@echo ""
	@echo "Development:"
	@echo "  make profile GAME=<game>        - Profile game performance"
	@echo "  make benchmark GAME=<game>      - Run compression benchmark"
	@echo "  make format                     - Format code with black and isort"
	@echo "  make lint                       - Run linting checks"
	@echo ""
	@echo "Examples:"
	@echo "  make run GAME=tower_treasures"
	@echo "  make validate GAME=tower_treasures"
	@echo "  make unit-test GAME=tower_treasures"

makeVirtual:
	$(PYTHON) -m venv $(VENV_DIR)

pipInstall: makeVirtual
	$(VENV_PY) -m pip install --upgrade pip

pipPackages: pipInstall
	$(VENV_PY) -m pip install -r requirements.txt

packInstall: pipPackages
	$(VENV_PY) -m pip install -e .

setup: packInstall
	@echo "Virtual environment ready."
	@echo "To activate it, run:"
	@echo "$(ACTIVATE)"


run:
ifndef GAME
	$(error GAME is not set. Usage: make run GAME=<game_name>)
endif
	$(VENV_PY) games/$(GAME)/run.py
	@echo "Checking compression setting..."
	@if grep -q "compression = False" games/$(GAME)/run.py; then \
		echo "Compression is disabled, formatting books files..."; \
		$(VENV_PY) scripts/format_books_json.py games/$(GAME) || echo "Warning: Failed to format books files"; \
	else \
		echo "Compression is enabled, skipping formatting."; \
	fi

test:
	cd $(CURDIR)
	pytest tests/

# Game-specific unit tests - usage: make unit-test GAME=tower_treasures
# Runs all unit tests for the specified game
unit-test:
ifndef GAME
	$(error GAME is not set. Usage: make unit-test GAME=<game_name>)
endif
	cd games/$(GAME) && ../../$(VENV_PY) tests/run_tests.py

clean:
	rm -rf env __pycache__ *.pyc
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Validate game configuration
validate:
ifndef GAME
	$(error GAME is not set. Usage: make validate GAME=<game_name>)
endif
	$(VENV_PY) scripts/validate_config.py $(GAME)

# List all available games
list-games:
	$(VENV_PY) scripts/validate_config.py --list

# Run tests with coverage report
coverage:
	$(VENV_PY) -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

# Profile game performance
profile:
ifndef GAME
	$(error GAME is not set. Usage: make profile GAME=<game_name>)
endif
	$(VENV_PY) scripts/profile_performance.py --game $(GAME) --mode cpu

# Run compression benchmark
benchmark:
ifndef GAME
	$(error GAME is not set. Usage: make benchmark GAME=<game_name>)
endif
	$(VENV_PY) scripts/benchmark_compression.py --game $(GAME)

# Format code with black and isort
format:
	$(VENV_PY) -m black src/ games/ tests/ scripts/ --line-length 100
	$(VENV_PY) -m isort src/ games/ tests/ scripts/

# Run linting checks
lint:
	$(VENV_PY) -m flake8 src/ --max-line-length 100 --ignore=E501,W503
	$(VENV_PY) -m mypy src/ --ignore-missing-imports

# Check code without making changes
check:
	$(VENV_PY) -m black src/ games/ tests/ scripts/ --check --line-length 100
	$(VENV_PY) -m isort src/ games/ tests/ scripts/ --check-only

.PHONY: help setup run test unit-test clean validate list-games coverage profile benchmark format lint check
