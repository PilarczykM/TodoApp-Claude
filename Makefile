.PHONY: help install test lint format all

help:
	@echo "Commands:"
	@echo "  install    : Install dependencies"
	@echo "  test       : Run tests"
	@echo "  lint       : Run linter"
	@echo "  typecheck  : Run typecheck"
	@echo "  format     : Run formatter"
	@echo "  all        : Run lint, format, and test"

install:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

format:
	uv run ruff check . --fix

all: format lint test