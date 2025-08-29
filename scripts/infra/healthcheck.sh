#!/usr/bin/env bash
set -Eeuo pipefail

# Load local env if present (so ports/users match your .env)
if [ -f ".env" ]; then
  set -a
  . ./.env
  set +a
fi

echo "== ResearchAI health check =="

# Helper to show a green check or fail fast
check_http () {
  local name="$1"; local url="$2"
  echo -n "[$name] $url ... "
  curl -fsS -o /dev/null "$url" && echo "OK" || { echo "FAIL"; exit 1; }
}

# Discover the actual container user
PG_USER_IN_CONTAINER="$(docker compose exec -T postgres printenv POSTGRES_USER || true)"
PG_USER="${PG_USER_IN_CONTAINER:-researchai}"

echo -n "[postgres] readiness ... "
docker compose exec -T postgres bash -lc 'pg_isready -U "$POSTGRES_USER"' >/dev/null && echo "OK" || { echo "FAIL"; exit 1; }

APP_DB_NAME="${APP_DB:-researchai_app}"
echo -n "[postgres] SELECT 1 on ${APP_DB_NAME} ... "
if docker compose exec -T postgres bash -lc 'psql -U "$POSTGRES_USER" -d "'"$APP_DB_NAME"'" -tAc "SELECT 1"' >/dev/null 2>&1; then
  echo "OK"
else
  echo "FAIL"; exit 1
fi

# OpenSearch cluster health
check_http "opensearch" "http://localhost:${OPENSEARCH_PORT:-9200}/_cluster/health"

# MinIO ready
check_http "minio" "http://localhost:${MINIO_API_PORT:-9000}/minio/health/ready"

# Airflow web health
check_http "airflow" "http://localhost:8080/health"

# API health
check_http "api" "http://localhost:${API_PORT:-8000}/healthz"

# UI reachable (returns HTML)
check_http "ui" "http://localhost:${UI_PORT:-7860}/"

# Ollama (optional) — only if service exists in compose
if docker compose ps --services | grep -qx "ollama"; then
  echo -n "[ollama] /api/tags ... "
  if docker compose ps | grep -q "researchai-ollama"; then
    curl -fsS -o /dev/null "http://localhost:11434/api/tags" && echo "OK" || { echo "FAIL"; exit 1; }
  else
    echo "SKIP"
  fi
fi