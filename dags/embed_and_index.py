from airflow.decorators import dag, task
from datetime import datetime, timedelta
from embedder.huggingface_embedder import HuggingFaceEmbedder
from store.opensearch_store import OpenSearchStore
import psycopg2
import os

# Add a column 'indexed_at' to chunks table that holds timestamp of when chunk was indexed and prevents re-indexing

@dag(schedule=None, start_date=datetime(2023, 1, 1), catchup=False, tags=["embedding"])
def embed_and_index():

    @task
    def load_unindexed_chunks():
        # Connect to DB and get chunks
        conn = psycopg2.connect(
            dbname=os.getenv("APP_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host="postgres",  # docker hostname
            port=os.getenv("POSTGRES_PORT", 5432)
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT chunk_id, chunk_text, source_file, chunk_index
            FROM chunks
            WHERE indexed_at IS NULL
            ORDER BY chunk_index
            LIMIT 100;
        """)
        rows = cur.fetchall()
        conn.close()
        return [
            {
                "chunk_id": row[0],
                "chunk_text": row[1],
                "source_file": row[2],
                "chunk_index": row[3],
            }
            for row in rows
        ]

    @task
    def embed_chunks(chunks):
        embedder = HuggingFaceEmbedder("intfloat/e5-base-v2")
        texts = [c["chunk_text"] for c in chunks]
        embeddings = embedder.embed(texts)
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i]
        return chunks

    @task
    def upsert_to_opensearch(chunks):
        store = OpenSearchStore()
        store.upsert_chunks(chunks)
        return [c["chunk_id"] for c in chunks]

    @task
    def mark_indexed(chunk_ids):
        conn = psycopg2.connect(
            dbname=os.getenv("APP_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host="postgres",
            port=os.getenv("POSTGRES_PORT", 5432)
        )
        cur = conn.cursor()
        cur.execute(
            "UPDATE chunks SET indexed_at = NOW() WHERE chunk_id = ANY(%s);",
            (chunk_ids,)
        )
        conn.commit()
        conn.close()

    # DAG sequence
    chunks = load_unindexed_chunks()
    embedded = embed_chunks(chunks)
    upserted_ids = upsert_to_opensearch(embedded)
    mark_indexed(upserted_ids)

dag = embed_and_index()