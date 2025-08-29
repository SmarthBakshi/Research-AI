#!/bin/bash

# Set environment variables
export AIRFLOW_ADMIN_USER=admin
export AIRFLOW_ADMIN_PWD=admin
export AIRFLOW_ADMIN_EMAIL=admin@example.com

echo "🚀 Initializing Airflow database..."
docker compose run --rm --no-deps --entrypoint bash airflow -lc "airflow db init"

echo "👤 Creating admin user..."
docker compose run --rm --no-deps --entrypoint bash airflow -lc \
  "airflow users create \
    --username \"$AIRFLOW_ADMIN_USER\" \
    --password \"$AIRFLOW_ADMIN_PWD\" \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email \"$AIRFLOW_ADMIN_EMAIL\" || true"

echo "✅ Done! Now starting the Airflow container..."
docker compose up -d airflow

echo "🚀 Starting Airflow scheduler..."
docker compose run --rm --no-deps --entrypoint bash airflow -lc "airflow scheduler"

