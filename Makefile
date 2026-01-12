PYTHON ?= python
RUFF ?= ruff
MYPY ?= mypy
PYTEST ?= pytest

.PHONY: format lint test ci run_fast run_full

format:
	$(RUFF) format .

lint:
	$(RUFF) check .
	$(MYPY) src/pipeline

test:
	$(PYTEST) -q

ci: format lint test

run_fast:
	$(PYTHON) run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db --no-embeddings --no-retries

run_full:
	$(PYTHON) run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db
