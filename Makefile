.PHONY: install test run lint

install:
	pip install -r requirements-dev.txt

test:
	pytest

run:
	python web/app.py

lint:
	ruff check .
