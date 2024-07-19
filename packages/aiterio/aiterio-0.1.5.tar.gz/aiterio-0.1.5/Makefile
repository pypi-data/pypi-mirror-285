# Makefile
PYTHON ?= ./.venv/bin/python
APP ?= aiterio
BENCHS ?= benchmarks
TESTS ?= tests

all: setup lint/fix lint mypy test

setup:
	rye sync

setup/pip:
	python -m venv .venv
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -Ur requirements-dev.lock

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} \;
	find . -type d -name .cache -prune -exec rm -rf {} \;
	find . -type d -name .mypy_cache -prune -exec rm -rf {} \;
	find . -type d -name .pytest_cache -prune -exec rm -rf {} \;
	find . -type d -name .ruff_cache -prune -exec rm -rf {} \;
	find . -type d -name .venv -prune -exec rm -rf {} \;
	find . -type d -name dist -prune -exec rm -rf {} \;
	find . -type d -name venv -prune -exec rm -rf {} \;

lint:
	$(PYTHON) -m ruff check ./$(APP) $(TESTS) $(BENCHS)
	$(PYTHON) -m ruff format --check ./$(APP) $(TESTS) $(BENCHS)
	$(PYTHON) -m vulture --min-confidence=100 ./$(APP) $(TESTS) $(BENCHS)

lint/fix:
	$(PYTHON) -m ruff check --fix-only ./$(APP) $(TESTS) $(BENCHS)
	$(PYTHON) -m ruff format ./$(APP) $(TESTS) $(BENCHS)

mypy:
	$(PYTHON) -m mypy --cache-dir .cache/mypy_cache ./$(APP) $(TESTS) $(BENCHS)

run:
	$(PYTHON) -m $(APP)

test:
	$(PYTHON) -m pytest --rootdir=. -o cache_dir=.cache/pytest_cache $(TESTS) -s -x -v $(options)

bench:
	$(PYTHON) -m $(BENCHS).bench_component

.PHONY: $(shell grep -E '^([a-zA-Z_-]|\/)+:' $(MAKEFILE_LIST) | awk -F':' '{print $$2}')
