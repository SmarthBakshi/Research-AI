import os
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{"host": os.getenv("OPENSEARCH_HOST", "localhost"), "port": int(os.getenv("OPENSEARCH_PORT", 9200))}],
    http_compress=True
)

index_name = os.getenv("OPENSEARCH_INDEX_NAME", "researchai_chunks")

mapping = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    },
    "mappings": {
        "properties": {
            "chunk_id": {"type": "keyword"},
            "chunk_text": {"type": "text"},  # For BM25 lexical search
            "embedding": {
                "type": "dense_vector",
                "dims": 768,
                "index": True,
                "similarity": "cosine"       # Good for L2-normalized vectors
            },
            "source_file": {"type": "keyword"},
            "chunk_index": {"type": "integer"}
        }
    }
}

if not client.indices.exists(index=index_name):
    client.indices.create(index=index_name, body=mapping)
    print(f"✅ Index '{index_name}' created.")
else:
    print(f"ℹ️ Index '{index_name}' already exists.")