.PHONY: install dev test lint clean build

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

dev: install
	$(PIP) install -r requirements-dev.txt
	$(VENV)/bin/pre-commit install

test:
	QT_QPA_PLATFORM=offscreen $(VENV)/bin/pytest tests/ -v --cov=. --cov-report=term-missing

lint:
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy . --ignore-missing-imports

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -type f -name "*.pyc" -delete 2>/dev/null; true
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	rm -rf dist build *.egg-info

build:
	$(VENV)/bin/python -m build
