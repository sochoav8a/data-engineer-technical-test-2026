# DevOps y CI/CD

## CI en GitHub Actions
La pipeline de CI corre:
- `ruff format --check`
- `ruff check`
- `mypy src/pipeline`
- `pytest -q`

Se ejecuta en Python 3.11 y 3.12 con cache de pip.

## Pre-commit
Instalacion:
```bash
pip install pre-commit
pre-commit install
```

Hooks:
- ruff (lint + format)
- mypy
- detect-secrets

## Makefile
```bash
make format
make lint
make test
make ci
``