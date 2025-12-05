#!/usr/bin/env python3
"""
Fast indexing script for interview demo - processes chunks directly without Airflow overhead
"""
import sys
sys.path.insert(0, '/Users/smarthbakshi/Desktop/projects/Research-AI')

import psycopg2
from services.embedding.huggingface_embedder import HuggingFaceEmbedder
from services.search.opensearch_store import OpenSearchStore
from datetime import datetime

def index_remaining_chunks():
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="researchai_app",
        user="researchai",
        password="researchai123"
    )
    
    embedder = HuggingFaceEmbedder("intfloat/e5-base-v2")
    opensearch_store = OpenSearchStore()
    
    cursor = conn.cursor()
    
    # Process in batches of 100
    batch_size = 100
    processed = 0
    
    while True:
        # Get unindexed chunks
        cursor.execute("""
            SELECT chunk_id, paper_id, chunk_text, chunk_number, page_number
            FROM chunks 
            WHERE indexed_at IS NULL 
            LIMIT %s
        """, (batch_size,))
        
        chunks = cursor.fetchall()
        if not chunks:
            print(f"\n✅ All chunks indexed! Total processed: {processed}")
            break
        
        print(f"\n📦 Processing batch of {len(chunks)} chunks...")
        
        # Prepare chunk documents
        chunk_docs = []
        chunk_ids = []
        for row in chunks:
            chunk_id, paper_id, chunk_text, chunk_number, page_number = row
            chunk_docs.append({
                "chunk_id": chunk_id,
                "paper_id": paper_id,
                "chunk_text": chunk_text,
                "chunk_number": chunk_number,
                "page_number": page_number
            })
            chunk_ids.append(chunk_id)
        
        # Generate embeddings
        print(f"  🔢 Generating embeddings...")
        texts = [c["chunk_text"] for c in chunk_docs]
        embeddings = embedder.embed_batch(texts)
        
        for i, chunk_doc in enumerate(chunk_docs):
            chunk_doc["embedding"] = embeddings[i]
        
        # Upsert to OpenSearch
        print(f"  📤 Uploading to OpenSearch...")
        opensearch_store.upsert_documents(chunk_docs)
        
        # Mark as indexed in PostgreSQL
        print(f"  ✅ Marking as indexed in PostgreSQL...")
        cursor.execute("""
            UPDATE chunks 
            SET indexed_at = %s 
            WHERE chunk_id = ANY(%s)
        """, (datetime.utcnow(), chunk_ids))
        conn.commit()
        
        processed += len(chunks)
        print(f"  ✓ Batch complete! Total: {processed}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("🚀 Fast Indexing Script for Interview Demo")
    print("=" * 50)
    index_remaining_chunks()
