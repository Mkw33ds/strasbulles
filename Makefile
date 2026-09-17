.PHONY: up down logs migrate superuser seed groups test lint check css collectstatic backup restore
COMPOSE = docker compose

up:
	$(COMPOSE) up --build
down:
	$(COMPOSE) down
logs:
	$(COMPOSE) logs -f web
migrate:
	$(COMPOSE) exec web python manage.py migrate
superuser:
	$(COMPOSE) exec web python manage.py create_initial_admin
seed:
	$(COMPOSE) exec web python manage.py seed_content
groups:
	$(COMPOSE) exec web python manage.py setup_staff_groups
test:
	$(COMPOSE) exec -e DJANGO_SETTINGS_MODULE=config.settings.test web pytest
lint:
	$(COMPOSE) exec -e RUFF_CACHE_DIR=/tmp/ruff-cache web ruff check .
	$(COMPOSE) exec -e RUFF_CACHE_DIR=/tmp/ruff-cache web ruff format --check .
check:
	$(COMPOSE) exec web python manage.py check
css:
	$(COMPOSE) exec assets npm run css:build
collectstatic:
	$(COMPOSE) exec web python manage.py collectstatic --noinput
backup:
	mkdir -p backups
	$(COMPOSE) exec -T db pg_dump -U "$${POSTGRES_USER:-strasbulles}" "$${POSTGRES_DB:-strasbulles}" | gzip > backups/database.sql.gz
	$(COMPOSE) exec -T web tar -czf - /app/media > backups/media.tar.gz
restore:
	@test -f backups/database.sql.gz
	gunzip -c backups/database.sql.gz | $(COMPOSE) exec -T db psql -U "$${POSTGRES_USER:-strasbulles}" "$${POSTGRES_DB:-strasbulles}"
	@test -f backups/media.tar.gz
	$(COMPOSE) exec -T web tar -xzf - -C / < backups/media.tar.gz
