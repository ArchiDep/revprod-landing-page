# Checks the project: make
#
# Every target installs what it needs into the repository, ignored by Git:
# doctoc and Prettier into node_modules, pytest and Ruff into .venv. The versions
# of Node.js, Python and uv come from .tool-versions when asdf is installed.

# uv would otherwise prefer a Python it downloaded itself to the one in
# .tool-versions. Set UV_PYTHON to run the checks with another version, e.g.
# make UV_PYTHON=3.12.
export UV_PYTHON ?= python3

# Fails instead of updating uv.lock if it no longer matches pyproject.toml.
UV_RUN := uv run --locked

.PHONY: all check clean doctoc doctoc-check format format-check lint run test

all: check

## Run every check: table of contents, formatting, linting, tests.
check: doctoc-check format-check lint test

## Check that the README's table of contents is up to date.
doctoc-check: node_modules
	npm run doctoc

## Update the README's table of contents with doctoc.
doctoc: node_modules
	npm run doctoc:write

## Check that every file is formatted: Python with Ruff, the rest with Prettier.
format-check: node_modules
	npm run format
	$(UV_RUN) ruff format --check

## Format every file: Python with Ruff, the rest with Prettier.
format: node_modules
	npm run format:write
	$(UV_RUN) ruff format

## Check the Python code with Ruff's linter.
lint:
	$(UV_RUN) ruff check

## Run the automated tests.
test:
	$(UV_RUN) pytest

## Run the application, with the settings in .env if there is one.
run:
	$(UV_RUN) $(if $(wildcard .env),--env-file .env) python -m revprod_landing

clean:
	rm -rf .venv .pytest_cache .ruff_cache node_modules
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

node_modules: package.json package-lock.json
	npm ci
	@touch node_modules
