.PHONY: help install test lint format clean dev-django

help:
	@grep -E '^[a-zA-Z_-]+:.*#' Makefile | sort | while read -r l; do printf "\033[36m%-20s\033[0m %s\n" "$${l%%:*}" "$${l#*}"; done

install:  # Install package in editable mode
	pip install -e ".[dev,ui]"

test:  # Run all tests
	python -m pytest tests/ -v

test-quick:  # Run tests quickly (no output files)
	python -m pytest tests/ -v --tb=short

lint:  # Lint with ruff
	ruff check src/brac7/ tests/

format:  # Format with ruff
	ruff format src/brac7/ tests/

typecheck:  # Type-check with mypy
	mypy src/brac7/ || true

clean:  # Remove cache and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/

dev-django:  # Run Django dev server
	cd brac7_site && python manage.py migrate && python manage.py runserver

dev-django-migrate:  # Run Django migrations
	cd brac7_site && python manage.py migrate

dev-django-admin:  # Create Django admin user
	cd brac7_site && python manage.py createsuperuser --username admin --email admin@example.com || true

bracket-demo:  # Generate a demo bracket
	brac7 -m "Alice" "Bob" "Carol" "Dave" "Eve" \
		--title "Demo Bracket" --format single_elimination --all \
		--slug demo-bracket

bracket-round-robin:  # Generate a round-robin demo
	brac7 -m "Alice" "Bob" "Carol" "Dave" \
		--title "Round Robin Demo" --format round_robin --all \
		--slug round-robin-demo
