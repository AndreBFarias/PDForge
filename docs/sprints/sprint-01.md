# Sprint 01 — Infraestrutura Git + DevOps + CI/CD

**Diretório:** `/home/andrefarias/Desenvolvimento/PDForge`
**Conta git:** `AndreBFarias` / `andre.dsbf@gmail.com`

Execute todas as tasks direto, sem criar task list, sem confirmar etapas, sem parar a não ser em erro real.

---

## Estado inicial

- `.gitignore` já existe
- `git init` já foi executado
- `git config --local user.name "AndreBFarias"` e `user.email "andre.dsbf@gmail.com"` já estão setados
- Nenhum commit ainda

---

## Task 1 — LICENSE (GPLv3)

Criar `LICENSE` com o texto completo padrão da GNU General Public License v3.0.
Use o texto canônico de https://www.gnu.org/licenses/gpl-3.0.txt

---

## Task 2 — pyproject.toml

Criar `pyproject.toml`:

```toml
[project]
name = "pdfforge"
version = "1.0.0"
description = "Editor de PDF com GUI e ML/AI para Linux"
requires-python = ">=3.10"
license = {text = "GPL-3.0"}
authors = [{name = "AndreBFarias"}]

[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "W", "I", "UP"]
exclude = ["venv/", ".venv/", "sprints/", "QR-Code-Void-Generator/"]

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_imports = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

---

## Task 3 — requirements-dev.txt

Criar `requirements-dev.txt`:

```
ruff>=0.3.0
mypy>=1.9.0
types-Pillow
pytest>=8.0.0
pytest-qt>=4.3.0
pytest-cov>=4.1.0
pre-commit>=3.7.0
build>=1.1.0
```

---

## Task 4 — Makefile

Criar `Makefile` (use tabulações reais, não espaços):

```makefile
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
```

---

## Task 5 — .pre-commit-config.yaml

Criar `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [types-Pillow]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=500]
```

---

## Task 6 — GitHub Actions

Criar `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11"]

    steps:
      - uses: actions/checkout@v4

      - name: Configurar Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Instalar dependencias do sistema
        run: |
          sudo apt-get update
          sudo apt-get install -y libgl1-mesa-glx libxcb-xinerama0 xvfb

      - name: Instalar dependencias Python
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint (ruff)
        run: ruff check . && ruff format --check .

      - name: Type check (mypy)
        run: mypy . --ignore-missing-imports

      - name: Testes
        run: QT_QPA_PLATFORM=offscreen pytest tests/ -v --tb=short
```

Criar `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - "v*.*.*"

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Gerar changelog
        id: changelog
        run: |
          PREV_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")
          if [ -z "$PREV_TAG" ]; then
            CHANGELOG=$(git log --pretty=format:"- %s" HEAD)
          else
            CHANGELOG=$(git log --pretty=format:"- %s" ${PREV_TAG}..HEAD)
          fi
          echo "changelog<<EOF" >> $GITHUB_OUTPUT
          echo "$CHANGELOG" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Criar GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          body: |
            ## Alteracoes

            ${{ steps.changelog.outputs.changelog }}
          draft: false
          prerelease: false
```

---

## Commit final do sprint

```bash
git add .gitignore LICENSE pyproject.toml requirements-dev.txt Makefile .pre-commit-config.yaml .github/
git commit -m "chore: infraestrutura inicial — DevOps, CI/CD e configuração de projeto"
```

**Próximo sprint:** `sprint-02.md`
