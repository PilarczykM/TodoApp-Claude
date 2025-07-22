.PHONY: help install test lint format all

help:
	@echo "Commands:"
	@echo "  install    : Install dependencies"
	@echo "  test       : Run tests"
	@echo "  cov        : Run coverage"
	@echo "  lint       : Run linter"
	@echo "  typecheck  : Run typecheck"
	@echo "  format     : Run formatter"
	@echo "  all        : Run lint, format, and test"

install:
	uv sync

test:
	uv run pytest

cov:
	uv run pytest --cov=src tests/ --cov-fail-under=90

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

format:
	uv run ruff format .

all: format lint test