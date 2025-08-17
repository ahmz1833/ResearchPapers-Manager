.PHONY: build recreate up down logs fmt scale test seed-data clean venv

build:
	docker build -t research-papers-manager:latest .

recreate:
	docker compose down
	docker compose up -d --build --force-recreate

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=100 api

fmt:
	black app
	isort app

scale:
	docker compose up -d --scale api=1

venv:
	@if [ ! -d .venv ]; then \
		echo "Creating virtualenv (.venv)"; \
		python3 -m venv .venv; \
	else \
		echo "Reusing existing virtualenv (.venv)"; \
	fi
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/pip install -e .

test:
	make venv
	. .venv/bin/activate
	python scripts/test_complete.py

seed-data:
	docker compose exec api python scripts/seed_data.py

clean:
	docker compose down -v
	docker system prune -f
