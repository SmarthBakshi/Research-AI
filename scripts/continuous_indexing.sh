#!/bin/bash
# Continuous indexing script - keeps triggering DAG runs until all chunks are indexed

echo "🚀 Starting continuous indexing..."
echo "This script will keep triggering DAG runs until all 1,992 chunks are indexed."
echo ""

while true; do
  # Check current indexed count
  INDEXED=$(docker exec research-ai-postgres-1 psql -U researchai -d researchai_app -t -c "SELECT COUNT(*) FROM chunks WHERE indexed_at IS NOT NULL;" | tr -d ' ')
  UNINDEXED=$(docker exec research-ai-postgres-1 psql -U researchai -d researchai_app -t -c "SELECT COUNT(*) FROM chunks WHERE indexed_at IS NULL;" | tr -d ' ')

  echo "📊 Progress: $INDEXED/1992 chunks indexed ($UNINDEXED remaining)"

  # Check if done
  if [ "$UNINDEXED" -eq 0 ]; then
    echo "✅ All chunks indexed! Exiting."
    exit 0
  fi

  # Check running/queued DAG runs
  RUNNING=$(docker exec researchai-airflow airflow dags list-runs -d embed_and_index --state running -o table 2>&1 | grep -c "manual__" || echo "0")
  QUEUED=$(docker exec researchai-airflow airflow dags list-runs -d embed_and_index --state queued -o table 2>&1 | grep -c "manual__" || echo "0")

  TOTAL_ACTIVE=$((RUNNING + QUEUED))
  echo "🔄 Active DAG runs: $RUNNING running, $QUEUED queued (total: $TOTAL_ACTIVE)"

  # Only trigger if less than 5 active runs
  if [ "$TOTAL_ACTIVE" -lt 5 ]; then
    RUNS_TO_TRIGGER=$((5 - TOTAL_ACTIVE))
    echo "▶️  Triggering $RUNS_TO_TRIGGER new DAG run(s)..."

    for ((i=1; i<=RUNS_TO_TRIGGER; i++)); do
      docker exec researchai-airflow airflow dags trigger embed_and_index > /dev/null 2>&1
      echo "  ✓ Triggered run $i/$RUNS_TO_TRIGGER"
    done
  else
    echo "⏸️  Enough runs active, waiting..."
  fi

  echo "⏳ Waiting 2 minutes before next check..."
  echo ""
  sleep 120
done
