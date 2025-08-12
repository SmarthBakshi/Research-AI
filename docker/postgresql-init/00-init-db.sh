#!/usr/bin/env bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
  CREATE DATABASE ${APP_DB};
  CREATE DATABASE ${AIRFLOW_DB};
EOSQL
