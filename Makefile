# Makefile

PORT ?= 8000

start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

install:
	poetry install

build:
	poetry build

publish:
	poetry publish --dry-run -u=USER -p=pwd_publish

package-install:
	python3 -m pip install --force-reinstall --user dist/*.whl

test:
	poetry run pytest

test-coverage-xml:
	poetry run pytest --cov=page_analyzer --cov-report xml

lint:
	poetry run flake8 page_analyzer

dev:
	poetry run flask --app page_analyzer:app run
