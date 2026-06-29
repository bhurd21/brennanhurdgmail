.PHONY: build-base build up down test debug

# Build the base Lahman DB image from v1 (contains the CSVs). Required once.
build-base:
	docker build -t lahman-db ../lahman-api/lahman-db

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
