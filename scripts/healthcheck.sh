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

# Postgres (inside container: pg_isready + simple query)
echo -n "[postgres] readiness ... "
docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-postgres}" >/dev/null && echo "OK" || { echo "FAIL"; exit 1; }
echo -n "[postgres] can SELECT 1 on ${APP_DB:-researchai_app} ... "
docker compose exec -T postgres psql -U "${POSTGRES_USER:-postgres}" -d "${APP_DB:-researchai_app}" -tAc "SELECT 1" >/dev/null && echo "OK" || { echo "FAIL"; exit 1; }

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
    curl -fsS
