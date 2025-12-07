#!/usr/bin/env python3
"""
Process PDFs from GCS and index them into Cloud SQL + OpenSearch
This runs outside of Airflow for quick GCP deployment
"""
import os
import sys
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add services to path
sys.path.insert(0, '/Users/smarthbakshi/Desktop/projects/Research-AI')

from google.cloud import storage
from services.processing.extractors.hybrid_extractor import HybridPdfExtractor
from services.processing.normalization.text_normaliser import TextNormalizer
from services.processing.chunking.chunker import Chunker
from services.processing.db_write.db_writer import write_chunks_to_db
from services.embedding.huggingface_embedder import HuggingFaceEmbedder
from services.search.opensearch_store import OpenSearchStore

# Configuration from environment variables
BUCKET_NAME = "researchai-pdfs-eu"
OPENSEARCH_HOST = os.getenv("GCP_OPENSEARCH_HOST")
OPENSEARCH_PORT = int(os.getenv("GCP_OPENSEARCH_PORT", "9200"))

# Set environment variables for db_writer
os.environ["POSTGRES_HOST"] = os.getenv("GCP_POSTGRES_HOST")
os.environ["POSTGRES_USER"] = os.getenv("GCP_POSTGRES_USER")
os.environ["POSTGRES_PASSWORD"] = os.getenv("GCP_POSTGRES_PASSWORD")
os.environ["APP_DB"] = os.getenv("GCP_POSTGRES_DB")
os.environ["POSTGRES_PORT"] = os.getenv("GCP_POSTGRES_PORT", "5432")

def download_pdf_from_gcs(bucket_name, blob_name):
    """Download PDF from GCS to temporary file"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Create temporary file
    suffix = os.path.splitext(blob_name)[1]
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_path = temp_file.name
    temp_file.close()

    print(f"📥 Downloading {blob_name} from GCS...")
    blob.download_to_filename(temp_path)
    print(f"✓ Downloaded to {temp_path}")

    return temp_path

def process_pdf(pdf_path, source_file):
    """Process a single PDF: extract, normalize, chunk, save to DB"""
    print(f"\n🔄 Processing {source_file}...")

    # Initialize components
    extractor = HybridPdfExtractor()
    normalizer = TextNormalizer(remove_latex=True)
    chunker = Chunker()

    # Extract text
    print("  📄 Extracting text...")
    result = extractor.extract(pdf_path)

    # Get text from result
    if hasattr(result, "full_text"):
        text = result.full_text
    elif hasattr(result, "text"):
        text = result.text
    else:
        text = str(result) if result else None

    if not text:
        raise ValueError(f"Could not extract text from {source_file}")

    print(f"  ✓ Extracted {len(text)} characters")

    # Normalize
    print("  🧹 Normalizing text...")
    normalized = normalizer.clean(text)

    # Chunk
    print("  ✂️  Chunking text...")
    chunks = chunker.chunk(normalized, source_file=source_file)
    print(f"  ✓ Created {len(chunks)} chunks")

    # Write to database
    print(f"  💾 Writing chunks to Cloud SQL...")
    write_chunks_to_db(chunks)
    print(f"  ✓ Saved {len(chunks)} chunks to database")

    return chunks

def index_chunks(source_file):
    """Index chunks from database into OpenSearch"""
    print(f"\n🔍 Indexing {source_file} into OpenSearch...")

    # Initialize services
    embedder = HuggingFaceEmbedder(model_name="intfloat/e5-base-v2")
    search_store = OpenSearchStore(
        host=OPENSEARCH_HOST,
        port=OPENSEARCH_PORT,
        index_name="chunks"
    )

    # Get chunks from database
    import psycopg2
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["APP_DB"],
        port=os.environ["POSTGRES_PORT"]
    )
    cur = conn.cursor()

    cur.execute(
        "SELECT id, source_file, chunk_index, chunk_text FROM chunks WHERE source_file = %s AND indexed_at IS NULL",
        (source_file,)
    )
    rows = cur.fetchall()

    if not rows:
        print(f"  ⚠️  No unindexed chunks found for {source_file}")
        return

    print(f"  📊 Found {len(rows)} chunks to index")

    # Embed and index
    print("  🧮 Generating embeddings...")
    texts = [row[3] for row in rows]
    embeddings = embedder.embed_batch(texts)

    print("  📤 Uploading to OpenSearch...")
    for i, row in enumerate(rows):
        chunk_id, source, chunk_idx, text = row
        search_store.insert_chunk(
            chunk_id=chunk_id,
            source_file=source,
            chunk_index=chunk_idx,
            chunk_text=text,
            embedding=embeddings[i]
        )

    # Update indexed_at timestamp
    from datetime import datetime
    cur.execute(
        "UPDATE chunks SET indexed_at = %s WHERE source_file = %s AND indexed_at IS NULL",
        (datetime.utcnow(), source_file)
    )
    conn.commit()
    conn.close()

    print(f"  ✓ Indexed {len(rows)} chunks")

def main():
    """Process all PDFs from GCS"""
    print("🚀 Starting PDF processing and indexing pipeline...")

    # List all PDFs in bucket
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blobs = list(bucket.list_blobs())
    pdf_blobs = [b for b in blobs if b.name.endswith('.pdf')]

    print(f"📚 Found {len(pdf_blobs)} PDFs in gs://{BUCKET_NAME}/")

    for blob in pdf_blobs:
        try:
            # Download PDF
            pdf_path = download_pdf_from_gcs(BUCKET_NAME, blob.name)

            # Process PDF
            chunks = process_pdf(pdf_path, blob.name)

            # Index chunks
            index_chunks(blob.name)

            # Clean up temp file
            os.unlink(pdf_path)

            print(f"✅ Completed {blob.name}\n")

        except Exception as e:
            print(f"❌ Error processing {blob.name}: {e}\n")
            import traceback
            traceback.print_exc()
            continue

    print("\n🎉 All done!")

if __name__ == "__main__":
    main()
