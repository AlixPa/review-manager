COMPOSE_PROD   = docker compose --env-file .env -f docker-compose.yaml
COMPOSE_LOCAL   = docker compose --env-file .env

prod-run-%:
	$(COMPOSE_PROD) up -d $*

prod-rebuild-%:
	$(COMPOSE_PROD) build --no-cache $*
	$(MAKE) prod-run-$*

prod-logs-%:
	$(COMPOSE_PROD) logs -f $*

local-run-%:
	$(COMPOSE_LOCAL) up -d $*

local-rebuild-%:
	$(COMPOSE_LOCAL) build --no-cache $*
	$(MAKE) local-run-$*

local-logs-%:
	$(COMPOSE_LOCAL) logs -f $*

stop:
	$(COMPOSE_PROD) stop

prod-app: prod-run-mysql run-migrations prod-run-backend prod-run-nginx-frontend
local-app: local-run-mysql run-migrations local-run-backend local-run-nginx-frontend

dev-frontend:
	$(COMPOSE_LOCAL) watch frontend

dev-backend:
	$(COMPOSE_LOCAL) watch backend

clean:
	docker system prune -f
	docker volume prune -f

new-migration:
	./shell/new_migration.sh "$(NAME)"

run-migrations:
	$(COMPOSE_PROD) build --no-cache migrations
	$(COMPOSE_PROD) up migrations


.PHONY: stop clean local-app prod-app dev-frontend dev-backend \
	new-migration run-migrations