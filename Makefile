install:
	uv sync

debug-mode:
	uv run flask --app page_analyzer:app --debug run --port 8000

dev:
	uv run flask --debug --app page_analyzer:app run

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:8000 page_analyzer:app

render-start:
	gunicorn -w 5 -b 0.0.0.0:8000 page_analyzer:app

build:
	./build.sh

lint:
	uv run flake8 page_analyzer

test:
	uv run pytest

check:
	ruff check --fix --select I