# ----------- 🐳 Docker targets -----------

up:
	@echo "🚀 Starting all services..."
	DOCKER_BUILDKIT=1 docker compose up -d

down:
	@echo "🛑 Stopping and removing containers and volumes..."
	docker compose down -v

logs:
	@echo "📜 Showing live logs..."
	docker compose logs -f

ps:
	@echo "📦 Listing container statuses..."
	docker compose ps

# ----------- Airflow DB Init -----------

init-airflow:
	@echo "🐍 Setting up Airflow DB and user..."
	@export AIRFLOW_ADMIN_USER=admin && \
	export AIRFLOW_ADMIN_PWD=admin && \
	export AIRFLOW_ADMIN_EMAIL=admin@example.com && \
	docker compose run --rm --no-deps --entrypoint bash airflow -lc "airflow db init" && \
	docker compose run --rm --no-deps --entrypoint bash airflow -lc "airflow users create \
		--username $$AIRFLOW_ADMIN_USER \
		--password $$AIRFLOW_ADMIN_PWD \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email $$AIRFLOW_ADMIN_EMAIL || true"

start-airflow:
	@echo "🚀 Starting Airflow container and scheduler..."
	docker compose up -d airflow
	docker compose run --rm --no-deps --entrypoint bash airflow -lc "airflow scheduler"

airflow-reset: down init-airflow start-airflow
	@echo "✅ Airflow has been reset and started."

# ----------- 🛠️ Rebuild targets -----------

rebuild-airflow:
	@echo "🔁 Rebuilding Airflow + Init..."
	DOCKER_BUILDKIT=1 docker compose build airflow airflow-init
	docker compose up -d airflow airflow-init

rebuild-api:
	@echo "🔁 Rebuilding API..."
	DOCKER_BUILDKIT=1 docker compose build api
	docker compose up -d api

rebuild-ui:
	@echo "🔁 Rebuilding UI..."
	DOCKER_BUILDKIT=1 docker compose build ui
	docker compose up -d ui

rebuild-all:
	@echo "💥 Rebuilding ALL with no cache..."
	docker compose down -v
	DOCKER_BUILDKIT=1 docker compose build --no-cache
	docker compose up -d

# ----------- 🧪 Python Dev (test, lint, format) -----------

test:
	@echo "✅ Running pytest..."
	pytest -v tests/

lint:
	@echo "🕵️‍♂️ Linting with ruff..."
	ruff check .

format:
	@echo "🧼 Formatting with black..."
	black .

check:
	@echo "🔍 Running lint & test..."
	make lint && make test

# ----------- 🔄 Restart specific containers -----------

restart-airflow:
	docker compose restart airflow

restart-api:
	docker compose restart api

restart-ui:
	docker compose restart ui

# ----------- 🧹 Cleanup -----------

clean:
	@echo "🧽 Cleaning Docker system..."
	docker system prune -af --volumes

purge:
	@echo "🔥 Full cleanup and build reset..."
	docker compose down -v
	docker system prune -af --volumes
