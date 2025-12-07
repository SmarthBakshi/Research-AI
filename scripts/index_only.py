#!/usr/bin/env python3
"""
Index existing chunks from Cloud SQL into OpenSearch
"""
import os
import sys

# Add services to path
sys.path.insert(0, '/Users/smarthbakshi/Desktop/projects/Research-AI')

from services.embedding.huggingface_embedder import HuggingFaceEmbedder
from services.search.opensearch_store import OpenSearchStore
import psycopg2
from datetime import datetime

# Configuration
OPENSEARCH_HOST = "34.179.167.137"
OPENSEARCH_PORT = 9200
os.environ["POSTGRES_HOST"] = "35.246.234.51"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "ResearchAI2024Secure!"
os.environ["APP_DB"] = "researchai"
os.environ["POSTGRES_PORT"] = "5432"

def main():
    print("🔍 Indexing chunks into OpenSearch...")

    # Initialize services
    print("🤖 Loading embedding model...")
    embedder = HuggingFaceEmbedder(model_name="intfloat/e5-base-v2")

    print("🔌 Connecting to OpenSearch...")
    search_store = OpenSearchStore(
        host=OPENSEARCH_HOST,
        port=OPENSEARCH_PORT,
        index_name="chunks"
    )

    # Create index if it doesn't exist
    search_store.create_index()

    # Get all unindexed chunks from database
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["APP_DB"],
        port=os.environ["POSTGRES_PORT"]
    )
    cur = conn.cursor()

    print("📊 Fetching unindexed chunks from database...")
    cur.execute(
        "SELECT id, source_file, chunk_index, chunk_text FROM chunks WHERE indexed_at IS NULL"
    )
    rows = cur.fetchall()

    if not rows:
        print("✅ No unindexed chunks found!")
        return

    print(f"Found {len(rows)} chunks to index")

    # Embed and index
    print("🧮 Generating embeddings (this takes 2-3 minutes)...")
    texts = [row[3] for row in rows]
    embeddings = embedder.embed_batch(texts)

    print("📤 Uploading to OpenSearch...")
    docs = []
    for i, row in enumerate(rows):
        chunk_id, source, chunk_idx, text = row
        docs.append({
            "chunk_text": text,
            "source_file": source,
            "chunk_index": chunk_idx,
            "embedding": embeddings[i].tolist() if hasattr(embeddings[i], 'tolist') else embeddings[i]
        })

    search_store.upsert_documents(docs)

    # Update indexed_at timestamp
    print("💾 Updating database timestamps...")
    cur.execute(
        "UPDATE chunks SET indexed_at = %s WHERE indexed_at IS NULL",
        (datetime.utcnow(),)
    )
    conn.commit()
    conn.close()

    print(f"✅ Successfully indexed {len(rows)} chunks!")

if __name__ == "__main__":
    main()
