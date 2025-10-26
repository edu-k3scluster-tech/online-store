.PHONY: test lint

test:
	docker compose run --rm order-service pytest -vv

lint:
	docker compose run --rm order-service ruff check --fix . && ruff format .
