#!/usr/bin/env python3
"""
Process local PDFs and index them into Cloud SQL + OpenSearch
"""
import os
import sys
import glob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add services to path
sys.path.insert(0, '/Users/smarthbakshi/Desktop/projects/Research-AI')

from services.processing.extractors.hybrid_extractor import HybridPdfExtractor
from services.processing.normalization.text_normaliser import TextNormalizer
from services.processing.chunking.chunker import Chunker
from services.processing.db_write.db_writer import write_chunks_to_db
from services.embedding.huggingface_embedder import HuggingFaceEmbedder
from services.search.opensearch_store import OpenSearchStore

# Configuration from environment variables
PDF_DIR = "/Users/smarthbakshi/Desktop/projects/Research-AI/data/arxiv"
OPENSEARCH_HOST = os.getenv("GCP_OPENSEARCH_HOST")
OPENSEARCH_PORT = int(os.getenv("GCP_OPENSEARCH_PORT", "9200"))

# Set environment variables for db_writer
os.environ["POSTGRES_HOST"] = os.getenv("GCP_POSTGRES_HOST")
os.environ["POSTGRES_USER"] = os.getenv("GCP_POSTGRES_USER")
os.environ["POSTGRES_PASSWORD"] = os.getenv("GCP_POSTGRES_PASSWORD")
os.environ["APP_DB"] = os.getenv("GCP_POSTGRES_DB")
os.environ["POSTGRES_PORT"] = os.getenv("GCP_POSTGRES_PORT", "5432")

def process_pdf(pdf_path):
    """Process a single PDF: extract, normalize, chunk, save to DB"""
    source_file = os.path.basename(pdf_path)
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

    return chunks, source_file

def index_chunks(source_file):
    """Index chunks from database into OpenSearch"""
    print(f"\n🔍 Indexing {source_file} into OpenSearch...")

    # Initialize services
    print("  🤖 Loading embedding model...")
    embedder = HuggingFaceEmbedder(model_name="intfloat/e5-base-v2")

    print("  🔌 Connecting to OpenSearch...")
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
    from datetime import datetime
    cur.execute(
        "UPDATE chunks SET indexed_at = %s WHERE source_file = %s AND indexed_at IS NULL",
        (datetime.utcnow(), source_file)
    )
    conn.commit()
    conn.close()

    print(f"  ✓ Indexed {len(rows)} chunks")

def main():
    """Process all PDFs from local directory"""
    print("🚀 Starting PDF processing and indexing pipeline...")

    # Find all PDFs
    pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    print(f"📚 Found {len(pdf_files)} PDFs in {PDF_DIR}")

    for pdf_path in pdf_files:
        try:
            # Process PDF
            chunks, source_file = process_pdf(pdf_path)

            # Index chunks
            index_chunks(source_file)

            print(f"✅ Completed {source_file}\n")

        except Exception as e:
            print(f"❌ Error processing {os.path.basename(pdf_path)}: {e}\n")
            import traceback
            traceback.print_exc()
            continue

    print("\n🎉 All done!")

if __name__ == "__main__":
    main()
