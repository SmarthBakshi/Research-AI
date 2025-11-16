#!/bin/bash
# Trigger embed_and_index DAG multiple times to index all chunks

echo "🚀 Starting batch indexing of all chunks..."
echo "This will trigger the embed_and_index DAG 18 times (100 chunks per run)"
echo ""

# Number of times to run (1763 chunks / 100 per run = ~18 runs)
RUNS=18

for i in $(seq 1 $RUNS); do
    echo "[$i/$RUNS] Triggering embed_and_index DAG..."
    docker exec researchai-airflow airflow dags trigger embed_and_index

    # Wait a bit between triggers to avoid overwhelming the system
    if [ $i -lt $RUNS ]; then
        echo "   Waiting 10 seconds before next trigger..."
        sleep 10
    fi
done

echo ""
echo "✅ All $RUNS DAG runs triggered!"
echo ""
echo "Monitor progress:"
echo "  - Airflow UI: http://localhost:8080"
echo "  - Check indexed count: curl 'http://localhost:9200/chunks/_count'"
echo ""
echo "Wait for all runs to complete, then test your search:"
echo "  curl -X POST http://localhost:8000/search -H 'Content-Type: application/json' -d '{\"query\": \"machine learning\", \"k\": 3}'"
