# Sidetrack Task Runner

default: check

# Run all quality checks
check: format-check lint typecheck test smoke

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

# Run route smoke test exercising full planning sequence
smoke:
	pytest apps/web/tests/test_planner.py

