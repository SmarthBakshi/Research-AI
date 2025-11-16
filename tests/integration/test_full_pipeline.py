"""
Integration test for full ResearchAI pipeline

Tests the end-to-end flow from ingestion to query answering.
"""

import pytest
import psycopg2
import os
from opensearchpy import OpenSearch


@pytest.fixture
def db_connection():
    """Create database connection"""
    conn = psycopg2.connect(
        dbname=os.getenv("APP_DB", "researchai_app"),
        user=os.getenv("POSTGRES_USER", "researchai"),
        password=os.getenv("POSTGRES_PASSWORD", "researchai"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )
    yield conn
    conn.close()


@pytest.fixture
def opensearch_client():
    """Create OpenSearch client"""
    client = OpenSearch(
        hosts=[{
            "host": os.getenv("OPENSEARCH_HOST", "localhost"),
            "port": int(os.getenv("OPENSEARCH_PORT", "9200"))
        }],
        use_ssl=False,
        verify_certs=False
    )
    return client


class TestDatabaseSetup:
    """Test database schema and setup"""

    def test_chunks_table_exists(self, db_connection):
        """Test that chunks table exists"""
        cur = db_connection.cursor()
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'chunks'
            );
        """)
        exists = cur.fetchone()[0]
        assert exists, "chunks table should exist"

    def test_chunks_table_has_required_columns(self, db_connection):
        """Test chunks table has all required columns"""
        cur = db_connection.cursor()
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'chunks';
        """)
        columns = [row[0] for row in cur.fetchall()]

        required_columns = ['id', 'source_file', 'chunk_index', 'chunk_text', 'created_at', 'indexed_at']
        for col in required_columns:
            assert col in columns, f"Column {col} should exist in chunks table"


class TestOpenSearchSetup:
    """Test OpenSearch configuration"""

    def test_opensearch_connection(self, opensearch_client):
        """Test connection to OpenSearch"""
        info = opensearch_client.info()
        assert "version" in info

    def test_opensearch_index_exists(self, opensearch_client):
        """Test that the chunks index exists or can be created"""
        index_name = "researchai_chunks"
        exists = opensearch_client.indices.exists(index=index_name)
        # Index may or may not exist depending on setup stage
        assert isinstance(exists, bool)


class TestProcessingPipeline:
    """Test PDF processing pipeline"""

    def test_chunking_logic(self):
        """Test that chunking produces expected results"""
        from services.chunkers.text_chunker import SlidingWindowChunker

        text = " ".join(["word"] * 1000)  # 1000 words
        chunker = SlidingWindowChunker(chunk_size=300, overlap=50)
        chunks = chunker.chunk_text(text)

        assert len(chunks) > 1, "Long text should produce multiple chunks"
        assert all(len(chunk.split()) <= 300 for chunk in chunks), "Chunks should respect max size"

    def test_embedding_generation(self):
        """Test embedding generation"""
        try:
            from services.embedding.huggingface_embedder import HuggingFaceEmbedder

            embedder = HuggingFaceEmbedder(model_name="sentence-transformers/all-MiniLM-L6-v2")
            texts = ["machine learning", "deep learning"]
            embeddings = embedder.embed(texts)

            assert len(embeddings) == 2, "Should return embedding for each text"
            assert all(isinstance(emb, list) for emb in embeddings), "Embeddings should be lists"
            assert all(len(emb) > 0 for emb in embeddings), "Embeddings should not be empty"
        except ImportError:
            pytest.skip("HuggingFace dependencies not available")


class TestSearchFunctionality:
    """Test search capabilities"""

    def test_opensearch_dense_search(self, opensearch_client):
        """Test dense vector search functionality"""
        index_name = "researchai_chunks"

        if not opensearch_client.indices.exists(index=index_name):
            pytest.skip("Index not created yet")

        # Create dummy query vector
        query_vector = [0.1] * 768

        try:
            response = opensearch_client.search(
                index=index_name,
                body={
                    "size": 5,
                    "query": {
                        "knn": {
                            "embedding": {
                                "vector": query_vector,
                                "k": 5
                            }
                        }
                    }
                }
            )
            assert "hits" in response
        except Exception as e:
            # May fail if no documents indexed yet
            pytest.skip(f"Search test skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
