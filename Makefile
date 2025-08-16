.PHONY: build recreate up down logs fmt scale

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
