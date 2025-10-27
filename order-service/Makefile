DC := docker compose
CLI := $(DC) run --rm order-service

.PHONY: test lint

test:
	$(CLI) pytest -vv

lint:
	$(CLI) ruff check --fix . && ruff format .

create-migration:
	$(CLI) bash -c "alembic revision --autogenerate"

setup-database:
	$(CLI) bash -c "alembic upgrade head"

start: setup-database
	$(DC) up -d

stop:
	$(DC) down