#!/bin/bash
# Re-process all PDFs with fixed chunking code

echo "🔧 Starting complete data reprocessing..."
echo ""

# Step 1: Clear all existing chunks from PostgreSQL
echo "1️⃣  Clearing all chunks from PostgreSQL..."
docker exec research-ai-postgres-1 psql -U researchai -d researchai_app -c "DELETE FROM chunks;"
echo "✅ PostgreSQL chunks cleared"
echo ""

# Step 2: Delete and recreate OpenSearch index
echo "2️⃣  Recreating OpenSearch index..."
./scripts/fix_opensearch_index.sh
echo "✅ OpenSearch index recreated"
echo ""

# Step 3: Trigger PDF processing DAG
echo "3️⃣  Triggering PDF processing DAG..."
echo "⚠️  This will process all PDFs from MinIO"
echo ""
read -p "Press Enter to trigger the process_pdfs DAG..."

docker exec researchai-airflow airflow dags trigger process_pdfs

echo ""
echo "✅ PDF processing DAG triggered!"
echo ""
echo "📊 Monitor progress:"
echo "  - Airflow UI: http://localhost:8080"
echo "  - Check DAG status and logs"
echo ""
echo "⏳ After process_pdfs completes, run indexing:"
echo "  ./scripts/trigger_indexing.sh"
echo ""
