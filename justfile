# Sidetrack Task Runner

default: check

# Run all quality checks
check: lint typecheck test

# Start local development server
dev:
	python app.py

# Run pytest suite
test:
	pytest

# Run ruff linter
lint:
	ruff check .

# Run ruff formatter check
format-check:
	ruff format --check .

# Format code with ruff
format:
	ruff format .

# Run type checker
typecheck:
	mypy apps/web packages/ovon_core

# Run route smoke test
smoke:
	python -m pytest apps/web/tests/test_planner.py -k test_home_page
