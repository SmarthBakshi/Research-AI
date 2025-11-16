#!/usr/bin/env python3
"""
Query and display text chunks from the PostgreSQL database.

Usage:
    python scripts/query_chunks.py --list                    # List all files
    python scripts/query_chunks.py --count                   # Count chunks
    python scripts/query_chunks.py --file FILENAME           # View chunks from specific file
    python scripts/query_chunks.py --search "keyword"        # Search chunks by keyword
    python scripts/query_chunks.py --chunk-id ID             # View specific chunk
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.processing.db_write.db_writer import Chunk, get_engine


def list_files(session):
    """List all unique source files in the database."""
    print("\n📚 Files in Database:")
    print("=" * 80)

    result = session.execute(text("""
        SELECT
            source_file,
            COUNT(*) as chunk_count,
            MIN(created_at) as first_chunk,
            MAX(created_at) as last_chunk
        FROM chunks
        GROUP BY source_file
        ORDER BY first_chunk DESC
    """))

    for row in result:
        print(f"\n📄 {row.source_file}")
        print(f"   Chunks: {row.chunk_count}")
        print(f"   Created: {row.first_chunk}")


def count_chunks(session):
    """Display chunk statistics."""
    print("\n📊 Database Statistics:")
    print("=" * 80)

    total = session.execute(text("SELECT COUNT(*) FROM chunks")).scalar()
    files = session.execute(text("SELECT COUNT(DISTINCT source_file) FROM chunks")).scalar()
    indexed = session.execute(text("SELECT COUNT(*) FROM chunks WHERE indexed_at IS NOT NULL")).scalar()

    print(f"Total chunks: {total}")
    print(f"Unique files: {files}")
    print(f"Indexed chunks: {indexed}")
    print(f"Pending indexing: {total - indexed}")


def view_file_chunks(session, filename):
    """View all chunks from a specific file."""
    print(f"\n📖 Chunks from: {filename}")
    print("=" * 80)

    chunks = session.query(Chunk).filter(
        Chunk.source_file.like(f"%{filename}%")
    ).order_by(Chunk.chunk_index).all()

    if not chunks:
        print(f"❌ No chunks found for file containing '{filename}'")
        return

    print(f"Found {len(chunks)} chunks\n")

    for chunk in chunks:
        print(f"\n--- Chunk {chunk.chunk_index} (ID: {chunk.id}) ---")
        print(f"Created: {chunk.created_at}")
        print(f"Indexed: {chunk.indexed_at or 'Not indexed'}")
        print(f"\nText (first 500 chars):")
        print(chunk.chunk_text[:500])
        if len(chunk.chunk_text) > 500:
            print(f"... ({len(chunk.chunk_text) - 500} more characters)")


def search_chunks(session, keyword):
    """Search chunks by keyword."""
    print(f"\n🔍 Searching for: '{keyword}'")
    print("=" * 80)

    chunks = session.query(Chunk).filter(
        Chunk.chunk_text.ilike(f"%{keyword}%")
    ).all()

    if not chunks:
        print(f"❌ No chunks found containing '{keyword}'")
        return

    print(f"Found {len(chunks)} matching chunks\n")

    for chunk in chunks[:10]:  # Limit to first 10 results
        print(f"\n--- Chunk {chunk.chunk_index} from {os.path.basename(chunk.source_file)} (ID: {chunk.id}) ---")

        # Find and highlight the keyword in context
        text_lower = chunk.chunk_text.lower()
        keyword_lower = keyword.lower()
        pos = text_lower.find(keyword_lower)

        if pos != -1:
            start = max(0, pos - 100)
            end = min(len(chunk.chunk_text), pos + len(keyword) + 100)
            context = chunk.chunk_text[start:end]
            print(f"Context: ...{context}...")

    if len(chunks) > 10:
        print(f"\n... and {len(chunks) - 10} more results")


def view_chunk_by_id(session, chunk_id):
    """View a specific chunk by ID."""
    print(f"\n📝 Chunk ID: {chunk_id}")
    print("=" * 80)

    chunk = session.query(Chunk).filter(Chunk.id == chunk_id).first()

    if not chunk:
        print(f"❌ No chunk found with ID {chunk_id}")
        return

    print(f"Source: {chunk.source_file}")
    print(f"Chunk Index: {chunk.chunk_index}")
    print(f"Created: {chunk.created_at}")
    print(f"Indexed: {chunk.indexed_at or 'Not indexed'}")
    print(f"Text Length: {len(chunk.chunk_text)} characters")
    print(f"\nFull Text:")
    print("-" * 80)
    print(chunk.chunk_text)


def main():
    parser = argparse.ArgumentParser(description="Query text chunks from PostgreSQL database")
    parser.add_argument("--list", action="store_true", help="List all files")
    parser.add_argument("--count", action="store_true", help="Show chunk statistics")
    parser.add_argument("--file", type=str, help="View chunks from specific file (partial name match)")
    parser.add_argument("--search", type=str, help="Search chunks by keyword")
    parser.add_argument("--chunk-id", type=int, help="View specific chunk by ID")

    args = parser.parse_args()

    # Create database session
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if args.list:
            list_files(session)
        elif args.count:
            count_chunks(session)
        elif args.file:
            view_file_chunks(session, args.file)
        elif args.search:
            search_chunks(session, args.search)
        elif args.chunk_id:
            view_chunk_by_id(session, args.chunk_id)
        else:
            # Default: show count
            count_chunks(session)
            print("\nUse --help to see all available options")

    finally:
        session.close()


if __name__ == "__main__":
    main()
