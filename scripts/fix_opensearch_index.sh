#!/bin/bash
# Fix OpenSearch index mapping for kNN vector search

echo "🔧 Fixing OpenSearch chunks index for vector search..."

# Delete old index
echo "1. Deleting old index..."
curl -X DELETE 'http://localhost:9200/chunks'

echo ""
echo "2. Creating new index with kNN mapping..."

# Create index with proper kNN configuration
curl -X PUT 'http://localhost:9200/chunks' -H 'Content-Type: application/json' -d '{
  "settings": {
    "index": {
      "knn": true
    }
  },
  "mappings": {
    "properties": {
      "embedding": {
        "type": "knn_vector",
        "dimension": 768,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "nmslib"
        }
      },
      "chunk_text": {"type": "text"},
      "chunk_index": {"type": "integer"},
      "chunk_id": {"type": "integer"},
      "source_file": {"type": "keyword"}
    }
  }
}'

echo ""
echo "3. Resetting indexed_at timestamps in PostgreSQL..."
docker exec research-ai-postgres-1 psql -U researchai -d researchai_app -c "UPDATE chunks SET indexed_at = NULL;"

echo ""
echo "✅ Done! Now re-run the embed_and_index DAG in Airflow to reindex all chunks."
echo "   Go to: http://localhost:8080"
