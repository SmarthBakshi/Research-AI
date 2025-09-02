import os
import psycopg2
from dotenv import load_dotenv

from services.embedding.huggingface_embedder import HuggingFaceEmbedder

load_dotenv()

# Connect to Postgres
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", "5435"),
    dbname=os.getenv("POSTGRES_DB", "researchai"),
    user=os.getenv("POSTGRES_USER", "airflow"),
    password=os.getenv("POSTGRES_PASSWORD", "airflow"),
)

cursor = conn.cursor()

# Step 1: Fetch chunk_texts
cursor.execute("SELECT chunk_index, chunk_text FROM chunks ORDER BY chunk_index LIMIT 10;")
rows = cursor.fetchall()
texts = [row[1] for row in rows]

# Step 2: Load embedder
embedder = HuggingFaceEmbedder(
    model_name=os.getenv("EMBEDDING_MODEL_NAME"),
    device=os.getenv("EMBEDDING_DEVICE", "cpu")
)

# Step 3: Generate embeddings
embeddings = embedder.embed_batch(texts)

# Step 4: Print result
for i, (chunk_id, _) in enumerate(rows):
    print(f"[{chunk_id}] Embedding vector (first 5 dims): {embeddings[i][:5]}")

cursor.close()
conn.close()
print("✅ Embeddings generated successfully.")