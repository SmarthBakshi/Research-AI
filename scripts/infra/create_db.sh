# load your env so the names are available
set -a; source .env; set +a

# create APP_DB if it doesn't exist
docker compose exec -T postgres bash -lc \
"psql -U \"$POSTGRES_USER\" -d postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='${APP_DB}'\" | grep -q 1 || \
 psql -U \"$POSTGRES_USER\" -d postgres -c \"CREATE DATABASE ${APP_DB}\""

# create AIRFLOW_DB if it doesn't exist
docker compose exec -T postgres bash -lc \
"psql -U \"$POSTGRES_USER\" -d postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='${AIRFLOW_DB}'\" | grep -q 1 || \
 psql -U \"$POSTGRES_USER\" -d postgres -c \"CREATE DATABASE ${AIRFLOW_DB}\""
