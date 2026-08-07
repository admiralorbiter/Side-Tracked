# Sidetrack Task Runner

default: check

# Run all quality checks
check: format-check lint typecheck test db-migrate media-verify data-verify smoke

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

# Run database migrations
db-migrate:
	python -m packages.ovon_core.cli.migrate_db

# Download Creative Commons media assets
media-download:
	python -m packages.ovon_core.cli.download_media

# Verify media assets and manifest
media-verify:
	python -m packages.ovon_core.cli.verify_media

# Verify regional pilot package and datasets
data-verify:
	python -m packages.ovon_core.cli.verify_pilot

# Run route smoke test exercising full planning sequence
smoke:
	pytest apps/web/tests/test_planner.py
