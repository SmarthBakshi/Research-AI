#!/usr/bin/env python3
"""Index all remaining chunks - run inside API container"""
import sys
import os

# Add project root to path
sys.path.insert(0, '/opt/researchai')

import psycopg2
from services.embedding.huggingface_embedder import HuggingFaceEmbedder
from services.search.opensearch_store import OpenSearchStore
from datetime import datetime

def main():
    print("=" * 60)
    print("🚀 ResearchAI - Fast Indexing Script")
    print("=" * 60)

    # Connect to database
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'postgres'),
        database='researchai_app',
        user='researchai',
        password='researchai123'
    )
    print("✓ Connected to PostgreSQL")

    # Initialize services
    print("📦 Loading embedding model (this may take a minute)...")
    embedder = HuggingFaceEmbedder("intfloat/e5-base-v2")
    print("✓ Embedding model loaded")

    opensearch_store = OpenSearchStore()
    print("✓ Connected to OpenSearch")

    cursor = conn.cursor()

    # Check total remaining
    cursor.execute("SELECT COUNT(*) FROM chunks WHERE indexed_at IS NULL")
    total_remaining = cursor.fetchone()[0]
    print(f"\n📊 Total chunks to index: {total_remaining}")

    if total_remaining == 0:
        print("✅ All chunks already indexed!")
        return

    # Process in batches
    batch_size = 100
    total_processed = 0

    while True:
        # Fetch unindexed chunks
        cursor.execute("""
            SELECT id, chunk_text, source_file, chunk_index
            FROM chunks
            WHERE indexed_at IS NULL
            LIMIT %s
        """, (batch_size,))

        rows = cursor.fetchall()
        if not rows:
            break

        print(f"\n{'='*60}")
        print(f"📦 Batch {(total_processed // batch_size) + 1}: Processing {len(rows)} chunks")
        print(f"{'='*60}")

        # Prepare documents
        chunk_docs = []
        chunk_ids = []
        for row in rows:
            chunk_id, chunk_text, source_file, chunk_index = row
            chunk_docs.append({
                "chunk_id": chunk_id,
                "chunk_text": chunk_text,
                "source_file": source_file,
                "chunk_index": chunk_index
            })
            chunk_ids.append(chunk_id)

        # Generate embeddings
        print(f"  🔢 Generating {len(chunk_docs)} embeddings...")
        texts = [doc["chunk_text"] for doc in chunk_docs]
        try:
            embeddings = embedder.embed_batch(texts)
            print(f"  ✓ Embeddings generated")
        except Exception as e:
            print(f"  ❌ Error generating embeddings: {e}")
            continue

        # Add embeddings to documents
        for i, chunk_doc in enumerate(chunk_docs):
            chunk_doc["embedding"] = embeddings[i]

        # Upsert to OpenSearch
        print(f"  📤 Uploading to OpenSearch...")
        try:
            opensearch_store.upsert_documents(chunk_docs)
            print(f"  ✓ Uploaded to OpenSearch")
        except Exception as e:
            print(f"  ❌ Error uploading to OpenSearch: {e}")
            continue

        # Mark as indexed in PostgreSQL
        print(f"  💾 Marking as indexed in PostgreSQL...")
        try:
            cursor.execute("""
                UPDATE chunks
                SET indexed_at = %s
                WHERE id = ANY(%s)
            """, (datetime.utcnow(), chunk_ids))
            conn.commit()
            print(f"  ✓ Marked as indexed")
        except Exception as e:
            print(f"  ❌ Error updating PostgreSQL: {e}")
            conn.rollback()
            continue

        total_processed += len(rows)
        progress = (total_processed / total_remaining) * 100
        print(f"\n✓ Batch complete! Progress: {total_processed}/{total_remaining} ({progress:.1f}%)")

    cursor.close()
    conn.close()

    print("\n" + "=" * 60)
    print(f"✅ INDEXING COMPLETE! Total processed: {total_processed}")
    print("=" * 60)

if __name__ == "__main__":
    main()
