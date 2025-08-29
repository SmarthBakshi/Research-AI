import os
import psycopg2
import pytest
from services.processing.db_write.db_writer import write_chunks_to_db


@pytest.fixture(scope="module")
def setup_test_db():
    # Create a temporary test table
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=os.environ.get("DB_PORT", 5432)
        )
    with conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS pdf_chunks;")
    conn.close()
    yield
    # Clean up after tests
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=os.environ.get("DB_PORT", 5432)
        )
    with conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS pdf_chunks;")
    conn.close()


def test_write_chunks_to_db(setup_test_db):
    sample_chunks = [
    {"source_file": "test.pdf", "chunk_index": 0, "chunk_text": "Sample chunk text."},
    {"source_file": "test.pdf", "chunk_index": 1, "chunk_text": "Another chunk."},
    ]
    write_chunks_to_db(sample_chunks)


    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=os.environ.get("DB_PORT", 5432)
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM pdf_chunks;")
            count = cur.fetchone()[0]
            assert count == 2
    conn.close()