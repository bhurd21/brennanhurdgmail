.PHONY: build-base build up down test debug push-db migrate-db deploy deploy-db

# Build the base Lahman DB image from v1 (contains the CSVs). Required once.
build-base:
	docker build -t lahman-db lahman-db

# Build v2 images (run build-base first if lahman-db image doesn't exist).
build:
	docker compose build

# Start the full stack.
up:
	docker compose up -d

down:
	docker compose down

# Run the full test suite (stack must be up).
test:
	cd lahman-api && uv run pytest -v

# Run only the combination tests (primary regression check).
test-combinations:
	cd lahman-api && uv run pytest tests/test_combinations.py -v

# Interactive debug: ask for a question and show the full pipeline.
debug:
	@read -p "Question: " q && cd lahman-api && uv run python scripts/debug_question.py "$$q"

# Deploy the API to production via Kamal.
deploy:
	kamal deploy

# Build the DB image for linux/amd64 (prod server arch) and push to Docker Hub.
# Run this whenever lahman-db/init/ or lahman-db/lahman_*_csv/ changes.
push-db:
	docker buildx build --platform linux/amd64 -t hurdbr/lahman-db:latest ./lahman-db --push

# Wipe the prod DB volume and restart from the latest image.
# Run push-db first. This will take ~2 min while postgres loads the CSVs.
migrate-db:
	kamal server exec "docker rm -f lahman-db-prod && docker volume rm lahman_pgdata_prod && docker pull hurdbr/lahman-db:latest && docker run -d --name lahman-db-prod --restart unless-stopped -e POSTGRES_PASSWORD=lahman -e POSTGRES_DB=lahman -v lahman_pgdata_prod:/var/lib/postgresql/data -p 172.17.0.1:5432:5432 hurdbr/lahman-db:latest"

# Full production deploy when both DB and API changed (e.g. new schema + new condition).
# DB migration runs first since the API depends on the new schema.
deploy-db:
	$(MAKE) push-db
	$(MAKE) migrate-db
	$(MAKE) deploy
