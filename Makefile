# Makefile
lint: #project linter check
	poetry run flake8 genpage_analyzer

install: # deps install
	poetry install

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build: # Build project
	rm -f ./dist/*
	poetry build

publish: # Publish package
	poetry publish --dry-run

package-install: # Install package
	python3 -m pip install --user dist/*.whl

test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml